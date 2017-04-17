#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2, urllib, json, re
import ssl
ssl._create_default_https_context = ssl._create_unverified_context         # windows 关闭证书


class saltAPI:
    def __init__(self):
        self.__url = 'https://192.168.1.182:8888'
#         self.__url = 'https://' + ipp + ':' + portp       #salt-api监控的地址和端口如:'https://192.168.188.203:8888'
        self.__user =  'saltapi'             #salt-api用户名
        self.__password = 'password'          #salt-api用户密码
        self.__token_id = self.salt_login()
#     def __init__(self, urlp, userp, passwdp):
# #        self.__url = 'https://' + ipp + ':' + portp     #salt-api监控的地址和端口如:'https://192.168.188.203:8888'
#         self.__url = urlp
#         self.__user = userp             #salt-api用户名
#         self.__password = passwdp         #salt-api用户密码
#         self.__token_id = self.salt_login()

    def salt_login(self):
        params = {'eauth': 'pam', 'username': self.__user, 'password': self.__password}
        encode = urllib.urlencode(params)
        obj = urllib.unquote(encode)
        headers = {'X-Auth-Token':''}
        url = self.__url + '/login'
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        try:
            token = content['return'][0]['token']
            return token
        except KeyError:
            raise KeyError

    def postRequest(self, obj, prefix='/'):
        url = self.__url + prefix
        headers = {'X-Auth-Token'   : self.__token_id}
#        formats = {'Accept': 'application/x-yaml'}
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        return content ['return']

    def saltCmd(self, params):
        obj = urllib.urlencode(params)
        obj, number = re.subn("arg\d", 'arg', obj)
        res = self.postRequest(obj)
        return res

def main():
    #以下是用来测试saltAPI类的部分
    sapi = saltAPI()
    params = {'client':'local', 'fun':'test.ping', 'tgt':'*'}
    #params = {'client':'local', 'fun':'test.ping', 'tgt':'某台服务器的key'}
    #params = {'client':'local', 'fun':'test.echo', 'tgt':'某台服务器的key', 'arg1':'hello'}
    #params = {'client':'local', 'fun':'test.ping', 'tgt':'某组服务器的组名', 'expr_form':'nodegroup'}
    test = sapi.saltCmd(params)
    print type(test)

if __name__ == '__main__':
    main()