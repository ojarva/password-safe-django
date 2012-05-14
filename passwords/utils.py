from django.core.cache import cache
from .models import Password, LdapGroup

def get_ldap_groups(username):
    """
    Returns:
        list. A list of all LdapGroups, which have *username* as a member.  
    """
    cache_key = "ldap_groups_%s" % username
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    ldap_groups = []    
    # Find user ldap groups
    for ldap_group in LdapGroup.objects.all():
        if username in ldap_group.members_usernames:
            ldap_groups.append(ldap_group)

    cache.set(cache_key, ldap_groups, 120)

    return ldap_groups

def check_authorization(pw_pk, username=None):
    """
    Args:
        pw_pk(str). Password's primary key.
        username(str). 
    
    Returns:
        bool. True if *username* is authorized to see password *pw_pk*, None if *pw_pk* doesn't exist ; False otherwise.
    """
    try:
        password = Password.objects.get(pk=pw_pk)
    except Password.DoesNotExist:
        return False

    cache_key = "authorization_%s_%s" % (pw_pk, username)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        ldap_group = LdapGroup.objects.get(pk=password.ldapGroup) 
    except:
        cache.set(cache_key, False, 120)
        return False
    if username in ldap_group.members_usernames:
        cache.set(cache_key, True, 120)
        return True
    else: 
        cache.set(cache_key, False, 120)
        return False
