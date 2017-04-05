#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import time
import re

from jpyapi.jpy001api import *
from jpyapi.jpyassetapi import *


@require_role(role='user')
def dispose_list(request):
    """
    dispose list view
    """
    header_title, path1, path2 = u'查看部署', u'部署管理', u'查看部署'
    posts = IDC.objects.all()
    keyword = request.GET.get('keyword', '')
    status = request.GET.get('status', '')

    return my_render('jpydispose/dispose_list.html', locals(), request)