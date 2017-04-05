#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from jpy001.settings import MEDIA_ROOT

IDC_TYPE = (
    (1, u"云服务"),
    (2, u"物理服务")
    )

class IDC(models.Model):
    name = models.CharField(max_length=32, verbose_name=u'机房名称')
    idcmark = models.CharField(max_length=16, unique=True, verbose_name=u'机房代号')
    linkman = models.CharField(max_length=16, blank=True, null=True, default='', verbose_name=u'联系人')
    phone = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name=u'联系电话')
    cloudid = models.CharField(max_length=255, blank=True, null=True, default='', verbose_name=u'云SecretId')
    cloudkey = models.CharField(max_length=255, blank=True, null=True, default='', verbose_name=u'云SecretKey')
    cloudregid = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name=u'云所属区域')
    idc_type = models.IntegerField(choices=IDC_TYPE, blank=True, null=True, verbose_name=u"区域类型")    
    date_added = models.DateTimeField(auto_now=True)
    operator = models.CharField(max_length=32, blank=True, default='', null=True, verbose_name=u"运营商")
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name


class Items(models.Model):
    name = models.CharField(max_length=32, verbose_name=u'项目名称')
    itemmark = models.CharField(max_length=16, unique=True, verbose_name=u'项目代号')
    linkman = models.CharField(max_length=16, blank=True, null=True, default='', verbose_name=u'项目负责人')
    phone = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name=u'负责人电话')
    date_added = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name
    

NATION_TYPE = (
    ("China", "China"),
    ("Foreign", "Foreign")
    )

class Areas(models.Model):
    name = models.CharField(max_length=32, verbose_name=u'区域名称')
    areamark = models.CharField(max_length=16, unique=True, verbose_name=u'区域代号')
    nation_type = models.CharField(choices=NATION_TYPE, max_length=32, default="China", verbose_name=u"区域类型")
    date_added = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name
    

class Functions(models.Model):
    name = models.CharField(max_length=32, verbose_name=u'功能名称')
    functionmark = models.CharField(max_length=16, unique=True, verbose_name=u'功能代号')
    date_added = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name


class ServerType(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=u'系统名称')
    vers = models.CharField(max_length=32, verbose_name=u'系统版本')
    date_added = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")

    def __unicode__(self):
        return self.name
    

class ApplyVocational(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=u'应用名称')
    applymark = models.CharField(max_length=32, verbose_name=u'应用代号')
    date_added = models.DateTimeField(auto_now=True)    
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name


APPLY_TYPE_DIR = {1:'sys', 2:'app'}

def get_upload_to(instance, fielname):
    apptype = instance.apply_type
    if apptype:
        typedir = APPLY_TYPE_DIR[apptype]
    else:
        typedir = 'upload'
    return '/'.join([typedir, instance.servername.name, fielname])

APPLY_TYPE = (
    (1, "系统服务"),
    (2, "程序服务") 
    )
class ApplyFile(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'应用文件名称')
    appfile = models.FileField(upload_to=get_upload_to, verbose_name=u'应用文件')
    apply_type = models.IntegerField(choices=APPLY_TYPE, blank=True, verbose_name=u"应用服务类型")
    date_added = models.DateTimeField(auto_now=True)    
    appvers = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"版本号")
    servername = models.ForeignKey("ApplyVocational", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'应用名称')
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name
    

TOOLS_TYPE = (
    (1, "ansible"),
    (2, "saltstack"),
    (3, "jenkins")    
    )
class ConfigVocational(models.Model):
    name = models.CharField(max_length=128, verbose_name=u'业务配置名称')
    configmark = models.CharField(max_length=64, verbose_name=u'业务配置代号')
    servername = models.ForeignKey("ApplyVocational", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'应用名称')    
    configfile = models.ManyToManyField("ApplyFile", blank=True, null=True, verbose_name=u"应用文件")
    tools_type = models.IntegerField(choices=TOOLS_TYPE, blank=True, default=1, verbose_name=u"工具格式类型")
    idc = models.ForeignKey("IDC", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'机房')
    item = models.ForeignKey("Items", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'项目')
    area = models.ForeignKey("Areas", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'区域')
    functs = models.ForeignKey("Functions", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'功能')    
    ostype = models.ForeignKey("ServerType", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'操作系统')    
    date_added = models.DateTimeField(auto_now=True)    
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name
    

class VersionVocational(models.Model):
    versionpath = models.CharField(max_length=255, verbose_name=u'版本配置路径')
    name = models.CharField(max_length=32, verbose_name=u'版本名称')
    versionmark = models.CharField(max_length=16, verbose_name=u'版本号')
    idc = models.ForeignKey("IDC", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'机房')
    item = models.ForeignKey("Items", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'项目')
    area = models.ForeignKey("Areas", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'区域')
    functs = models.ForeignKey("Functions", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'功能')    
    date_added = models.DateTimeField(auto_now=True)    
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name


class TaskName(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"配置任务名称")
    confstep = models.PositiveSmallIntegerField(blank=True, null=True, default=1, verbose_name=u"步骤计数")
    date_added = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name    


CONF_STEP = (
    (1, "第一步"),
    (2, "第二步"),
    (3, "第三步"),   
    (4, "第四步"),   
    (5, "第五步"),   
    (6, "第六步"),   
    (7, "第七步"),   
    (8, "第八步"),   
    (9, "第九步"),   
    (10, "第十步")   
    )    
class ConfigPlanTask(models.Model):
    name = models.ForeignKey("TaskName", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u"配置任务名称")
    servername = models.ForeignKey("ApplyVocational", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'应用名称')
    confname = models.ForeignKey("ConfigVocational", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'业务配置')
    confstep = models.IntegerField(choices=CONF_STEP, blank=True, default=1, verbose_name=u"步骤计数")
    date_added = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name.name   


class PlanVocational(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'方案名称')
    planmark = models.CharField(max_length=32, unique=True, verbose_name=u'方案代号')
    idc = models.ForeignKey("IDC", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'机房')
    item = models.ForeignKey("Items", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'项目')
    area = models.ForeignKey("Areas", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'区域')
    functs = models.ForeignKey("Functions", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'功能')
    configset = models.ManyToManyField("ConfigPlanTask", blank=True, null=True, verbose_name=u'配置任务')    
    date_added = models.DateTimeField(auto_now=True)    
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name
    

ASSET_STATUS = (
    (1, u"已使用"),
    (2, u"未使用"),
    (3, u"报废")
    )
class HostAsset(models.Model):
    wan_ip = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"外网IP")
    lan_ip = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"内网IP")
    other_ip = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"其他IP")
    hostname = models.CharField(unique=True, max_length=128, verbose_name=u"主机名")
    username = models.CharField(max_length=16, blank=True, null=True, default='root', verbose_name=u"管理用户名")
    password = models.CharField(max_length=256, blank=True, null=True, verbose_name=u"密码")
    port = models.IntegerField(blank=True, null=True, default=22, verbose_name=u"端口号")    
    cpu = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'CPU')
    memory = models.CharField(max_length=128, blank=True, null=True, verbose_name=u'内存')
    disk = models.CharField(max_length=1024, blank=True, null=True, verbose_name=u'硬盘')
    mac = models.CharField(max_length=20, blank=True, null=True, verbose_name=u"MAC地址")
    cretime = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"云创建时间")
    exptime = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"云到期时间")
    imageid = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"云系统镜像")
    banwidth = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"云网络带宽")
    system_type = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"系统类型")
    system_version = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"系统版本号")
    number = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=u'主机编号')    
    date_added = models.DateTimeField(auto_now=True)
    idc = models.ForeignKey("IDC", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'机房')
    item = models.ForeignKey("Items", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'项目')
    area = models.ForeignKey("Areas", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'区域')
    functs = models.ForeignKey("Functions", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'功能')
    plan = models.ForeignKey("PlanVocational", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'方案')
    status = models.IntegerField(choices=ASSET_STATUS, blank=True, null=True, default=2, verbose_name=u"机器状态")
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.wan_ip
        

CLOUDRD_STATUS = (
    (1, u"更新成功"),
    (2, u"更新失败"),
    )

class CloudRecord(models.Model):
    idc = models.ForeignKey("IDC", blank=True, null=True,  on_delete=models.SET_NULL, verbose_name=u'机房')
    assetcloud = models.TextField(blank=True, null=True)
    wordkey = models.TextField(blank=True, null=True)
    update_time = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=CLOUDRD_STATUS, blank=True, null=True, verbose_name=u"机器状态")

    def __unicode__(self):
        return self.assetcloud
    
    
class IpAsset(models.Model):
    ip = models.CharField(max_length=32, verbose_name=u"IP")
    name = models.CharField(max_length=32, verbose_name=u'IP名称')
    ipmark = models.CharField(max_length=16, verbose_name=u'IP代号')
    date_added = models.DateTimeField(auto_now=True)    
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.ip
    
    
class NetAsset(models.Model):
    netaddress = models.CharField(max_length=255, verbose_name=u'网络资源地址')
    name = models.CharField(max_length=32, verbose_name=u'网络资源名称')
    netmark = models.CharField(max_length=16, verbose_name=u'网络资源代号')
    date_added = models.DateTimeField(auto_now=True)    
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name
    

class StoragerAsset(models.Model):
    staaddress = models.CharField(max_length=255, verbose_name=u'存储地址')
    name = models.CharField(max_length=32, verbose_name=u'存储资源名称')
    storagermark = models.CharField(max_length=16, verbose_name=u'存储资源代号')
    date_added = models.DateTimeField(auto_now=True)    
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name
    

class RealmName(models.Model):
    rlmaddress = models.CharField(max_length=255, verbose_name=u'域名地址')
    name = models.CharField(max_length=32, verbose_name=u'域名资源名称')
    realmmark = models.CharField(max_length=16, verbose_name=u'域名资源代号')
    date_added = models.DateTimeField(auto_now=True)    
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    
    def __unicode__(self):
        return self.name
     

class AssetPerm(models.Model):
    pass