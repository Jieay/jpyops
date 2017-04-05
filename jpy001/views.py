#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import urllib
from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseNotFound
from django.http import HttpResponse
import paramiko
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from jpyapi.jpy001api import *
from jpyuser.models import User
from jpyasset.models import HostAsset, Items, Areas, IDC, Functions


@require_role(role='user')
def index_cu(request):
    username = request.user.username
    return HttpResponseRedirect(reverse('host_list'))


@require_role(role='user')
def index(request):
    
    if is_role_request(request, 'user'):
        return index_cu(request)

    elif is_role_request(request, 'super'):    
        users = User.objects.all()
        hosts = HostAsset.objects.all()
        items = Items.objects.all()
        areas = Areas.objects.all()
        idcs = IDC.objects.all()
        functs = Functions.objects.all()
        active_users = User.objects.filter(is_active=1)    
        
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))


def skin_config(request):
    return render_to_response('skin_config.html')


@defend_attack
def Login(request):
    """登录界面"""
    error = ''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'GET':
        return render_to_response('login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if user.role == 'SU':
                        request.session['role_id'] = 2
                    elif user.role == 'GA':
                        request.session['role_id'] = 1
                    else:
                        request.session['role_id'] = 0
                    return HttpResponseRedirect(request.session.get('pre_url', '/'))
                else:
                    error = '用户未激活'
            else:
                error = '用户名或密码错误'
        else:
            error = '用户名或密码错误'
    return render_to_response('login.html', {'error': error})


@require_role(role='user')
def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))