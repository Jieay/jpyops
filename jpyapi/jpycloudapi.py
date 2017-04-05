#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
import json
import sys
from jpyapi.src.QcloudApi.qcloudapi import QcloudApi

# default_encoding = 'utf-8'
# if sys.getdefaultencoding() != default_encoding:
#     reload(sys)
#     sys.setdefaultencoding(default_encoding)


class ALiYunApi(object):
    '''
        import aliyun ecs server hosts
    '''
    def __init__(self, **kwargs):
        self.__keyid = kwargs.get('keyid')
        self.__keysecret = kwargs.get('keysecret')
        self.regionid = kwargs.get('regionid')
    
        
    def connt(self, request):
        clt = client.AcsClient(self.__keyid, self.__keysecret, self.regionid)
        return clt.do_action(request)
     
    
    def ecsresult(self):
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format('json')
        result = self.connt(request)
        return result



class TenXunYunCvm(object):
    
    def __init__(self, **kwargs):
        self.__secretId = kwargs.get('secretId')
        self.__secretKey = kwargs.get('secretKey')
        self.Region = kwargs.get('Region')
        self.offset = kwargs.get('nubstart', 100)
        self.limit = kwargs.get('nubend', 100)
        self.status = kwargs.get('status', 2)
        
    def conn(self, module, action):
        self.module = module
        self.action = action
        config = {
                  'Region': self.Region,
                  'secretId': self.__secretId,
                  'secretKey': self.__secretKey,
                  'method': 'get'
                  }
        params = {
                  'offset': self.offset,
                  'limit': self.limit,
                  'status': self.status
                  }
        try:
            service = QcloudApi(module, config)
            geturl = service.generateUrl(action, params)
            requsl = service.call(action, params)
            return requsl
        except Exception, e:
            return 'exception:', e
              
    def cvmresult(self):
        self.module = 'cvm'
        self.action = 'DescribeInstances'
        result = self.conn(self.module, self.action)
        return result
        




if __name__ == '__main__':
#     p = ALiYunApi('LTAIeLb5PP5XEsch', '2atTFF7yzcO4ZFFA9LjiPdRlRCNx8K', 'cn-hangzhou')
#     print type(p.ecsresult())
#     print type(json.loads(p.ecsresult()))
#     hh = json.loads(p.ecsresult())
#     jj = hh['Instances']['Instance']
#     print jj
#     for i, jj in enumerate(jj):
#         print i, jj
#         fd,hj = i,jj
#         ll = fd + 1
#         print ll, hj
#          
#         ll = i +1
#          
#         print ll , jj['Instance'][0]['SerialNumber']
    kl = TenXunYunCvm(secretId='AKIDPippeHnx1ta5GG9hDXgdNvJxTnwtADcV', secretKey='tb8SqAWjmdIl2CPSJ2f8PUN3XoskT0Kx', Region='gz')
    print kl.cvmresult()
    print json.loads(kl.cvmresult())['instanceSet']
    gg = json.loads(kl.cvmresult())
    shili = gg['instanceSet']
    print type(shili)
#     for i,shili in enumerate(shili):
#         #print 'zhuji %s: %s' % (i, shili)
#         k,hh = i,shili
#         ll = k+1
#         #print ll,hh
#         print u'''
#                     第 %s 台:
#                             内网ip：%s
#                             外网ip：%s
#            CPU：%s 核
#                             内存：%s G
#                             系统盘：%s G
#                             数据盘：%s G
#                             系统：%s
#                             创建时间：%s
#                             到期时间：%s
#         ''' % (ll, hh['lanIp'], hh['wanIpSet'][0], hh['cpu'], hh['mem'], hh['diskInfo']['rootSize'], hh['diskInfo']['storageSize'], hh['os'], hh['createTime'], hh['statusTime'])        
#         
#         