#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from jpydispose.views import *

urlpatterns = patterns('',
    url(r'^dispose/list/$', dispose_list, name='dispose_list'),
    url(r'^dispose/add/$', dispose_add, name='dispose_add'),
    url(r'^dispose/history/$', dispose_history, name='dispose_history'),
    url(r'^dispose/news/$', dispose_news, name='dispose_news'),
)