from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('jpy001.views',
    # Examples:
    # url(r'^$', 'jpy001.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'index', name='index'),
    url(r'^skin_config/$', 'skin_config', name='skin_config'),
    url(r'^login/$', 'Login', name='login'),
    url(r'^logout/$', 'Logout', name='logout'),    
    url(r'^jpyasset/', include('jpyasset.urls')),
    url(r'^jpyuser/', include('jpyuser.urls')),
    url(r'^jpydispose/', include('jpydispose.urls')),
)
