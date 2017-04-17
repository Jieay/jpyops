#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import random
import re
zm = 'abcdefghijklmnopqrstuvwxyz'
zmt = tuple(zm)
 
class prpcrypt():
    def __init__(self,key):
        self.key = key
        self.mode = AES.MODE_CBC
                

    def encrypt(self,text):
        cryptor = AES.new(self.key,self.mode,b'0000000000000000')
        length = 16
        count = len(text)
        if count < length:
            add = (length-count)
            text = text + ('\0' * add)
        elif count > length:
            add = (length-(count % length))
            text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        return b2a_hex(self.ciphertext)


    def mycryptjm(self,text):
        if text.strip():
            passwd = str(text)
            pl = len(passwd)
            plt = tuple(passwd)
            chg1 = []
            for i in range(pl):
                chg1.append(ord(plt[i]))
            chg2 = []
            for i in chg1:
                i = str(i)
                s = random.randint(0,25)
                k = zmt[s]
                yx = i + k
                chg2.append(yx)
            mw = ''.join(chg2)
            ws = str(pl)
            wcjm = mw + '+' + ws 
            return self.encrypt(wcjm)
        else:
            return None


    def decrypt(self,text):
        cryptor = AES.new(self.key,self.mode,b'0000000000000000')
        plain_text  = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')
    
    def mycryptdes(self,text):
        args = self.decrypt(text)
        if '+' in args:
            hy1 = args.split('+')
            hylen = hy1[-1]
            hy2 = hy1[0]
            hy3 = re.split(r'[a-z]', hy2)
            while '' in hy3:
                hy3.remove('')
            hy4 = []
            for i in hy3:
                i = int(i)
                hy4.append(chr(i))
            hy5 = ''.join(hy4)
            return hy5
        else:
            return None        
 
if __name__ == '__main__':
    pc = prpcrypt('keyskeyskeyskeys') # 初始化密钥
    import sys
    e = pc.mycryptjm('HJHuc9dqw83n2gweq12t12451235tdwe') # 加密
    d = pc.mycryptdes(e) # 解密
    print "加密:",e
    print len(e)
    print "解密:",d
    print len(d)