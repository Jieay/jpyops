#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time
import re
from django.db.models import Q
from jpyapi.jpy001api import *
from jpyapi.jpyassetapi import *
from jpyasset.forms import IdcForm, ItemsForm, AreasForm, FunctionsForm, HostsForm, IpassetForm, CloudRecordForm, ServerTypeForm, ApplyVocationalForm, ApplyFileForm, ConfigVocationalForm, TaskNameForm, ConfigPlanTaskForm, PlanVocationalForm
from jpyasset.models import IDC, Items, Areas, Functions, HostAsset, IpAsset, CloudRecord, ApplyVocational, ServerType, ApplyFile, ConfigVocational, PlanVocational, TaskName, ConfigPlanTask
from jpyasset.models import IDC_TYPE, NATION_TYPE, ASSET_STATUS, CLOUDRD_STATUS, APPLY_TYPE, TOOLS_TYPE, CONF_STEP

from jpyapi.jpycloudapi import ALiYunApi, TenXunYunCvm
from django.http import HttpResponse
from jpy001.settings import MEDIA_ROOT
from django.shortcuts import get_object_or_404
from _ast import Add




@require_role(role='user')
def host_list(request):
    """
    host list view
    """
    header_title, path1, path2, path3 = u'查看主机', u'资源管理', u'查看主机' , u'主机管理'
    user_perm = request.session['role_id']
    posts = HostAsset.objects.all()
    idc_all = IDC.objects.filter()
    item_all = Items.objects.filter()
    area_all = Areas.objects.filter()
    functs_all = Functions.objects.filter()
    host_status = ASSET_STATUS    
    
    keyword = request.GET.get('keyword', '')
    status = request.GET.get('status', '')
    
    if status:
        posts = HostAsset.objects.filter(status__contains=status)
  
    if keyword:
        posts = HostAsset.objects.filter(
            Q(hostname__contains=keyword) |
            Q(wan_ip__contains=keyword) |
            Q(lan_ip__contains=keyword) |
            Q(comment__contains=keyword))
        if not posts:
            idc_name = IDC.objects.filter(Q(name__contains=keyword))
            item_name = Items.objects.filter(Q(name__contains=keyword))
            area_name = Areas.objects.filter(Q(name__contains=keyword))
            functs_name = Functions.objects.filter(Q(name__contains=keyword))
            if idc_name:
                posts = HostAsset.objects.filter(idc=idc_name)
            elif item_name:
                posts = HostAsset.objects.filter(item=item_name)
            elif area_name:
                posts = HostAsset.objects.filter(area=area_name)
            elif functs_name:
                posts = HostAsset.objects.filter(functs=functs_name)
            else:
                posts = HostAsset.objects.exclude(hostname='ALL').order_by('id')
    else:
        posts = HostAsset.objects.exclude(hostname='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    
    if user_perm == 2:
        return my_render('jpyasset/jhost_list.html', locals(), request)
    else:
        return my_render('jpyasset/jhost_list_cu.html', locals(), request)


@require_role(role='super')
def host_detail(request):
    """
    Asset detail view
    """
    header_title, path1, path2, path3 = u'主机详细信息', u'资产管理', u'主机详情', u'主机管理'
    hostasset_id = request.GET.get('id', '')
    hostasset = get_object(HostAsset, id=hostasset_id)

    return my_render('jpyasset/jhost_detail.html', locals(), request)


@require_role(role='super')
def host_add(request):
    """
    host add view
    """
    header_title, path1, path2, path3 = u'添加主机', u'资源管理', u'添加主机' , u'主机管理'
    host_all = HostAsset.objects.all()
    af = HostsForm()
    if request.method == 'POST':
        af_post = HostsForm(request.POST)
        wan_ip = request.POST.get('wan_ip', '')
        lan_ip = request.POST.get('lan_ip', '')
        hostname = request.POST.get('hostname', '')

        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            if HostAsset.objects.filter(hostname=unicode(hostname)):
                error = u'该主机名 %s 已存在!' % hostname
                raise ServerError(error)
            if len(hostname) > 128:
                error = u"主机名长度不能超过128位!"
                raise ServerError(error)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                host_save = af_post.save(commit=False)
                if not use_default_auth:
                    password = request.POST.get('password', '')
                    #password_encode = CRYPTOR.encrypt(password)
                    #host_save.password = password_encode
                    host_save.password = password
                if not wan_ip:
                    host_save.wan_ip = hostname
                host_save.save()
                af_post.save_m2m()

                msg = u'主机 %s 添加成功' % hostname
            else:
                esg = u'主机 %s 添加失败' % hostname

    return my_render('jpyasset/jhost_add.html', locals(), request)


@require_role(role='super')
def host_del(request):
    """
    del a host
    """
    host_ids = request.GET.get('id', '')
    host_id_list = host_ids.split(',')

    for host_id in host_id_list:
        HostAsset.objects.filter(id=host_id).delete()

    return HttpResponseRedirect(reverse('host_list'))


@require_role(role='super')
def host_edit_chg_name(request):
    
    idc_id = request.GET.get('idc_id', '')
    item_id = request.GET.get('item_id', '')
    area_id = request.GET.get('area_id', '')
    functs_id = request.GET.get('functs_id', '')
    idcs = get_object(IDC, id=idc_id)
    items = get_object(Items, id=item_id)
    areas = get_object(Areas, id=area_id)
    functss = get_object(Functions, id=functs_id)
    if idcs and items and areas and functss:
        idc = idcs.idcmark
        item = items.itemmark
        area = areas.areamark
        functs = functss.functionmark
        get_all = {'idc':idc, 'item':item, 'area':area, 'functs':functs}
        return HttpResponse(json.dumps(get_all), content_type="application/json")    


@require_role(role='super')
def host_edit(request):
    """
    edit a host
    """
    header_title, path1, path2, path3 = u'编辑主机', u'资源管理', u'编辑主机' , u'主机管理'

    hostasset_id = request.GET.get('id', '') 
    if hostasset_id:   
        username = request.user.username
        hostasset = get_object(HostAsset, id=hostasset_id)
        if hostasset:
            password_old = hostasset.password
        af = HostsForm(instance=hostasset)
        if request.method == 'POST':
            af_post = HostsForm(request.POST, instance=hostasset)
            wan_ip = request.POST.get('wan_ip', '')
            hostname = request.POST.get('hostname', '')
            password = request.POST.get('password', '')
            use_default_auth = request.POST.get('use_default_auth', '')
            try:
                hostasset_test = get_object(HostAsset, hostname=hostname)
                if hostasset_test and hostasset_id != unicode(hostasset_test.id):
                    emg = u'该主机名 %s 已存在!' % hostname
                    raise ServerError(emg)
                if len(hostname) > 128:
                    emg = u'主机名长度不能超过128位!'
                    raise ServerError(emg)
                else:
                    if af_post.is_valid():
                        af_save = af_post.save(commit=False)
                        if use_default_auth:
                            af_save.username = ''
                            af_save.password = ''
                        else:
                            if password:
                                #password_encode = CRYPTOR.encrypt(password)
                                #af_save.password = password_encode
                                af_save.password = password
                            else:
                                af_save.password = password_old
                        af_save.save()
                        af_post.save_m2m()
    
                        #info = hostasset_diff(af_post.__dict__.get('initial'), request.POST)
                        #db_hostasset_alert(hostasset, username, info)
    
                        smg = u'主机 %s 修改成功' % wan_ip
                    else:
                        emg = u'主机 %s 修改失败' % wan_ip
                        raise ServerError(emg)
            except ServerError as e:
                error = e.message
                return my_render('jpyasset/jhost_edit.html', locals(), request)
            return HttpResponseRedirect(reverse('host_detail')+'?id=%s' % hostasset_id)
    
        return my_render('jpyasset/jhost_edit.html', locals(), request)
    else:
        return HttpResponseRedirect(reverse('host_list'))


@require_role(role='super')
def host_cloud_list(request):
    """

    """
    header_title, path1, path2, path3 = u'更新云机', u'项目管理', u'更新云主机', u'主机管理'
    posts = IDC.objects.all()
    keyword = request.GET.get('keyword', '')
    if keyword:
        posts = IDC.objects.filter(
            Q(name__contains=keyword) |
            Q(idcmark__contains=keyword) |
            Q(operator__contains=keyword) |
            Q(comment__contains=keyword))
    else:
        posts = IDC.objects.exclude(name='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('jpyasset/jhost_cloud.html', locals(), request)    
    
    
@require_role(role='super')
def host_cloud_update(request):
    """
    host cloud update view
    """
    cloud_ids = request.GET.get('id', '')
    cloud_yuns = request.GET.get('yun', '')
    print cloud_ids
    print cloud_yuns
    if cloud_ids and cloud_yuns:
        aliyun = re.match('aly\d+', cloud_yuns)
        tenxunyun = re.match('tx\d+', cloud_yuns)        
        cloud_get_data_in(cloud_ids=cloud_ids, cloud_yuns=cloud_yuns)                  
                     
        servers = db_cloud_get_detail(cloud_ids=cloud_ids, cloud_yuns=cloud_yuns)
        old_ip_list = []
        wan_ip_old = HostAsset.objects.all().values('wan_ip')
        for i in wan_ip_old:
            ip = i['wan_ip']
            old_ip_list.append(ip)
        for k in servers.values():
            newip = k['wan_ip']
            lanip = k['lan_ip']
            cpu = k['cpu']
            mem = k['memory']
            if tenxunyun:
                disk = k['disk']['storageSize']
            else:
                disk = None
            cretime = k['cretime']
            exptime = k['exptime']
            imageid = k['imageid']
            banwidth = k['banwidth']
             
            if newip not in old_ip_list:
                #print newip
                hosts = HostAsset.objects.create(hostname=newip,
                                                 wan_ip=newip, 
                                                 lan_ip=lanip, 
                                                 cpu=cpu, 
                                                 memory=mem, 
                                                 disk=disk, 
                                                 cretime=cretime,
                                                 exptime=exptime,
                                                 imageid=imageid,
                                                 banwidth=banwidth,
                                                 date_added=datetime.datetime.now())
                hosts.save()
                
        

    return HttpResponseRedirect(reverse('host_cloud_list'))       
              
    


def net_ip_add(request):
    pass


def net_ip_del(request):
    pass


def net_ip_edit(request):
    pass


def net_ip_list(request):
    pass


def net_resource_add(request):
    pass


def net_resource_del(request):
    pass


def net_resource_edit(request):
    pass


def net_resource_list(request):
    pass


def net_realm_add(request):
    pass


def net_realm_del(request):
    pass


def net_realm_edit(request):
    pass


def net_realm_list(request):
    pass


def storager_cnd_add(request):
    pass


def storager_cnd_del(request):
    pass


def storager_cnd_edit(request):
    pass


def storager_cnd_list(request):
    pass


def storager_cold_add(request):
    pass


def storager_cold_del(request):
    pass


def storager_cold_edit(request):
    pass


def storager_cold_list(request):
    pass


@require_role(role='super')
def idc_add(request):
    """
    IDC add view
    """
    header_title, path1, path2 = u'添加IDC', u'机房管理', u'添加IDC'
    if request.method == 'POST':
        idc_form = IdcForm(request.POST)
        if idc_form.is_valid():
            idc_name = idc_form.cleaned_data['name']

            if IDC.objects.filter(name=idc_name):
                emg = u'添加失败, 此IDC %s 已存在!' % idc_name
                return my_render('jpyasset/idc_add.html', locals(), request)
            else:
                idc_form.save()
                smg = u'IDC: %s添加成功' % idc_name
            return HttpResponseRedirect(reverse('idc_list'))
    else:
        idc_form = IdcForm()
    return my_render('jpyasset/idc_add.html', locals(), request)


@require_role(role='super')
def idc_del(request):
    """
    IDC delete view
    """
    idc_ids = request.GET.get('id', '')
    idc_id_list = idc_ids.split(',')

    for idc_id in idc_id_list:
        IDC.objects.filter(id=idc_id).delete()

    return HttpResponseRedirect(reverse('idc_list'))


@require_role(role='super')
def idc_edit(request):
    """
    IDC edit view
    """
    header_title, path1, path2 = u'编辑IDC', u'机房管理', u'编辑IDC'
    idc_id = request.GET.get('id', '')
    if idc_id:
        idc = get_object(IDC, id=idc_id)
        if request.method == 'POST':
            idc_form = IdcForm(request.POST, instance=idc)
            if idc_form.is_valid():
                idc_form.save()
                return HttpResponseRedirect(reverse('idc_list'))
        else:
            idc_form = IdcForm(instance=idc)
            return my_render('jpyasset/idc_edit.html', locals(), request)
    else:
        return HttpResponseRedirect(reverse('idc_list'))


@require_role(role='super')
def idc_list(request):
    """
    IDC list view
    """
    header_title, path1, path2 = u'查看IDC', u'机房管理', u'查看IDC'
    posts = IDC.objects.all()
    keyword = request.GET.get('keyword', '')
    status = request.GET.get('status', '')
    
    if status:
        posts = IDC.objects.filter(status__contains=status)    
    if keyword:
        posts = IDC.objects.filter(
            Q(name__contains=keyword) |
            Q(idcmark__contains=keyword) |
            Q(linkman__contains=keyword) |
            Q(phone__contains=keyword) |
            Q(operator__contains=keyword) |
            Q(comment__contains=keyword))
    else:
        posts = IDC.objects.exclude(name='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('jpyasset/idc_list.html', locals(), request)


@require_role(role='super')
def item_add(request):
    """
    item add view
    """
    header_title, path1, path2, path3 = u'添加项目', u'项目管理', u'添加项目', u'项目组管理'
    if request.method == 'POST':
        item_form = ItemsForm(request.POST)
        if item_form.is_valid():
            item_name = item_form.cleaned_data['name']

            if Items.objects.filter(name=item_name):
                emg = u'添加失败, 此项目 %s 已存在!' % item_name
                return my_render('jpyasset/item_add.html', locals(), request)
            else:
                item_form.save()
                smg = u'项目: %s添加成功' % item_name
            return HttpResponseRedirect(reverse('item_list'))
    else:
        item_form = ItemsForm()
    return my_render('jpyasset/item_add.html', locals(), request)


@require_role(role='super')
def item_del(request):
    """
    item delete view
    """
    item_ids = request.GET.get('id', '')
    item_id_list = item_ids.split(',')

    for item_id in item_id_list:
        Items.objects.filter(id=item_id).delete()

    return HttpResponseRedirect(reverse('item_list'))


@require_role(role='super')
def item_edit(request):
    """
    item edit view
    """
    header_title, path1, path2, path3 = u'编辑项目', u'项目管理', u'编辑项目', u'项目组管理'
    item_id = request.GET.get('id', '')
    if item_id:
        item = get_object(Items, id=item_id)
        if request.method == 'POST':
            item_form = ItemsForm(request.POST, instance=item)
            if item_form.is_valid():
                item_form.save()
                return HttpResponseRedirect(reverse('item_list'))
        else:
            item_form = ItemsForm(instance=item)
            return my_render('jpyasset/item_edit.html', locals(), request)
    else:
        return HttpResponseRedirect(reverse('item_list'))


@require_role(role='super')
def item_list(request):
    """
    item list view
    """
    header_title, path1, path2, path3 = u'查看项目', u'项目管理', u'查看项目', u'项目组管理'
    posts = Items.objects.all()
    keyword = request.GET.get('keyword', '')
    if keyword:
        posts = Items.objects.filter(
            Q(name__contains=keyword) |
            Q(itemmark__contains=keyword) |
            Q(linkman__contains=keyword) |
            Q(phone__contains=keyword) |
            Q(comment__contains=keyword))
    else:
        posts = Items.objects.exclude(name='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('jpyasset/item_list.html', locals(), request)


@require_role(role='super')
def area_add(request):
    """
    area add view
    """
    header_title, path1, path2, path3 = u'添加区域', u'项目管理', u'添加区域', u'区域组管理'
    if request.method == 'POST':
        area_form = AreasForm(request.POST)
        if area_form.is_valid():
            area_name = area_form.cleaned_data['name']

            if Areas.objects.filter(name=area_name):
                emg = u'添加失败, 此区域%s 已存在!' % area_name
                return my_render('jpyasset/area_add.html', locals(), request)
            else:
                area_form.save()
                smg = u'区域: %s添加成功' % area_name
            return HttpResponseRedirect(reverse('area_list'))
    else:
        area_form = AreasForm()
    return my_render('jpyasset/area_add.html', locals(), request)


@require_role(role='super')
def area_del(request):
    """
    area delete view
    """
    area_ids = request.GET.get('id', '')
    area_id_list = area_ids.split(',')

    for area_id in area_id_list:
        Areas.objects.filter(id=area_id).delete()

    return HttpResponseRedirect(reverse('area_list'))


@require_role(role='super')
def area_edit(request):
    """
    area edit view
    """
    header_title, path1, path2, path3 = u'编辑区域', u'项目管理', u'编辑区域', u'区域组管理'
    area_id = request.GET.get('id', '')
    if area_id:
        area = get_object(Areas, id=area_id)
        if request.method == 'POST':
            area_form = AreasForm(request.POST, instance=area)
            if area_form.is_valid():
                area_form.save()
                return HttpResponseRedirect(reverse('area_list'))
        else:
            area_form = AreasForm(instance=area)
            return my_render('jpyasset/area_edit.html', locals(), request)
    else:
        return HttpResponseRedirect(reverse('area_list'))


@require_role(role='super')
def area_list(request):
    """
    area list view
    """
    header_title, path1, path2, path3 = u'查看区域', u'项目管理', u'查看区域', u'区域组管理'
    posts = Areas.objects.all()
    keyword = request.GET.get('keyword', '')
    if keyword:
        posts = Areas.objects.filter(
            Q(name__contains=keyword) |
            Q(areamark__contains=keyword) |
            Q(nation_type__contains=keyword) |
            Q(comment__contains=keyword))
    else:
        posts = Areas.objects.exclude(name='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('jpyasset/area_list.html', locals(), request)


@require_role(role='super')
def funct_add(request):
    """
    funct add view
    """
    header_title, path1, path2, path3 = u'添加功能', u'项目管理', u'添加功能', u'功能组管理'
    if request.method == 'POST':
        funct_form = FunctionsForm(request.POST)
        if funct_form.is_valid():
            funct_name = funct_form.cleaned_data['name']

            if Functions.objects.filter(name=funct_name):
                emg = u'添加失败, 此功能 %s 已存在!' % funct_name
                return my_render('jpyasset/funct_add.html', locals(), request)
            else:
                funct_form.save()
                smg = u'功能: %s添加成功' % funct_name
            return HttpResponseRedirect(reverse('funct_list'))
    else:
        funct_form = FunctionsForm()
    return my_render('jpyasset/funct_add.html', locals(), request)


@require_role(role='super')
def funct_del(request):
    """
    funct delete view
    """
    funct_ids = request.GET.get('id', '')
    funct_id_list = funct_ids.split(',')

    for funct_id in funct_id_list:
        Functions.objects.filter(id=funct_id).delete()

    return HttpResponseRedirect(reverse('funct_list'))


@require_role(role='super')
def funct_edit(request):
    """
    funct edit view
    """
    header_title, path1, path2, path3 = u'编辑功能', u'项目管理', u'编辑功能', u'功能组管理'
    funct_id = request.GET.get('id', '')
    if funct_id:
        funct = get_object(Functions, id=funct_id)
        if request.method == 'POST':
            funct_form = FunctionsForm(request.POST, instance=funct)
            if funct_form.is_valid():
                funct_form.save()
                return HttpResponseRedirect(reverse('funct_list'))
        else:
            funct_form = FunctionsForm(instance=funct)
            return my_render('jpyasset/funct_edit.html', locals(), request)
    else:
        return HttpResponseRedirect(reverse('funct_list'))


@require_role(role='super')
def funct_list(request):
    """
    funct list view
    """
    header_title, path1, path2, path3 = u'查看功能', u'项目管理', u'查看功能', u'功能组管理'
    posts = Functions.objects.all()
    keyword = request.GET.get('keyword', '')
    if keyword:
        posts = Functions.objects.filter(
            Q(name__contains=keyword) |
            Q(functionmark__contains=keyword) |
            Q(comment__contains=keyword))
    else:
        posts = Functions.objects.exclude(name='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('jpyasset/funct_list.html', locals(), request)


@require_role(role='super')
def osname_add(request):
    """
    osname add view
    """
    header_title, path1, path2, path3 = u'添加系统类型', u'业务管理', u'添加系统类型', u'应用管理'
    if request.method == 'POST':
        osname_form = ServerTypeForm(request.POST)
        if osname_form.is_valid():
            osname_name = osname_form.cleaned_data['name']

            if ServerType.objects.filter(name=osname_name):
                emg = u'添加失败, 此系统类型 %s 已存在!' % osname_name
                return my_render('jpyasset/osname_add.html', locals(), request)
            else:
                osname_form.save()
                smg = u'系统类型: %s添加成功' % osname_name
            return HttpResponseRedirect(reverse('osname_list'))
    else:
        osname_form = ServerTypeForm()
    return my_render('jpyasset/osname_add.html', locals(), request)


@require_role(role='super')
def osname_del(request):
    """
    osname delete view
    """
    osname_ids = request.GET.get('id', '')
    osname_id_list = osname_ids.split(',')

    for osname_id in osname_id_list:
        ServerType.objects.filter(id=osname_id).delete()

    return HttpResponseRedirect(reverse('osname_list'))


@require_role(role='super')
def osname_edit(request):
    """
    osname edit view
    """
    header_title, path1, path2, path3 = u'编辑系统类型', u'业务管理', u'编辑系统类型', u'应用管理'
    osname_id = request.GET.get('id', '')
    if osname_id:
        osname = get_object(ServerType, id=osname_id)
        if request.method == 'POST':
            osname_form = ServerTypeForm(request.POST, instance=osname)
            if osname_form.is_valid():
                osname_form.save()
                return HttpResponseRedirect(reverse('osname_list'))
        else:
            osname_form = ServerTypeForm(instance=osname)
            return my_render('jpyasset/osname_edit.html', locals(), request)
    else:
        return HttpResponseRedirect(reverse('osname_list'))


@require_role(role='super')
def osname_list(request):
    """
    osname list view
    """
    header_title, path1, path2, path3 = u'系统类型', u'项目管理', u'系统类型', u'应用管理'
    posts = ServerType.objects.all()
    keyword = request.GET.get('keyword', '')
    if keyword:
        posts = ServerType.objects.filter(
            Q(name__contains=keyword) |
            Q(vers__contains=keyword) |
            Q(comment__contains=keyword))
    else:
        posts = ServerType.objects.exclude(name='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('jpyasset/osname_list.html', locals(), request)


@require_role(role='super')
def appvl_add(request):
    """
    appvl add view
    """
    header_title, path1, path2, path3 = u'添加应用名称', u'业务管理', u'添加应用名称', u'应用管理'
    if request.method == 'POST':
        appvl_form = ApplyVocationalForm(request.POST)
        if appvl_form.is_valid():
            appvl_name = appvl_form.cleaned_data['name']

            if ApplyVocational.objects.filter(name=appvl_name):
                emg = u'添加失败, 此应用名称 %s 已存在!' % appvl_name
                return my_render('jpyasset/appvl_add.html', locals(), request)
            else:
                appvl_form.save()
                smg = u'应用名称: %s添加成功' % appvl_name
            return HttpResponseRedirect(reverse('appvl_list'))
    else:
        appvl_form = ApplyVocationalForm()
    return my_render('jpyasset/appvl_add.html', locals(), request)


@require_role(role='super')
def appvl_del(request):
    """
    appvl delete view
    """
    appvl_ids = request.GET.get('id', '')
    appvl_id_list = appvl_ids.split(',')

    for appvl_id in appvl_id_list:
        ApplyVocational.objects.filter(id=appvl_id).delete()

    return HttpResponseRedirect(reverse('appvl_list'))


@require_role(role='super')
def appvl_edit(request):
    """
    appvl edit view
    """
    header_title, path1, path2, path3 = u'编辑应用名称', u'业务管理', u'编辑应用名称', u'应用管理'
    appvl_id = request.GET.get('id', '')
    if appvl_id:
        appvl = get_object(ApplyVocational, id=appvl_id)
        if request.method == 'POST':
            appvl_form = ApplyVocationalForm(request.POST, instance=appvl)
            if appvl_form.is_valid():
                appvl_form.save()
                return HttpResponseRedirect(reverse('appvl_list'))
        else:
            appvl_form = ApplyVocationalForm(instance=appvl)
            return my_render('jpyasset/appvl_edit.html', locals(), request)
    else:
        return HttpResponseRedirect(reverse('appvl_list'))


@require_role(role='super')
def appvl_list(request):
    """
    appvl list view
    """
    header_title, path1, path2, path3 = u'应用名称', u'项目管理', u'应用名称', u'应用管理'
    posts = ApplyVocational.objects.all()
    keyword = request.GET.get('keyword', '')
    if keyword:
        posts = ApplyVocational.objects.filter(
            Q(name__contains=keyword) |
            Q(applymark__contains=keyword) |
            Q(comment__contains=keyword))
    else:
        posts = ApplyVocational.objects.exclude(name='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('jpyasset/appvl_list.html', locals(), request)


@require_role(role='super')
def filevl_add(request):
    """
    filevl add view
    """
    header_title, path1, path2, path3 = u'添加应用文件', u'业务管理', u'添加应用文件', u'应用管理'
    if request.method == 'POST':
        filevl_form = ApplyFileForm(request.POST, request.FILES)
        if filevl_form.is_valid():
            filevl_name = filevl_form.cleaned_data['name']
            appfiles = filevl_form.cleaned_data['appfile']
            applyfile = ApplyFile()
            applyfile.appfile = appfiles
            appfilename = ApplyFile.objects.filter(name=filevl_name)
            appfilefile = ApplyFile.objects.filter(appfile__contains=appfiles)

            if appfilename or appfilefile:
                if appfilename:
                    emg = u'添加失败, 此应用文件名 %s 已存在!' % filevl_name
                elif appfilefile:
                    emg = u'添加失败, 此应用文件 %s 已存在!' % appfiles
                return my_render('jpyasset/filevl_add.html', locals(), request)
            else:
                filevl_form.save()
                smg = u'应用文件: %s添加成功' % filevl_name
            return HttpResponseRedirect(reverse('filevl_list'))
    else:
        filevl_form = ApplyFileForm()
    return my_render('jpyasset/filevl_add.html', locals(), request)


@require_role(role='super')
def filevl_del(request):
    """
    filevl delete view
    """
    filevl_ids = request.GET.get('id', '')
    filevl_id_list = filevl_ids.split(',')

    for filevl_id in filevl_id_list:
        appfiles = ApplyFile.objects.filter(id=filevl_id).values()
        db_filedir = appfiles[0]['appfile']
        filedir = '/'.join([MEDIA_ROOT, db_filedir])
        if os.path.exists(filedir):
            os.remove(filedir)
            ApplyFile.objects.filter(id=filevl_id).delete()

    return HttpResponseRedirect(reverse('filevl_list'))


@require_role(role='super')
def filevl_edit(request):
    """
    filevl edit view
    """
    header_title, path1, path2, path3 = u'编辑应用文件', u'业务管理', u'编辑应用文件', u'应用管理'
    filevl_id = request.GET.get('id', '')
    if filevl_id:
        filevl = get_object(ApplyFile, id=filevl_id)
        if request.method == 'POST':
            filevl_form = ApplyFileForm(request.POST, request.FILES, instance=filevl)
            ck_file = request.FILES
            if filevl_form.is_valid():
                filevl_name = filevl_form.cleaned_data['name']
                appfiles = filevl_form.cleaned_data['appfile']
                applyfile = ApplyFile()
                applyfile.appfile = appfiles
                appfilename = ApplyFile.objects.filter(name=filevl_name)
                appfilefile = ApplyFile.objects.filter(appfile__contains=appfiles).values()
                db_filedir = appfilefile[0]['appfile']
                filedir = '/'.join([MEDIA_ROOT, db_filedir])
                    
                if len(ck_file) == 1:
                    if appfilename or filedir:
                        if os.path.exists(filedir):
                            os.remove(filedir)
                        
                filevl_form.save()
                return HttpResponseRedirect(reverse('filevl_list'))
        else:
            filevl_form = ApplyFileForm(instance=filevl)
            return my_render('jpyasset/filevl_edit.html', locals(), request)
    else:
        return HttpResponseRedirect(reverse('filevl_list'))


@require_role(role='super')
def filevl_list(request):
    """
    filevl list view
    """
    header_title, path1, path2, path3 = u'应用文件', u'项目管理', u'应用文件', u'应用管理'
    posts = ApplyFile.objects.all()
    keyword = request.GET.get('keyword', '')
    conf_id = request.GET.get('confid', '')
    if keyword:
        posts = ApplyFile.objects.filter(
            Q(name__contains=keyword) |
            Q(functionmark__contains=keyword) |
            Q(comment__contains=keyword))
    elif conf_id:
        confvl = ConfigVocational.objects.get(id=conf_id)
        posts = confvl.configfile.all()
    else:
        posts = ApplyFile.objects.exclude(name='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('jpyasset/filevl_list.html', locals(), request)


@require_role(role='super')
def confvl_add(request):
    """
    confvl add view 
    """
    error = ''
    msg = ''
    header_title, path1, path2, path3 = u'添加配置', u'业务管理', u'添加配置', u'配置管理'
    file_all = ApplyFile.objects.all()
    af = ConfigVocationalForm()

    if request.method == 'POST':
        conf_name = request.POST.get('conf_name', '')
        conf_configmark = request.POST.get('configmark', '')
        files_selected = request.POST.getlist('files_selected', '')
              
        try:
            if not conf_name:
                error = u'配置名 不能为空'
                raise ServerError(error)
            elif not conf_configmark:
                error = u'配置代号 不能为空'
                raise ServerError(error)                

            if ConfigVocational.objects.filter(name=conf_name):
                error = u'配置名 %s 已存在' % conf_name
                raise ServerError(error)
            elif ConfigVocational.objects.filter(configmark=conf_configmark):
                error = u'配置代号 %s 已存在' % conf_configmark
                raise ServerError(error)
            db_add_conf(name=conf_name, configmark=conf_configmark, files_id=files_selected)
            confvl = get_object(ConfigVocational, name=conf_name)
            if confvl:
                confvl_form = ConfigVocationalForm(request.POST, instance=confvl)            
                if confvl_form.is_valid():
                    confvl_form.save()
                    msg = u'添加配置  %s 成功' % conf_name
                    return HttpResponseRedirect(reverse('confvl_list'))
                else:
                    esg = u'添加配置  %s 失败' % conf_name            

        except ServerError:
            pass
        except TypeError:
            error = u'添加配置失败'
        else:
            msg = u'添加配置  %s 成功' % conf_name

    return my_render('jpyasset/confvl_add.html', locals(), request)


@require_role(role='super')
def confvl_del(request):
    """
    del a confvl
    """
    conf_ids = request.GET.get('id', '')
    conf_id_list = conf_ids.split(',')
    for conf_id in conf_id_list:
        conf_file_data = get_object_or_404(ConfigVocational, id=conf_id)            
        filedata = conf_file_data.configfile.all()
        for k in filedata:
            conf_file_data.configfile.remove(k)
        ConfigVocational.objects.filter(id=conf_id).delete()
        
#         try:
#             ConfigVocational.objects.filter(id=conf_id).delete()
#         except Exception, e:
#             print e
#         print "is ok"

    return HttpResponse("删除成功")


@require_role(role='super')
def confvl_edit(request):
    error = ''
    msg = ''
    header_title, path1, path2, path3 = u'编辑配置', u'业务管理', u'编辑配置', u'配置管理'

    conf_id = request.GET.get('id', '')
    if conf_id:
        file_conf = ConfigVocational.objects.get(id=conf_id)
        files_selected = file_conf.configfile.all()
        file_list = []
        for i in files_selected:
            file_list.append(i)
        
        files_remain = ApplyFile.objects.filter(~Q(name__in=file_list))
       
        af = ConfigVocationalForm(instance=file_conf)
    
        if request.method == 'POST':
            conf_name = request.POST.get('conf_name', '')
            conf_configmark = request.POST.get('configmark', '')
            conf_files_selected_id = request.POST.getlist('files_selected')
            conf_files_del_id = request.POST.getlist('files')
            conf_file = get_object(ConfigVocational, id=conf_id)
     
            try:
                if '' in [conf_id, conf_name]:
                    raise ServerError('配置名和配置代号不能为空')
                if len(ConfigVocational.objects.filter(name=conf_name)) > 1:
                    raise ServerError(u'%s 配置名已存在' % conf_name)
                elif len(ConfigVocational.objects.filter(configmark=conf_configmark)) > 1:
                    raise ServerError(u'%s 配置代号已存在' % conf_configmark)
                # add file conf
                                    
                for k in conf_files_del_id:
                    conf_file_data = get_object_or_404(ConfigVocational, id=conf_id)
                    file_date = get_object_or_404(ApplyFile, id=k)                
                    conf_file_data.configfile.remove(file_date)         
                                  
                for fileobj in ApplyFile.objects.filter(id__in=conf_files_selected_id):
                    fileobj.configvocational_set.add(file_conf)
     
                file_conf.name = conf_name
                file_conf.configmark = conf_configmark
                file_conf.save()
                
                if conf_file:
                    af_post = ConfigVocationalForm(request.POST, instance=conf_file)
                    if af_post.is_valid():
                        af_post.save()
                        msg = u' %s 配置修改成功' % conf_name
                    else:
                        esg = u' %s 配置修改失败' % conf_name               
            except ServerError, e:
                error = e
    
            if not error:
                return HttpResponseRedirect(reverse('confvl_list'))
    
        return my_render('jpyasset/confvl_edit.html', locals(), request)
    else:
        return HttpResponseRedirect(reverse('confvl_list'))


@require_role(role='super')
def confvl_list(request):
    """
    confvl list views
    """
    header_title, path1, path2, path3 = u'查看配置', u'业务管理', u'查看配置', u'配置管理'
    keyword = request.GET.get('search', '')
    file_confvl_list = ConfigVocational.objects.all().order_by('name')
    conf_id = request.GET.get('id', '')

    if keyword:
        file_confvl_list = file_confvl_list.filter(
                            Q(name__icontains=keyword) |
                            Q(configmark__icontains=keyword) |
                            Q(comment__icontains=keyword))
        if not file_confvl_list:
            idc_name = IDC.objects.filter(Q(name__contains=keyword))
            item_name = Items.objects.filter(Q(name__contains=keyword))
            area_name = Areas.objects.filter(Q(name__contains=keyword))
            functs_name = Functions.objects.filter(Q(name__contains=keyword))
            for tpy in TOOLS_TYPE:
                tools_name = tpy[1]
                if keyword == tools_name:
                    tools_id = tpy[0]
                    file_confvl_list = ConfigVocational.objects.filter(tools_type=tools_id)
            
            if idc_name:
                file_confvl_list = ConfigVocational.objects.filter(idc=idc_name)
            elif item_name:
                file_confvl_list = ConfigVocational.objects.filter(item=item_name)
            elif area_name:
                file_confvl_list = ConfigVocational.objects.filter(area=area_name)
            elif functs_name:
                file_confvl_list = ConfigVocational.objects.filter(functs=functs_name)
            else:
                file_confvl_list = ConfigVocational.objects.exclude(name='ALL').order_by('id')            

    if conf_id:
        file_confvl_list = file_confvl_list.filter(id=int(conf_id))

    file_confvl_list, p, file_confvls, page_range, current_page, show_first, show_end = pages(file_confvl_list, request)
    return my_render('jpyasset/confvl_list.html', locals(), request)


@require_role(role='super')
def conftaskname_add(request):
    """
    conf task name add view
    """
    header_title, path1, path2, path3 = u'添加配置任务名称', u'业务管理', u'添加配置任务名称', u'配置管理'
    if request.method == 'POST':
        taskname_form = TaskNameForm(request.POST)
        if taskname_form.is_valid():
            task_name = taskname_form.cleaned_data['name']

            if TaskName.objects.filter(name=task_name):
                emg = u'添加失败, 此配置任务名称 %s 已存在!' % task_name
                return my_render('jpyasset/conftaskname_add.html', locals(), request)
            else:
                taskname_form.save()
                smg = u'配置任务名: %s添加成功' % task_name
            return HttpResponseRedirect(reverse('conftaskname_list'))
    else:
        taskname_form = TaskNameForm()
    return my_render('jpyasset/conftaskname_add.html', locals(), request)


@require_role(role='super')
def conftaskname_del(request):
    """
    conf task name delete view
    """
    taskname_ids = request.GET.get('id', '')
    taskname_id_list = taskname_ids.split(',')

    for taskname_id in taskname_id_list:
        TaskName.objects.filter(id=taskname_id).delete()

    return HttpResponseRedirect(reverse('conftaskname_list'))


@require_role(role='super')
def conftaskname_edit(request):
    """
    conf task name edit view
    """
    header_title, path1, path2, path3 = u'编辑配置任务名称', u'业务管理', u'编辑配置任务名称', u'配置管理'
    taskname_id = request.GET.get('id', '')
    if taskname_id:
        taskname = get_object(TaskName, id=taskname_id)
        if request.method == 'POST':
            taskname_form = TaskNameForm(request.POST, instance=taskname)
            if taskname_form.is_valid():
                taskname_form.save()
                return HttpResponseRedirect(reverse('conftaskname_list'))
        else:
            taskname_form = TaskNameForm(instance=taskname)
            return my_render('jpyasset/conftaskname_edit.html', locals(), request)
    else:
        return HttpResponseRedirect(reverse('conftaskname_list'))


@require_role(role='super')
def conftaskname_list(request):
    """
    conf task name list view
    """
    header_title, path1, path2, path3 = u'配置任务名称', u'项目管理', u'配置任务名称', u'配置管理'
    posts = TaskName.objects.all()
    keyword = request.GET.get('keyword', '')
    if keyword:
        posts = TaskName.objects.filter(
            Q(name__contains=keyword) |
            Q(comment__contains=keyword))
    else:
        posts = TaskName.objects.exclude(name='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('jpyasset/conftaskname_list.html', locals(), request)


@require_role(role='super')
def conftaskset_add(request):
    """
    conf task set add view
    """
    header_title, path1, path2, path3 = u'添加配置任务设置', u'业务管理', u'添加配置任务设置', u'配置管理'
    if request.method == 'POST':
        taskset_form = ConfigPlanTaskForm(request.POST)
        if taskset_form.is_valid():
            taskset_form.save()
            return HttpResponseRedirect(reverse('conftaskset_list'))
    else:
        taskset_form = ConfigPlanTaskForm()
    return my_render('jpyasset/conftaskset_add.html', locals(), request)


@require_role(role='super')
def conftaskset_del(request):
    """
    conf task set delete view
    """
    taskset_ids = request.GET.get('id', '')
    taskset_id_list = taskset_ids.split(',')

    for taskset_id in taskset_id_list:
        ConfigPlanTask.objects.filter(id=taskset_id).delete()

    return HttpResponseRedirect(reverse('conftaskset_list'))


@require_role(role='super')
def conftaskset_edit(request):
    """
    conf task set edit view
    """
    header_title, path1, path2, path3 = u'编辑配置任务设置', u'业务管理', u'编辑配置任务设置', u'配置管理'
    taskset_id = request.GET.get('id', '')
    if taskset_id:
        taskset = get_object(ConfigPlanTask, id=taskset_id)
        if request.method == 'POST':
            taskset_form = ConfigPlanTaskForm(request.POST, instance=taskset)
            if taskset_form.is_valid():
                taskset_form.save()
                return HttpResponseRedirect(reverse('conftaskset_list'))
        else:
            taskset_form = ConfigPlanTaskForm(instance=taskset)
            return my_render('jpyasset/conftaskset_edit.html', locals(), request)
    else:
        return HttpResponseRedirect(reverse('conftaskset_list'))


@require_role(role='super')
def conftaskset_list(request):
    """
    conf task set list view
    """
    header_title, path1, path2, path3 = u'配置任务设置', u'项目管理', u'配置任务设置', u'配置管理'
    posts = ConfigPlanTask.objects.all()
    keyword = request.GET.get('keyword', '')
    if keyword:
        posts = ConfigPlanTask.objects.filter(
            Q(comment__contains=keyword))
        if not posts:
            taskname = TaskName.objects.filter(Q(name__contains=keyword))
            servername = ApplyVocational.objects.filter(Q(name__contains=keyword))
            confname = ConfigVocational.objects.filter(Q(name__contains=keyword))
            for tkstep in CONF_STEP:
                step_name = tkstep[1]
                if keyword == step_name:
                    step_id = tkstep[0]
                    posts = ConfigPlanTask.objects.filter(confstep=step_id)            
            if taskname:
                posts = ConfigPlanTask.objects.filter(name=taskname)
            elif servername:
                posts = ConfigPlanTask.objects.filter(servername=servername)
            elif confname:
                posts = ConfigPlanTask.objects.filter(confname=confname)
            else:
                posts = ConfigPlanTask.objects.exclude(comment='ALL').order_by('id')   
    else:
        posts = ConfigPlanTask.objects.exclude(comment='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('jpyasset/conftaskset_list.html', locals(), request)


@require_role(role='super')
def vervl_add(request):
    pass


@require_role(role='super')
def vervl_del(request):
    pass


@require_role(role='super')
def vervl_edit(request):
    pass


@require_role(role='super')
def vervl_list(request):
    pass


@require_role(role='super')
def planvl_add(request):
    """
    planvl add view 
    """
    error = ''
    msg = ''
    header_title, path1, path2, path3 = u'添加方案', u'业务管理', u'添加方案', u'方案管理'
    plantask_all = ConfigPlanTask.objects.all()
    af = PlanVocationalForm()

    if request.method == 'POST':
        plan_name = request.POST.get('plan_name', '')
        plan_planmark = request.POST.get('planmark', '')
        plans_selected = request.POST.getlist('plans_selected', '')
              
        try:
            if not plan_name:
                error = u'方案名 不能为空'
                raise ServerError(error)
            elif not plan_planmark:
                error = u'方案代号 不能为空'
                raise ServerError(error)                

            if PlanVocational.objects.filter(name=plan_name):
                error = u'方案名 %s 已存在' % plan_name
                raise ServerError(error)
            elif PlanVocational.objects.filter(planmark=plan_planmark):
                error = u'方案代号 %s 已存在' % plan_planmark
                raise ServerError(error)
            db_add_plan(name=plan_name, planmark=plan_planmark, cpts_id=plans_selected)
            planvl = get_object(PlanVocational, name=plan_name)
            if planvl:
                planvl_form = PlanVocationalForm(request.POST, instance=planvl)            
                if planvl_form.is_valid():
                    planvl_form.save()
                    msg = u'添加方案  %s 成功' % plan_name
                    return HttpResponseRedirect(reverse('planvl_list'))
                else:
                    esg = u'添加方案 %s 失败' % plan_name            

        except ServerError:
            pass
        except TypeError:
            error = u'添加方案失败'
        else:
            msg = u'添加方案  %s 成功' % plan_name

    return my_render('jpyasset/planvl_add.html', locals(), request)


@require_role(role='super')
def planvl_del(request):
    """
    planvl delete view
    """
    plan_ids = request.GET.get('id', '')
    plan_id_list = plan_ids.split(',')
    for plan_id in plan_id_list:
        plan_data = get_object_or_404(PlanVocational, id=plan_id)            
        conftaskdata = plan_data.configset.all()
        for k in conftaskdata:
            plan_data.configset.remove(k)
        PlanVocational.objects.filter(id=plan_id).delete()
        
    return HttpResponse("删除成功")


@require_role(role='super')
def planvl_edit(request):
    pass


@require_role(role='super')
def planvl_list(request):
    """
    planvl list view
    """
    header_title, path1, path2, path3 = u'查看方案', u'业务管理', u'查看方案', u'方案管理'
    keyword = request.GET.get('search', '')
    planvl_list = PlanVocational.objects.all().order_by('name')
    plan_id = request.GET.get('id', '')

    if keyword:
        planvl_list = planvl_list.filter(
                            Q(name__icontains=keyword) |
                            Q(planmark__icontains=keyword) |
                            Q(comment__icontains=keyword))
        if not planvl_list:
            idc_name = IDC.objects.filter(Q(name__contains=keyword))
            item_name = Items.objects.filter(Q(name__contains=keyword))
            area_name = Areas.objects.filter(Q(name__contains=keyword))
            functs_name = Functions.objects.filter(Q(name__contains=keyword))
            
            if idc_name:
                planvl_list = PlanVocational.objects.filter(idc=idc_name)
            elif item_name:
                planvl_list = PlanVocational.objects.filter(item=item_name)
            elif area_name:
                planvl_list = PlanVocational.objects.filter(area=area_name)
            elif functs_name:
                planvl_list = PlanVocational.objects.filter(functs=functs_name)
            else:
                planvl_list = PlanVocational.objects.exclude(name='ALL').order_by('id')            

    if plan_id:
        planvl_list = planvl_list.filter(id=int(plan_id))

    planvl_list, p, planvls, page_range, current_page, show_first, show_end = pages(planvl_list, request)
    return my_render('jpyasset/planvl_list.html', locals(), request)













































































































































