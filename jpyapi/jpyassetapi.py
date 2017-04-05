#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import xlrd
import xlsxwriter
import json
import time
import re
from django.db.models import AutoField
from jpyasset.models import ASSET_STATUS, IDC, HostAsset, CloudRecord, ApplyFile, ConfigVocational
from jpyapi.jpy001api import *
#from jpy001.templatetags.mytags import get_disk_info
from jpyapi.jpycloudapi import ALiYunApi, TenXunYunCvm




def get_tuple_name(asset_tuple, value):
    """"""
    for t in asset_tuple:
        if t[0] == value:
            return t[1]

    return ''


def get_tuple_diff(asset_tuple, field_name, value):
    """"""
    old_name = get_tuple_name(asset_tuple, int(value[0])) if value[0] else u''
    new_name = get_tuple_name(asset_tuple, int(value[1])) if value[1] else u''
    alert_info = [field_name, old_name, new_name]
    return alert_info



def hostasset_diff(before, after):
    """
    hostasset change before and after
    """
    alter_dic = {}
    before_dic, after_dic = before, dict(after.iterlists())
    for k, v in before_dic.items():
        after_dic_values = after_dic.get(k, [])
        if k == 'group':
            after_dic_value = after_dic_values if len(after_dic_values) > 0 else u''
            uv = v if v is not None else u''
        else:
            after_dic_value = after_dic_values[0] if len(after_dic_values) > 0 else u''
            uv = unicode(v) if v is not None else u''
        if uv != after_dic_value:
            alter_dic.update({k: [uv, after_dic_value]})

    for k, v in alter_dic.items():
        if v == [None, u'']:
            alter_dic.pop(k)

    return alter_dic

def hostasset_diff_one(before, after):
    print before.__dict__, after.__dict__
    fields = HostAsset._meta.get_all_field_names()
    for field in fields:
        print before.field, after.field


def db_hostasset_alert(hostasset, username, alert_dic):
    """
    hostasset alert info to db
    """
    alert_list = []
    asset_tuple_dic = {'status': ASSET_STATUS}
    for field, value in alert_dic.iteritems():
        field_name = HostAsset._meta.get_field_by_name(field)[0].verbose_name
        if field == 'idc':
            old = IDC.objects.filter(id=value[0]) if value[0] else u''
            new = IDC.objects.filter(id=value[1]) if value[1] else u''
            old_name = old[0].name if old else u''
            new_name = new[0].name if new else u''
            alert_info = [field_name, old_name, new_name]

        elif field == 'status':
            alert_info = get_tuple_diff(asset_tuple_dic.get(field), field_name, value)


        elif field == 'use_default_auth':
            if unicode(value[0]) == 'True' and unicode(value[1]) == 'on' or \
                                    unicode(value[0]) == 'False' and unicode(value[1]) == '':
                continue
            else:
                name = hostasset.username
                alert_info = [field_name, u'默认', name] if unicode(value[0]) == 'True' else \
                    [field_name, name, u'默认']

        elif field in ['username', 'password']:
            continue

        else:
            alert_info = [field_name, unicode(value[0]), unicode(value[1])]

        if 'alert_info' in dir():
            alert_list.append(alert_info)


def get_enumerate_data(**kwargs):
    '''
        get cloud record data enumerate
    '''
    datas = kwargs.get('datas')
    keyvals = kwargs.get('keylists')
    servers_list = {}
    ip_word = []
    if datas and keyvals:
        for i,datas in enumerate(datas):
            m,k = i,datas
            xlh = m + 1
            if len(keyvals) == 1:
                for fids,vals in keyvals.items():
                    if len(vals) == 1:
                        ip_word.append(k[vals[0]])
                    elif len(vals) == 2:
                        ip_word.append(k[vals[0]][vals[1]])
                    elif len(vals) == 3:
                        ip_word.append(k[vals[0]][vals[1]][vals[2]])                           
            else: 
                server_detail = {}
                for fids,vals in keyvals.items():
                    if len(vals) == 1:
                        server_detail[fids] = k[vals[0]]
                    elif len(vals) == 2:
                        server_detail[fids] = k[vals[0]][vals[1]]
                    elif len(vals) == 3:
                        server_detail[fids] = k[vals[0]][vals[1]][vals[2]]
                
                servers_list[xlh] = server_detail

        if len(servers_list.values()) == 0:
            return ip_word
        else:
            return servers_list
    else:
        return None



def cloud_get_data_in(**kwargs):
    '''
        get net cloud data
    '''
    
    cloud_ids = kwargs.pop('cloud_ids')
    cloud_yuns = kwargs.pop('cloud_yuns')
    nubstart = kwargs.get('nubstart', 0)
    nubend = kwargs.get('nubend', 100)
    aliyun = re.match('aly\d+', cloud_yuns)
    tenxunyun = re.match('tx\d+', cloud_yuns)
    
    if aliyun:
        cloud = get_object(IDC, id=cloud_ids)
        keyid = str(cloud.cloudid)
        keysecret = str(cloud.cloudkey)
        regid = str(cloud.cloudregid)
        if keyid and keysecret and regid:
            alycloud = ALiYunApi(keyid=keyid, keysecret=keysecret, regionid=regid)
            data = alycloud.ecsresult()
            result = json.loads(data)
            servers = result['Instances']['Instance']
            keylists={'ip_word':['PublicIpAddress', 'IpAddress', 0]}
            get_ip_word = get_enumerate_data(datas=servers, keylists=keylists)
                                
            db_add = db_add_cloud(result=result, ip_word=get_ip_word, idc_id=cloud)               
                         
    elif tenxunyun:
        cloud = get_object(IDC, id=cloud_ids)
        keyid = str(cloud.cloudid)
        keysecret = str(cloud.cloudkey)
        regid = str(cloud.cloudregid)
        if keyid and keysecret and regid:
            numb = 0
            tags = True
            results = {}
            get_ip_words = []
            while tags:
                nubstarts = nubstart + numb
                nubends = nubend
                if nubstarts == 0:
                    txcloud = TenXunYunCvm(secretId=keyid, secretKey=keysecret, Region=regid, nubstart=nubstarts, nubend=nubends)
                    data = txcloud.cvmresult()
                    result = json.loads(data)
                    servers = result['instanceSet']
                    keylists={'ip_word':['wanIpSet', 0]}
                    get_ip_word = get_enumerate_data(datas=servers, keylists=keylists)
                    results = result
                    for ip in get_ip_word:
                        get_ip_words.append(ip)
                    
                elif nubstarts >= 100: 
                    txcloud = TenXunYunCvm(secretId=keyid, secretKey=keysecret, Region=regid, nubstart=nubstarts, nubend=nubends)
                    data = txcloud.cvmresult()
                    result = json.loads(data)
                    servers = result['instanceSet']
                    if len(servers) > 0: 
                        keylists={'ip_word':['wanIpSet', 0]}
                        get_ip_word = get_enumerate_data(datas=servers, keylists=keylists) 
                        for sers in servers:                   
                            results['instanceSet'].append(sers)
                        for ip in get_ip_word:
                            get_ip_words.append(ip)
                    else:
                        tags = False
                numb += 100           
        
            db_add = db_add_cloud(result=results, ip_word=get_ip_words, idc_id=cloud)



def db_cloud_get(**kwargs):
    '''
        select cloud record db data
    '''
    confidvls = kwargs.pop('confidvls')
    getfid = kwargs.pop('getfid')
    get_fidvld = CloudRecord.objects.filter(idc=confidvls).order_by('-update_time').values(getfid)
    if len(get_fidvld) != 0:
        get_fidvld = get_fidvld[0][getfid]
    else:
        get_fidvld = None
    return get_fidvld


def db_cloud_get_detail(**kwargs):
    '''
        select cloud recard db data to detail servers
    '''
    cloud_ids = kwargs.pop('cloud_ids')
    cloud_yuns = kwargs.pop('cloud_yuns')      
    if cloud_ids and cloud_yuns:
        aliyun = re.match('aly\d+', cloud_yuns)
        tenxunyun = re.match('tx\d+', cloud_yuns)           
        if aliyun:
            get_cloud_servers = db_cloud_get(confidvls=cloud_ids, getfid='assetcloud')
            servers = json.loads(get_cloud_servers)['Instances']['Instance']
            keylists={'wan_ip':['PublicIpAddress', 'IpAddress', 0], 
                      'lan_ip':['InnerIpAddress', 'IpAddress', 0], 
                      'cpu':['Cpu'], 
                      'memory':['Memory'], 
                      #'disk':"['Memory']", 
                      'cretime':['CreationTime'],
                      'exptime':['ExpiredTime'],
                      'imageid':['ImageId'],
                      'banwidth':['InternetMaxBandwidthOut']}        
            servers_detail = get_enumerate_data(datas=servers, keylists=keylists)
         
        elif tenxunyun:
            get_cloud_servers = db_cloud_get(confidvls=cloud_ids, getfid='assetcloud')
            servers = json.loads(get_cloud_servers)['instanceSet']          
            keylists={'wan_ip':['wanIpSet', 0], 
                      'lan_ip':['lanIp'], 
                      'cpu':['cpu'], 
                      'memory':['mem'], 
                      'disk':['diskInfo'], 
                      'cretime':['createTime'],
                      'exptime':['deadlineTime'],
                      'imageid':['imageId'],
                      'banwidth':['bandwidth']}        
            servers_detail = get_enumerate_data(datas=servers, keylists=keylists)
        
        return servers_detail


def db_add_cloud(**kwargs):
    '''
        add cloud record db data
    '''
    results = kwargs.pop('result')
    ip_words = kwargs.pop('ip_word')
    idc_ids = kwargs.pop('idc_id')
    
    if results and ip_words and idc_ids:
        asstcld = json.dumps(results)
        wordkey = json.dumps(ip_words)
        if len(asstcld) == 0:
            status = 2
        else:
            status =1               
        
        data_ips = db_cloud_get(confidvls=idc_ids, getfid='wordkey')
    
        if data_ips:
            ip_word_old = json.loads(data_ips)
        else:
            ip_word_old = 'None'                 
        dif_ip_list = []
        if ip_word_old == 'None':
            server = CloudRecord.objects.create(assetcloud=asstcld, idc=idc_ids, wordkey=wordkey, status=status, update_time=datetime.datetime.now())               
            server.save()                 
        else:
            for i in ip_words:
                if i not in ip_word_old:
                    dif_ip_list.append(i)
            if len(dif_ip_list) != 0:
                server = CloudRecord.objects.create(assetcloud=asstcld, idc=idc_ids, wordkey=wordkey, status=status, update_time=datetime.datetime.now())               
                server.save()


def db_hostasset_get(**kwargs):
    pass
    

def db_add_hostasset(**kwargs):
    pass


def conf_add_file(conf, file_id=None, filename=None):
    """
            配置中添加文件
    """
    if file_id:
        file = get_object(ApplyFile, id=file_id)
    else:
        file = get_object(ApplyFile, filename=filename)

    if file:
        conf.configfile.add(file)


def db_add_conf(**kwargs):
    """
    数据库中添加配置
    """
    name = kwargs.get('name')
    conf = get_object(ConfigVocational, name=name)
    files = kwargs.pop('files_id')

    if not conf:
        conf = ConfigVocational(**kwargs)
        conf.save()
        for file_id in files:
            conf_add_file(conf, file_id)
            

def conf_update_member(conf_id, files_id_list):
    """
    配置中更新应用文件
    """
    conf = get_object(ConfigVocational, id=conf_id)
    if conf:
        conf.configfile.clear()
        for file_id in files_id_list:
            file = get_object(ConfigVocational, id=file_id)
            if isinstance(file, ConfigVocational):
                conf.configfile.add(file)       
        
        
        
        
        
        
        
        
        
        
        
        
        