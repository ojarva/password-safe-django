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

from django.conf import settings
from django.db.backends import BaseDatabaseFeatures, BaseDatabaseOperations

def escape_ldap_filter(value):
    value = unicode(value)
    return value.replace('\\', '\\5c') \
                .replace('*', '\\2a') \
                .replace('(', '\\28') \
                .replace(')', '\\29') \
                .replace('\0', '\\00')

class DatabaseCursor(object):
    def __init__(self, ldap_connection):
        self.connection = ldap_connection

class DatabaseFeatures(BaseDatabaseFeatures):
    pass

class DatabaseOperations(BaseDatabaseOperations):
    def quote_name(self, name):
        return name

class LdapConnection(object):
    def __init__(self):
        self.connection = None
        self.charset = "utf-8"
        self.features = DatabaseFeatures()
        self.ops = DatabaseOperations()

    def _cursor(self):
        if self.connection is None:
            self.connection = ldap.initialize(settings.LDAPDB_SERVER_URI)
            self.connection.simple_bind_s(
                settings.LDAPDB_BIND_DN,
                settings.LDAPDB_BIND_PASSWORD)
        return DatabaseCursor(self.connection)

    def add_s(self, dn, modlist):
        cursor = self._cursor()
        return cursor.connection.add_s(dn.encode(self.charset), modlist)

    def delete_s(self, dn):
        cursor = self._cursor()
        return cursor.connection.delete_s(dn.encode(self.charset))

    def modify_s(self, dn, modlist):
        cursor = self._cursor()
        return cursor.connection.modify_s(dn.encode(self.charset), modlist)

    def rename_s(self, dn, newrdn):
        cursor = self._cursor()
        return cursor.connection.rename_s(dn.encode(self.charset), newrdn.encode(self.charset))

    def search_s(self, base, scope, filterstr, attrlist):
        cursor = self._cursor()
        #test
        con = cursor.connection
        test_dict = {}
	for attr in dir(con):
            test_dict[attr] = getattr(con, attr)	

        results = cursor.connection.search_s(base, scope, filterstr.encode(self.charset), attrlist)
        output = []
        for dn, attrs in results:
            output.append((dn.decode(self.charset), attrs))
        return output

# FIXME: is this the right place to initialize the LDAP connection?
connection = LdapConnection()

