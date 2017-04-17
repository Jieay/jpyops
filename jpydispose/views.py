#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import time
import re

from jpyapi.jpy001api import *
from jpyapi.jpyassetapi import *
from jpyasset.models import HostAsset, IDC, Areas, Items, Functions, PlanVocational, SaltReturns
from jpydispose.models import TaskTest
from jpyapi.saltapi import *


@require_role(role='user')
def dispose_add(request):
    ret = {'status':0, 'data':'','message':''}
    hostip = request.POST.get('hostip')
    cmdfurits = request.POST.get('furits')
    parm_arg = request.POST.get('parm_arg', '')
    
    salt = saltAPI()
    if not hostip:
        hostip = '*'
    if parm_arg:
        params = {'client':'local', 'fun':cmdfurits, 'tgt':hostip, 'arg1':parm_arg}
    else:
        cmdfurits = 'test.ping'
        params = {'client':'local', 'fun':cmdfurits, 'tgt':hostip}
        
    result = salt.saltCmd(params)
    
    try:
        if result:
            jsresult = json.dumps(result)
            temp = TaskTest.objects.create(hostip=hostip,fruits=jsresult)
            temp.save()
            ret['status'] = 1
            ret['data'] = result            
    except Exception,e:
        ret['message'] = e.message
        
    return HttpResponse(json.dumps(ret), content_type="application/json")



@require_role(role='user')
def dispose_history(request):
    ret = {'status':0, 'data':'','message':''}    
#     cmd_details = TaskTest.objects.all().values('id', 'fruits', 'create_time')
#     cmd_details = TaskTest.objects.all().order_by('-id')[0:10].values('id', 'fruits', 'create_time')
    cmd_details = SaltReturns.objects.all().order_by('-id')[0:10].values('id', 'jid', 'returns', 'ids', 'success', 'alter_time')
    cmd_details = list(cmd_details)
    print cmd_details
    print type(cmd_details)
    print type(cmd_details[0])
    print cmd_details[0]
    ret['data'] = cmd_details
    ret['status'] = 1
    print ret
    
    return HttpResponse(json.dumps(ret, cls=MyJsonEncoder), content_type="application/json")


@require_role(role='user')
def dispose_news(request):
    ret = {'status':0, 'data':'','message':''}  
    ht_id = request.POST.get('ht_id')
    print ht_id
    try:
#         cmd_details = TaskTest.objects.filter(id__gt=ht_id).order_by('-id').values('id', 'fruits', 'create_time')
        cmd_details = SaltReturns.objects.filter(id__gt=ht_id).order_by('-id').values('id', 'jid', 'returns', 'ids', 'success', 'alter_time')
        cmd_details = list(cmd_details)
        print cmd_details
        print type(cmd_details)
        ret['data'] = cmd_details
        if cmd_details:
            ret['status'] = 1
        print type(ret)
    except Exception,e:
        ret['message'] = e.message
    
    return HttpResponse(json.dumps(ret, cls=MyJsonEncoder), content_type="application/json")


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