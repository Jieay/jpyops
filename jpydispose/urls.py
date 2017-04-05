#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from jpydispose.views import *

urlpatterns = patterns('',
    url(r'^dispose/list/$', dispose_list, name='dispose_list'),
)