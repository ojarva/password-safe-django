from functools import wraps


from django.core.cache import cache

from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from models import Password, LdapGroup
from forms import PasswordForm
from utils import check_authorization, get_ldap_groups

def check_ldap_access(view_func):
    """
    Decorator for views with signature `view(request, pw_pk, **kwargs)`. Denies the access if the connected user has no rights on the password.
    If *pw_pk* is None, then authorization is never denied. If the password doesn't exist, then view is called with `pw_pk=None`.
    """
    def _decorated_view (request, pw_pk=None, **kwargs):
        if not pw_pk or check_authorization(pw_pk, request.user.username):
            return view_func(request, pw_pk, **kwargs)
        elif check_authorization(pw_pk, request.user.username) == None:
            return view_func(request, None, **kwargs) 
        else:
            raise PermissionDenied(str(get_ldap_groups(request.user.username))+request.user.username)
    return wraps(view_func)(_decorated_view)

def first_parameter_to_int(view_func):
    """
    Decorator for views with signature `view(request, pw_pk, **kwargs)`. Calls the view with *pw_pk* converted to an int. If *pw_pk* is None, the value stays the same.

    Unhandled exception if int(pw_pk) fails - with correct url regex ([0-9]+) that never happens.
    """
    def _decorated_view (request, pw_pk=None, **kwargs):
        if pw_pk == None:
            pass
        else:
            pw_pk = int(pw_pk)
        return view_func(request, pw_pk, **kwargs)
    return wraps(view_func)(_decorated_view)

def index(request):
    username = request.user.username
    user_passwords = filter(lambda p: check_authorization(p.pk, username),
        Password.objects.all())
    
    if request.session.get('showOnly', True):
        show_only_accessible = True
    else:
        show_only_accessible = False

    baseUrl = '/'
    
    return direct_to_template(request, 'passwords/index.html', {'passwords': Password.objects.all(), 'user_passwords': user_passwords, 'showOnly': show_only_accessible, 'baseUrl': baseUrl})

def new_password(request):
    new = True
    password = Password()

    ldap_groups = get_ldap_groups(request.user.username)
    ldap_groups_choices = [(lg, lg) for lg in ldap_groups]
    if request.method == 'POST':
        form = PasswordForm(request.POST, instance=password,
            ldap_groups_choices=ldap_groups_choices)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
    elif request.method == 'GET':
        form = PasswordForm(instance=password,
            ldap_groups_choices=ldap_groups_choices)

    return direct_to_template(request, 'passwords/edit_password.html', {'form': form, 'ldapGroups': LdapGroup.objects.all(), 'new': new})

@first_parameter_to_int
@check_ldap_access
def edit_password(request, pw_pk=None):
    new = False
    password = get_object_or_404(Password, pk=pw_pk)

    ldap_groups = get_ldap_groups(request.user.username)
    ldap_groups_choices = [(lg, lg) for lg in ldap_groups]
    if request.method == 'POST':
        form = PasswordForm(request.POST, instance=password,
            ldap_groups_choices=ldap_groups_choices)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
    elif request.method == 'GET':
        form = PasswordForm(instance=password,
            ldap_groups_choices=ldap_groups_choices)

    return direct_to_template(request, 'edit_password.html', {'form': form, 'ldapGroups': LdapGroup.objects.all(), 'new': new})

@first_parameter_to_int
@check_ldap_access
def delete_password(request, pw_pk=None):
    try:
        pw = Password.objects.get(pk=pw_pk)
    except Password.DoesNotExist:
        pass
    else:    
        pw.delete()
    return HttpResponseRedirect(reverse("index"))

@first_parameter_to_int
@check_ldap_access
def get_password(request, pw_pk=None):
    try:
        pw = Password.objects.get(pk=pw_pk)
    except Password.DoesNotExist:
        raise Http404 
    return HttpResponse(pw.password, mimetype="text/plain")
