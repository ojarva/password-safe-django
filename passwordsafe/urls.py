import os

from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

from django.http import HttpResponse

def ping(request):
    return HttpResponse('status: OK')

urlpatterns = patterns('',

    url(r'^ping/$', ping),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    url(r'^login/$', 'django.contrib.auth.views.login', kwargs={'template_name': 'login.html'}),

    url(r'^$', 'passwordsafe.passwords.views.index', name="index"),
    
     # Edit and save password functions
    (r'^getPassword/(?P<pw_pk>\d*)/$', 'passwordsafe.passwords.views.get_password'),
    (r'^editPassword/(?P<pw_pk>\d*)/$', 'passwordsafe.passwords.views.edit_password'),      
    (r'^newPassword/$', 'passwordsafe.passwords.views.new_password'),
    (r'^deletePassword/(?P<pw_pk>\d*)/$', 'passwordsafe.passwords.views.delete_password'),  
    
    # Remove from the real version
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.abspath('./static')}),
)
