import os

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.http import HttpResponse

def ping(request):
    return HttpResponse('status: OK')

urlpatterns = patterns('',
    # Example:
    # (r'^passwordsafe/', include('passwordsafe.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^ping/$', ping),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    url(r'^login/$', 'django.contrib.auth.views.login', kwargs={'template_name': 'login.html'}),

    url(r'^$', 'passwordsafe.passwords.views.index', name="index"),
    
     # Edit and save password functions
    (r'^getPassword/(?P<pw_pk>\d*)/$', 'passwordsafe.passwords.views.getPassword'),
    (r'^editPassword/(?P<pw_pk>\d*)/$', 'passwordsafe.passwords.views.editPassword'),      
    (r'^newPassword/$', 'passwordsafe.passwords.views.newPassword'),   
    (r'^deletePassword/(?P<pw_pk>\d*)/$', 'passwordsafe.passwords.views.deletePassword'),  
    
    # Remove from the real version
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.abspath('./static')}),
)
