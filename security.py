import hashlib
import ctypes
from uuid import getnode
import sys
from Crypto.Cipher import AES
import ntplib
import time
import threading
import os
import time
import traceback

def dbg_watcher():
    return
    while True:
        if os.name=='nt' and ctypes.windll.kernel32.IsDebuggerPresent():
            os.kill()
        time.sleep(0.5)

t = threading.Thread(target=dbg_watcher)
t.daemon = True
t.start()

class Security:
    def __init__(self, key):
        self.is_debugging()
        key = key[20:]
        try:
            self.OK=False
            self.MAC = getnode()
            if self.MAC!= getnode() or self.MAC!= getnode(): #Unable to determine mac address
                raise
            self.MAGIC = 'answer_questions'
            self.KEY = key.decode('hex')
            self.b  = hashlib.sha256()
            self.c = ntplib.NTPClient()
            self.time = self.check_time()
            self.check_key()
        except:
            print traceback.format_exc()
            os.abort()
            raise
        
        
    def is_debugging(self):
        if os.name=='nt' and ctypes.windll.kernel32.IsDebuggerPresent():
            sys.abort()
            raise
            return True

    def check_time(self):
        return time.time()+100000
        sys_time = time.strftime('%d+%m+%Y').split('+')
        sys_time = [int(e) for e in sys_time]
        return sys_time
        response = self.c.request('europe.pool.ntp.org', version=3)
        int_time = time.strftime('%d+%m+%Y',time.localtime(response.tx_time)).split('+')
        int_time = [int(e) for e in int_time]
        if sys_time[1]!=int_time[1]:
            sys.exit()
            raise
        if sys_time[2]!=int_time[2]:
            sys.exit()
            raise
        if sys_time[0] not in [int_time[0],int_time[0]+1,int_time[0]-1]:
            sys.exit()
            raise
        return int_time
        
        
    def check_key(self):
        self.ext = (11, 11, 2022)
        self.expires = time.strftime("%d %B %Y", time.localtime())
        self.OK=time
        return
        if self.is_debugging() or self.MAC!= getnode() or self.MAC!= getnode():
            sys.exit()
            raise
        else:
            a=hashlib.sha256()
            a.update(str(self.MAC))
        decoder = AES.new(self.MAGIC, AES.MODE_CBC,'1234567890121314')
        self.hash, self.expires, self.secret, pff = decoder.decrypt(self.KEY).split('b_34u')
        decoder2 = AES.new('super ask.fm bot', AES.MODE_CBC, '1234567890121314')
        self.b.update(self.hash + self.expires)
        if int(decoder2.decrypt(self.secret),16)!= int(self.b.hexdigest(),16):
            sys.exit()
            raise
        if int(self.hash,16)!=int(a.hexdigest(),16):
            sys.exit()
            raise
        if self.check_time()!=self.time:
            sys.exit()
            raise
        ex = [int(e) for e in self.expires.split('+')]
        if ex[2]<self.time[2]:
            sys.exit()
            raise
        if self.check_time()!=self.time:
            sys.exit()
            raise
        if ex[1]<self.time[1] and ex[2]==self.time[2]:
            sys.exit()
            raise
        if self.check_time()!=self.time:
            sys.exit()
            raise
        if ex[0]<self.time[0] and ex[2]==self.time[2]and ex[1]==self.time[1]:
            sys.exit()
            raise
        if self.check_time()!=self.time:
            sys.exit()
            raise
        self.ext = ex
        self.expires = time.strftime("%d %B %Y", time.struct_time(ex[::-1]+6*[0]))
        self.OK=time


    
            

        
