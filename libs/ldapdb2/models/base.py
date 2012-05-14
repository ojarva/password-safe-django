# -*- coding: utf-8 -*-
# 
# django-ldapdb
# Copyright (c) 2009-2010, Bolloré telecom
# All rights reserved.
# 
# See AUTHORS file for a full list of contributors.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
#     1. Redistributions of source code must retain the above copyright notice, 
#        this list of conditions and the following disclaimer.
#     
#     2. Redistributions in binary form must reproduce the above copyright 
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
# 
#     3. Neither the name of Bolloré telecom nor the names of its contributors
#        may be used to endorse or promote products derived from this software
#        without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import ldap
import logging

import django.db.models
from django.db.models import signals

import ldapdb
from ldapdb.models.query import QuerySet

class ModelBase(django.db.models.base.ModelBase):
    """
    Metaclass for all LDAP models.
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(ModelBase, cls).__new__
        new_class = super_new(cls, name, bases, attrs)

        # patch manager to use our own QuerySet class
        if not new_class._meta.abstract:
            def get_query_set():
                return QuerySet(new_class)
            new_class.objects.get_query_set = get_query_set
            new_class._default_manager.get_query_set = get_query_set

        return new_class

class Model(django.db.models.base.Model):
    """
    Base class for all LDAP models.
    """
    __metaclass__ = ModelBase

    dn = django.db.models.fields.CharField(max_length=200)

    # meta-data
    base_dn = None
    search_scope = ldap.SCOPE_SUBTREE
    object_classes = ['top']

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self.saved_pk = self.pk

    def _collect_sub_objects(self, collector):
        """
        This private API seems to be called by the admin interface in django 1.2
        """
        pass

    def build_rdn(self):
        """
        Build the Relative Distinguished Name for this entry.
        """
        bits = []
        for field in self._meta.fields:
            if field.db_column and field.primary_key:
                bits.append("%s=%s" % (field.db_column, getattr(self, field.name)))
        if not len(bits):
            raise Exception("Could not build Distinguished Name")
        return '+'.join(bits)

    def build_dn(self):
        """
        Build the Distinguished Name for this entry.
        """
        return "%s,%s" % (self.build_rdn(), self.base_dn)
        raise Exception("Could not build Distinguished Name")

    def delete(self):
        """
        Delete this entry.
        """
        logging.debug("Deleting LDAP entry %s" % self.dn)
        ldapdb.connection.delete_s(self.dn)
        signals.post_delete.send(sender=self.__class__, instance=self)
        
    def save(self):
        if not self.dn:
            # create a new entry
            record_exists = False 
            entry = [('objectClass', self.object_classes)]
            new_dn = self.build_dn()

            for field in self._meta.fields:
                if not field.db_column:
                    continue
                value = getattr(self, field.name)
                if value:
                    entry.append((field.db_column, field.get_db_prep_save(value, connection=ldapdb.connection)))

            logging.debug("Creating new LDAP entry %s" % new_dn)
            ldapdb.connection.add_s(new_dn, entry)

            # update object
            self.dn = new_dn

        else:
            # update an existing entry
            record_exists = True
            modlist = []
            orig = self.__class__.objects.get(pk=self.saved_pk)
            for field in self._meta.fields:
                if not field.db_column:
                    continue
                old_value = getattr(orig, field.name, None)
                new_value = getattr(self, field.name, None)
                if old_value != new_value:
                    if new_value:
                        modlist.append((ldap.MOD_REPLACE, field.db_column, field.get_db_prep_save(new_value, connection=ldapdb.connection)))
                    elif old_value:
                        modlist.append((ldap.MOD_DELETE, field.db_column, None))

            if len(modlist):
                # handle renaming
                new_dn = self.build_dn()
                if new_dn != self.dn:
                    logging.debug("Renaming LDAP entry %s to %s" % (self.dn, new_dn))
                    ldapdb.connection.rename_s(self.dn, self.build_rdn())
                    self.dn = new_dn
            
                logging.debug("Modifying existing LDAP entry %s" % self.dn)
                ldapdb.connection.modify_s(self.dn, modlist)
            else:
                logging.debug("No changes to be saved to LDAP entry %s" % self.dn)

        # done
        self.saved_pk = self.pk
        signals.post_save.send(sender=self.__class__, instance=self, created=(not record_exists))

    @classmethod
    def scoped(base_class, base_dn):
        """
        Returns a copy of the current class with a different base_dn.
        """
        import new
        import re
        suffix = re.sub('[=,]', '_', base_dn)
        name = "%s_%s" % (base_class.__name__, str(suffix))
        new_class = new.classobj(name, (base_class,), {'base_dn': base_dn, '__module__': base_class.__module__})
        return new_class

