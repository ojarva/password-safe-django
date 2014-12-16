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

from copy import deepcopy
import ldap

from django.db.models.query import QuerySet as BaseQuerySet
from django.db.models.query_utils import Q
from django.db.models.sql import Query as BaseQuery
from django.db.models.sql.where import WhereNode as BaseWhereNode, Constraint as BaseConstraint, AND, OR

import ldapdb

from ldapdb.models.fields import CharField

def get_lookup_operator(lookup_type):
    if lookup_type == 'gte':
        return '>='
    elif lookup_type == 'lte':
        return '<='
    else:
        return '='

class Constraint(BaseConstraint):
    """
    An object that can be passed to WhereNode.add() and knows how to
    pre-process itself prior to including in the WhereNode.
    """
    def process(self, lookup_type, value):
        """
        Returns a tuple of data suitable for inclusion in a WhereNode
        instance.
        """
        # Because of circular imports, we need to import this here.
        from django.db.models.base import ObjectDoesNotExist

        try:
            if self.field:
                params = self.field.get_db_prep_lookup(lookup_type, value)
                db_type = self.field.db_type()
            else:
                params = CharField().get_db_prep_lookup(lookup_type, value)
                db_type = None
        except ObjectDoesNotExist:
            raise EmptyShortCircuit

        return (self.alias, self.col, db_type), params

class Compiler(object):
    def __init__(self, query, connection, using):
        self.query = query
        self.connection = connection
        self.using = using

    def results_iter(self):
        if self.query.select_fields:
            fields = self.query.select_fields
        else:
            fields = self.query.model._meta.fields

        attrlist = [ x.db_column for x in fields if x.db_column ]

        try:
            vals = self.connection.search_s(
                self.query.model.base_dn,
                self.query.model.search_scope,
                filterstr=self.query._ldap_filter(),
                attrlist=attrlist,
            )
        except ldap.NO_SUCH_OBJECT:
            return

        # perform sorting
        if self.query.extra_order_by:
            ordering = self.query.extra_order_by
        elif not self.query.default_ordering:
            ordering = self.query.order_by
        else:
            ordering = self.query.order_by or self.query.model._meta.ordering
        def cmpvals(x, y):
            for fieldname in ordering:
                if fieldname.startswith('-'):
                    fieldname = fieldname[1:]
                    negate = True
                else:
                    negate = False
                field = self.query.model._meta.get_field(fieldname)
                attr_x = field.from_ldap(x[1].get(field.db_column, []), connection=self.connection)
                attr_y = field.from_ldap(y[1].get(field.db_column, []), connection=self.connection)
                # perform case insensitive comparison
                if hasattr(attr_x, 'lower'):
                    attr_x = attr_x.lower()
                if hasattr(attr_y, 'lower'):
                    attr_y = attr_y.lower()
                val = negate and cmp(attr_y, attr_x) or cmp(attr_x, attr_y)
                if val:
                    return val
            return 0
        vals = sorted(vals, cmp=cmpvals)

        # process results
        pos = 0
        for dn, attrs in vals:
            # FIXME : This is not optimal, we retrieve more results than we need
            # but there is probably no other options as we can't perform ordering
            # server side.
            if (self.query.low_mark and pos < self.query.low_mark) or \
               (self.query.high_mark is not None and pos >= self.query.high_mark):
                pos += 1
                continue
            row = []
            for field in iter(fields):
                if field.attname == 'dn':
                    row.append(dn)
                elif hasattr(field, 'from_ldap'):
                    row.append(field.from_ldap(attrs.get(field.db_column, []), connection=self.connection))
                else:
                    row.append(None)
            yield row
            pos += 1


class WhereNode(BaseWhereNode):
    def add(self, data, connector):
        if not isinstance(data, (list, tuple)):
            super(WhereNode, self).add(data, connector)
            return

        # we replace the native Constraint by our own
        obj, lookup_type, value = data
        if hasattr(obj, "process"):
            obj = Constraint(obj.alias, obj.col, obj.field)
        super(WhereNode, self).add((obj, lookup_type, value), connector)

    def as_sql(self, qn=None, connection=None):
        bits = []
        for item in self.children:
            if hasattr(item, 'as_sql'):
                sql, params = item.as_sql(qn=qn, connection=connection)
                bits.append(sql)
                continue

            constraint, lookup_type, y, values = item
            comp = get_lookup_operator(lookup_type)
            if hasattr(constraint, "col"):
                # django 1.2
                column = constraint.col
                if lookup_type == 'in':
                    equal_bits = [ "(%s%s%s)" % (column, comp, value) for value in values ]
                    clause = '(|%s)' % ''.join(equal_bits)
                else:
                    clause = "(%s%s%s)" % (constraint.col, comp, values)
            else:
                # django 1.1
                (table, column, db_type) = constraint
                equal_bits = [ "(%s%s%s)" % (column, comp, value) for value in values ]
                if len(equal_bits) == 1:
                    clause = equal_bits[0]
                else:
                    clause = '(|%s)' % ''.join(equal_bits)

            if self.negated:
                bits.append('(!%s)' % clause)
            else:
                bits.append(clause)
        if len(bits) == 0:
            sql_string = ""
        elif len(bits) == 1:
            sql_string = bits[0]
        elif self.connector == AND:
            sql_string = '(&%s)' % ''.join(bits)
        elif self.connector == OR:
            sql_string = '(|%s)' % ''.join(bits)
        else:
            raise Exception("Unhandled WHERE connector: %s" % self.connector)
        return sql_string, []

class Query(BaseQuery):
    def __init__(self, *args, **kwargs):
        super(Query, self).__init__(*args, **kwargs)
        self.connection = ldapdb.connection

    def _ldap_filter(self):
        filterstr = ''.join(['(objectClass=%s)' % cls for cls in self.model.object_classes])
        sql, params = self.where.as_sql()
        filterstr += sql
        return '(&%s)' % filterstr

    def get_count(self, using=None):
        try:
            vals = ldapdb.connection.search_s(
                self.model.base_dn,
                self.model.search_scope,
                filterstr=self._ldap_filter(),
                attrlist=[],
            )
        except ldap.NO_SUCH_OBJECT:
            return 0

        number = len(vals)

        # apply limit and offset
        number = max(0, number - self.low_mark)
        if self.high_mark is not None:
            number = min(number, self.high_mark - self.low_mark)

        return number

    def get_compiler(self, using=None, connection=None):
        return Compiler(self, ldapdb.connection, using)

    def results_iter(self):
        "For django 1.1 compatibility"
        return self.get_compiler().results_iter()

class QuerySet(BaseQuerySet):
    def __init__(self, model=None, query=None, using=None):
        if not query:
            import inspect
            spec = inspect.getargspec(BaseQuery.__init__)
            if len(spec[0]) == 3:
                # django 1.2
                query = Query(model, WhereNode)
            else:
                # django 1.1
                query = Query(model, None, WhereNode)
        super(QuerySet, self).__init__(model=model, query=query)

    def delete(self):
        "Bulk deletion."
        try:
            vals = ldapdb.connection.search_s(
                self.model.base_dn,
                self.model.search_scope,
                filterstr=self.query._ldap_filter(),
                attrlist=[],
            )
        except ldap.NO_SUCH_OBJECT:
            return

        # FIXME : there is probably a more efficient way to do this 
        for dn, attrs in vals:
            ldapdb.connection.delete_s(dn)

