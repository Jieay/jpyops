#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
import hashlib
import datetime
import random
import json
#import crypt
from binascii import b2a_hex, a2b_hex
#from Crypto.Cipher import AES

from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
#from jpyuser.models import User, UserGroup, AdminGroup




def get_object(model, **kwargs):
    """
    use this function for query
    使用改封装函数查询数据库
    """
    for value in kwargs.values():
        if not value:
            return None

    the_object = model.objects.filter(**kwargs)
    if len(the_object) == 1:
        the_object = the_object[0]
    else:
        the_object = None
    return the_object


def http_success(request, msg):
    return render_to_response('success.html', locals())


def http_error(request, emg):
    message = emg
    return render_to_response('error.html', locals())


def my_render(template, data, request):
    return render_to_response(template, data, context_instance=RequestContext(request))


def page_list_return(total, current=1):
    """
    page
    分页，返回本次分页的最小页数到最大页数列表
    """
    min_page = current - 2 if current - 4 > 0 else 1
    max_page = min_page + 4 if min_page + 4 < total else total

    return range(min_page, max_page + 1)


def pages(post_objects, request):
    """
    page public function , return page's object tuple
    分页公用函数，返回分页的对象元组
    """
    paginator = Paginator(post_objects, 20)
    try:
        current_page = int(request.GET.get('page', '1'))
    except ValueError:
        current_page = 1

    page_range = page_list_return(len(paginator.page_range), current_page)

    try:
        page_objects = paginator.page(current_page)
    except (EmptyPage, InvalidPage):
        page_objects = paginator.page(paginator.num_pages)

    if current_page >= 5:
        show_first = 1
    else:
        show_first = 0

    if current_page <= (len(paginator.page_range) - 3):
        show_end = 1
    else:
        show_end = 0

    # 所有对象， 分页器， 本页对象， 所有页码， 本页页码，是否显示第一页，是否显示最后一页
    return post_objects, paginator, page_objects, page_range, current_page, show_first, show_end


# class PyCrypt(object):
#     """
#     This class used to encrypt and decrypt password.
#     加密类
#     """
# 
#     def __init__(self, key):
#         self.key = key
#         self.mode = AES.MODE_CBC
# 
#     @staticmethod
#     def gen_rand_pass(length=16, especial=False):
#         """
#         random password
#         随机生成密码
#         """
#         salt_key = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
#         symbol = '!@$%^&*()_'
#         salt_list = []
#         if especial:
#             for i in range(length - 4):
#                 salt_list.append(random.choice(salt_key))
#             for i in range(4):
#                 salt_list.append(random.choice(symbol))
#         else:
#             for i in range(length):
#                 salt_list.append(random.choice(salt_key))
#         salt = ''.join(salt_list)
#         return salt
# 
#     @staticmethod
#     def md5_crypt(string):
#         """
#         md5 encrypt method
#         md5非对称加密方法
#         """
#         return hashlib.new("md5", string).hexdigest()
# 
#     @staticmethod
#     def gen_sha512(salt, password):
#         """
#         generate sha512 format password
#         生成sha512加密密码
#         """
#         return crypt.crypt(password, '$6$%s$' % salt)
# 
#     def encrypt(self, passwd=None, length=32):
#         """
#         encrypt gen password
#         对称加密之加密生成密码
#         """
#         if not passwd:
#             passwd = self.gen_rand_pass()
# 
#         cryptor = AES.new(self.key, self.mode, b'8122ca7d906ad5e1')
#         try:
#             count = len(passwd)
#         except TypeError:
#             raise ServerError('Encrypt password error, TYpe error.')
# 
#         add = (length - (count % length))
#         passwd += ('\0' * add)
#         cipher_text = cryptor.encrypt(passwd)
#         return b2a_hex(cipher_text)
# 
#     def decrypt(self, text):
#         """
#         decrypt pass base the same key
#         对称加密之解密，同一个加密随机数
#         """
#         cryptor = AES.new(self.key, self.mode, b'8122ca7d906ad5e1')
#         try:
#             plain_text = cryptor.decrypt(a2b_hex(text))
#         except TypeError:
#             raise ServerError('Decrypt password error, TYpe error.')
#         return plain_text.rstrip('\0')

class ServerError(Exception):
    """
    self define exception
    自定义异常
    """
    pass


def is_role_request(request, role='user'):
    """
    require this request of user is right
    要求请求角色正确
    """
    role_all = {'user': 'CU', 'admin': 'GA', 'super': 'SU'}
    if request.user.role == role_all.get(role, 'CU'):
        return True
    else:
        return False


def view_splitter(request, su=None, adm=None):
    """
    for different user use different view
    视图分页器
    """
    if is_role_request(request, 'super'):
        return su(request)
    elif is_role_request(request, 'admin'):
        return adm(request)
    else:
        return HttpResponseRedirect(reverse('login'))


def defend_attack(func):
    def _deco(request, *args, **kwargs):
        if int(request.session.get('visit', 1)) > 10:
            #logger.debug('请求次数: %s' % request.session.get('visit', 1))
            return HttpResponse('Forbidden', status=403)
        request.session['visit'] = request.session.get('visit', 1) + 1
        request.session.set_expiry(300)
        return func(request, *args, **kwargs)
    return _deco


#logger = set_log(LOG_LEVEL)


def require_role(role='user'):
    """
    decorator for require user role in ["super", "admin", "user"]
    要求用户是某种角色 ["super", "admin", "user"]的装饰器
    """

    def _deco(func):
        def __deco(request, *args, **kwargs):
            request.session['pre_url'] = request.path
            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('login'))
            if role == 'admin':
                # if request.session.get('role_id', 0) < 1:
                if request.user.role == 'CU':
                    return HttpResponseRedirect(reverse('index'))
            elif role == 'super':
                # if request.session.get('role_id', 0) < 2:
                if request.user.role in ['CU', 'GA']:
                    return HttpResponseRedirect(reverse('index'))
            return func(request, *args, **kwargs)

        return __deco

    return _deco


def get_session_user_dept(request):
    """
    get department of the user in session
    获取session中用户的部门
    """
    return request.user, None


@require_role
def get_session_user_info(request):
    """
    get the user info of the user in session, for example id, username etc.
    获取用户的信息
    """
    return [request.user.id, request.user.username, request.user]


def get_tmp_dir():
    dir_name = os.path.join('/tmp', '%s' % (datetime.datetime.now().strftime('%Y%m%d-%H%M%S')))
    mkdir(dir_name, mode=777)
    return dir_name

class MyJsonEncoder(json.JSONEncoder):
    
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)        

