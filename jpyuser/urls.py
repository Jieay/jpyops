#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from jpyapi.jpy001api import view_splitter
from jpyuser.views import *


urlpatterns = patterns('jpyuser.views',
                        url(r'^group/add/$', 'group_add', name='user_group_add'),
                        url(r'^group/list/$', 'group_list', name='user_group_list'),
                        url(r'^group/del/$', 'group_del', name='user_group_del'),
                        url(r'^group/edit/$', 'group_edit', name='user_group_edit'),
                        url(r'^user/add/$', 'user_add', name='user_add'),
                        url(r'^user/del/$', 'user_del', name='user_del'),
                        url(r'^user/list/$', 'user_list', name='user_list'),
                        url(r'^user/edit/$', 'user_edit', name='user_edit'),
#                        url(r'^password/reset/$', 'reset_password', name='password_reset'),
#                        url(r'^password/forget/$', 'forget_password', name='password_forget'),
                       )