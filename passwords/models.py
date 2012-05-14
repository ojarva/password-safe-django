import re

from django.db import models
from ldapdb.models.fields import CharField, IntegerField, ListField
import ldapdb.models

#Class for representing an LDAP group entry.
class LdapGroup(ldapdb.models.Model):
    
    # LDAP meta-data
    base_dn = "ou=Groups,dc=futurice,dc=com"
    #object_classes = ['*']

    # attributes
    gid = IntegerField(db_column='gidNumber', unique=True)
    name = CharField(db_column='cn', max_length=200, primary_key=True)
    members = ListField(db_column='uniqueMember')

    def __unicode__(self):
        return self.name

    @property
    def members_usernames(self):
        usernames = []
        for member in self.members:
            # The members are given in ldap entries - we need to parse the user id from them
            matched = re.match(r'uid=(?P<uid>\w+?),.*', member)
            usernames.append(matched.group('uid'))
        return usernames

class Password(models.Model):
    
    # attributes
    targetSystem = models.CharField(max_length=100)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    ldapGroup = models.CharField(max_length=200)
    description = models.CharField(max_length=10000, null=True, blank=True)

    def __unicode__(self):
        return self.username
        
