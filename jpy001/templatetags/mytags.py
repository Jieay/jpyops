#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import ast
import time

from django import template
from jpyapi.jpy001api import *
from jpyapi.jpyassetapi import *
from jpyuser.models import User, UserGroup
from jpyasset.models import IDC, Items, Areas, Functions, ConfigVocational, PlanVocational



register = template.Library()


@register.filter(name='int2str')
def int2str(value):
    """
    int 转换为 str
    """
    return str(value)


@register.filter(name='bool2str')
def bool2str(value):
    if value:
        return u'是'
    else:
        return u'否'


@register.filter(name='result2bool')
def result2bool(result=''):
    """将结果定向为结果"""
    result = eval(result)
    unreachable = result.get('unreachable', [])
    failures = result.get('failures', [])

    if unreachable or failures:
        return '<b style="color: red">失败</b>'
    else:
        return '<b style="color: green">成功</b>'


@register.filter(name='rule_member_count')
def rule_member_count(instance, member):
    """
    instance is a rule object,
    use to get the number of the members
    :param instance:
    :param member:
    :return:
    """
    member = getattr(instance, member)
    counts = member.all().count()
    return str(counts)


@register.filter(name='rule_member_name')
def rule_member_name(instance, member):
    """
    instance is a rule object,
    use to get the name of the members
    :param instance:
    :param member:
    :return:
    """
    member = getattr(instance, member)
    names = member.all()

    return names


@register.filter(name='str_to_list')
def str_to_list(info):
    """
    str to list
    """
    print ast.literal_eval(info), type(ast.literal_eval(info))
    return ast.literal_eval(info)


@register.filter(name='str_to_dic')
def str_to_dic(info):
    """
    str to list
    """
    if '{' in info:
        info_dic = ast.literal_eval(info).iteritems()
    else:
        info_dic = {}
    return info_dic


@register.filter(name='str_to_code')
def str_to_code(char_str):
    if char_str:
        return char_str
    else:
        return u'空'


@register.filter(name='ip_str_to_list')
def ip_str_to_list(ip_str):
    """
    ip str to list
    """
    return ip_str.split(',')


@register.filter(name='get_cpu_core')
def get_cpu_core(cpu_info):
    cpu_core = cpu_info.split('* ')[1] if cpu_info and '*' in cpu_info else cpu_info
    return cpu_core


@register.filter(name='get_disk_info')
def get_disk_info(disk_info):
    try:
        if disk_info:
            disk_list = json.loads(disk_info)
            disk_size = disk_list
        else:
            disk_size = ''
    except Exception, e:
        disk_size = disk_info
    return disk_size    


@register.filter(name='to_avatar')
def to_avatar(role_id='0'):
    """不同角色不同头像"""
    role_dict = {'0': 'user', '1': 'admin', '2': 'root'}
    return role_dict.get(str(role_id), 'user')


@register.filter(name='members_count')
def members_count(group_id):
    """统计用户组下成员数量"""
    group = get_object(UserGroup, id=group_id)
    if group:
        return group.user_set.count()
    else:
        return 0


@register.filter(name='appfile_mem_count')
def appfile_mem_count(conf_id):
    """统计配置下文件的数量"""
    conf = get_object(ConfigVocational, id=conf_id)
    if conf:
        return conf.configfile.count()
    else:
        return 0


@register.filter(name='conf_mem_count')
def conf_mem_count(plan_id):
    """统计方案下配置的数量"""
    plan = get_object(PlanVocational, id=plan_id)
    if plan:
        return plan.configset.count()
    else:
        return 0
    

@register.filter(name='get_role')
def get_role(user_id):
    """
    根据用户id获取用户权限
    """

    user_role = {'SU': u'超级管理员', 'GA': u'部门管理员', 'CU': u'普通用户'}
    user = get_object(User, id=user_id)
    if user:
        return user_role.get(str(user.role), u"普通用户")
    else:
        return u"普通用户"
        
    
@register.filter(name='groups2str')
def groups2str(group_list):
    """
    将用户组列表转换为str
    """
    if len(group_list) < 3:
        return ' '.join([group.name for group in group_list])
    else:
        return '%s ...' % ' '.join([group.name for group in group_list[0:2]])
    
    
@register.filter(name='to_name')
def to_name(user_id):
    """user id 转位用户名称"""
    try:
        user = User.objects.filter(id=int(user_id))
        if user:
            user = user[0]
            return user.name
    except:
        return '非法用户'
    

