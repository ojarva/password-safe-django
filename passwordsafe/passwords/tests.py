"""
    >>> from .models import LdapGroup
    >>> from .utils import *

    >>> from django.conf import settings
    >>> import ldap
    >>> def get_binded_connection():
    ...     con = ldap.initialize(settings.LDAPDB_SERVER_URI)
    ...     con.simple_bind_s(settings.LDAPDB_BIND_DN, settings.LDAPDB_BIND_PASSWORD)
    ...     return con
    >>> def get_attr_dict(dn):
    ...     con = get_binded_connection()
    ...     return con.search_s(dn, ldap.SCOPE_BASE)[0][1]

members_usernames
==================

>>> t = LdapGroup(name='test')
>>> t.members_usernames
[]
>>> t.members = ['uid=jmclain,ou=People,dc=futurice,dc=com', 'uid=ojar,ou=People,dc=futurice,dc=com']
>>> set(t.members_usernames) == set(['jmclain', 'ojar'])
True

get_ldap_groups
=================

Fixture
---------

    Adding a user :

    >>> add_list = [('cn', ['John Mc Clain']), ('gidNumber', ['19910019']), ('homeDirectory', ['/home/blabla']), ('sambaSID', ['16871876816']), ('sn', ['blablabla']), ('uidNumber', ['77676767']), ('ntUserDomainId', ['jmclain']), ('uid', ['jmclain']), ('objectclass', ['inetOrgPerson', 'ntUser', 'account', 'hostObject', 'posixAccount', 'shadowAccount', 'sambaSamAccount', 'organizationalPerson', 'top', 'person'])]

    >>> con = get_binded_connection()
    
    Delete user if already exist first.

    >>> try:
    ...     trash = con.delete_s('uid=jmclain,ou=People,dc=futurice,dc=com')
    ... except ldap.NO_SUCH_OBJECT:
    ...     pass
    >>> trash = con.add_s('uid=jmclain,ou=People,dc=futurice,dc=com', add_list)

User with no groups
-----------------------

    >>> get_ldap_groups('jmclain')
    []

Fixture
---------

Adding a few groups to add our user to them

    >>> add_list = [('cn', ['SaveTheWorld']), ('gidNumber', ['774455103']),
    ...     ('sambaGroupType', ['2']), ('sambaSID', ['784poo67']), ('labeledURI', ['proj.save-the-world']), ('objectclass', ['sambaGroupMapping', 'groupofuniquenames', 'top', 'posixGroup', 'labeledURIObject']), ('uniqueMember', ['uid=jmclain,ou=People,dc=futurice,dc=com'])]
    >>> add_list2 = [('cn', ['SaveTheWorld2']), ('gidNumber', ['774455103']),
    ...     ('sambaGroupType', ['2']), ('sambaSID', ['784poo67']), ('labeledURI', ['proj.save-the-world']), ('objectclass', ['sambaGroupMapping', 'groupofuniquenames', 'top', 'posixGroup', 'labeledURIObject']), ('uniqueMember', ['uid=jmclain,ou=People,dc=futurice,dc=com', 'uid=spiq,ou=People,dc=futurice,dc=com'])]
    >>> add_list3 = [('cn', ['SaveTheWorld3']), ('gidNumber', ['774455103']),
    ...     ('sambaGroupType', ['2']), ('sambaSID', ['784poo67']), ('labeledURI', ['proj.save-the-world']), ('objectclass', ['sambaGroupMapping', 'groupofuniquenames', 'top', 'posixGroup', 'labeledURIObject']), ('uniqueMember', ['uid=jmclain,ou=People,dc=futurice,dc=com', 'uid=spiq,ou=People,dc=futurice,dc=com'])]
    >>> try:
    ...     trash = con.delete_s('cn=SaveTheWorld,ou=Projects,ou=Groups,dc=futurice,dc=com')
    ... except ldap.NO_SUCH_OBJECT:
    ...     pass
    >>> try:
    ...     trash = con.delete_s('cn=SaveTheWorld2,ou=Projects,ou=Groups,dc=futurice,dc=com')
    ... except ldap.NO_SUCH_OBJECT:
    ...     pass
    >>> try:
    ...     trash = con.delete_s('cn=SaveTheWorld3,ou=Projects,ou=Groups,dc=futurice,dc=com')
    ... except ldap.NO_SUCH_OBJECT:
    ...     pass
    >>> trash = con.add_s('cn=SaveTheWorld,ou=Projects,ou=Groups,dc=futurice,dc=com', add_list)
    >>> trash = con.add_s('cn=SaveTheWorld2,ou=Projects,ou=Groups,dc=futurice,dc=com', add_list2)
    >>> trash = con.add_s('cn=SaveTheWorld3,ou=Projects,ou=Groups,dc=futurice,dc=com', add_list3)

User with three groups
-------------------------

    >>> jmclain_groups = get_ldap_groups('jmclain')
    >>> len(jmclain_groups) == 3
    True
    >>> set([g.name for g in jmclain_groups]) == set(['SaveTheWorld', 'SaveTheWorld2', 'SaveTheWorld3'])
    True

check_autorization
====================

Fixture
---------

    >>> p = Password(targetSystem='bla', username='bla', password='superSecret', ldapGroup='SomeGroup')
    >>> p.save()
    >>> add_list = [('cn', ['SomeGroup']), ('gidNumber', ['774455103']),
    ...     ('sambaGroupType', ['2']), ('sambaSID', ['784poo67']), ('labeledURI', ['proj.save-the-world']), ('objectclass', ['sambaGroupMapping', 'groupofuniquenames', 'top', 'posixGroup', 'labeledURIObject']), ('uniqueMember', ['uid=spiq,ou=People,dc=futurice,dc=com'])]
    >>> try:
    ...     trash = con.delete_s('cn=SomeGroup,ou=Projects,ou=Groups,dc=futurice,dc=com')
    ... except ldap.NO_SUCH_OBJECT:
    ...     pass
    >>> trash = con.add_s('cn=SomeGroup,ou=Projects,ou=Groups,dc=futurice,dc=com', add_list)

Unexisting password
---------------------

    >>> check_authorization(None, 'jmclain')
    >>> check_authorization(100000000000000000, 'jmclain')

Unallowed password
---------------------

    >>> check_authorization(p.pk, 'jmclain')
    False

Fixture
-----------

    >>> p.ldapGroup = 'SaveTheWorld'
    >>> p.save()

Allowed password
------------------

    >>> check_authorization(p.pk, 'jmclain')
    True

Cleaning-up
-------------
    
    >>> p.delete()

    >>> try:
    ...     trash = con.delete_s('cn=SaveTheWorld,ou=Projects,ou=Groups,dc=futurice,dc=com')
    ...     pass
    ... except ldap.NO_SUCH_OBJECT:
    ...     pass
    >>> try:
    ...     trash = con.delete_s('cn=SaveTheWorld2,ou=Projects,ou=Groups,dc=futurice,dc=com')
    ... except ldap.NO_SUCH_OBJECT:
    ...     pass
    >>> try:
    ...     trash = con.delete_s('cn=SaveTheWorld3,ou=Projects,ou=Groups,dc=futurice,dc=com')
    ... except ldap.NO_SUCH_OBJECT:
    ...     pass
    >>> try:
    ...     trash = con.delete_s('uid=jmclain,ou=People,dc=futurice,dc=com')
    ... except ldap.NO_SUCH_OBJECT:
    ...     pass
    >>> try:
    ...     trash = con.delete_s('cn=SomeGroup,ou=Projects,ou=Groups,dc=futurice,dc=com')
    ... except ldap.NO_SUCH_OBJECT:
    ...     pass
"""
