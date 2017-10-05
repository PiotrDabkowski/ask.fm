import deathbycaptcha as dbc
import time
from bs4 import BeautifulSoup
import cPickle
import urllib

def save_data(path,data):
    f=open(path,'wb')
    cPickle.dump(data,f,protocol=2)
    f.close()

def load_data(path):
    f=open(path,'rb')
    data=cPickle.load(f)
    f.close()
    return data

def save_res(res, read=True):
    f=open('response.html','wb')
    if read:
        f.write(res.read())
    else:
        f.write(res)
    f.close()
    



    
def check_ban():
    '''Returns 1 if captcha 2 if ban and 0 if server is not aware that we are using the bot'''
    r = urllib.urlopen('http://www.ask.fm').read()
    if 'captcha' in r:
        return 1
    if 'robocat' in r:
        return 2
    return 0
    
def easy_licence_check(key):
    return time.localtime()
    try:
        easy = key[0:20].decode('hex')
        ex = [int(e) for e in easy.split('+')][::-1]
        return time.struct_time(ex+[23,59,59]+3*[0])
    except:
        return False
        
    
class CaptchaSolver:
    ''' API to death by captcha. PAID :(

        To solve a captcha use solve method giving the path to the
        captcha image file (stored on your computer). After some
        time it should return the text that was in the captcha.
        If the text is not valid then use report_last method.

        Cheaper but much slower method is change_ip from cute_ip_changer (2 minutes)
    '''
    def __init__(self, login='piodrus', password='drukarka'):
        self.solver=dbc.HttpClient(login, password)

    def solve(self, path, timeout=60):
        try:
           self.last_captcha=self.solver.decode(open(path,'rb'),timeout)
        except:
            return False
        if self.last_captcha:
            return self.last_captcha['text']
        return False

    def report_last(self):
        return self.solver.report(self.last_captcha['captcha'])
    
class SourceReader:
    def __init__(self, source, ajaxed=False, bs=True):
        if '"questionBox\\"'  in source:
            source = self.find_by_start_end(source, '</script>', '");')
            source=source.replace('\\','')
        self.source = source
        self.bs=BeautifulSoup(source, "lxml")
        self.auth_token = False
        
    def get_auth_token(self):
        if self.auth_token:
            return self.auth_token
        start='AUTH_TOKEN = "'
        end='"'
        return self.find_by_start_end(self.source, start, end)

    def find_by_start_end(self, source, start, end, list_all=False):
        res=[]
        while True:
            try:
                beg = source.index(start)+len(start)
                fin=source[beg:].index(end)
            except:
                if not list_all: 
                     raise ValueError('Could not find the auth token, the pattern does not work.')
                break
            res.append(source[beg:fin+beg])
            source = source[fin+beg+1:]
            if not list_all:
                return res[0]
        return res

    def get_unliked_questions(self):
        return self.find_by_start_end(self.source, "Profile.quickLike('#like_box_", "'", True)
        unliked = self.bs.select('.likeBox a')
        return [self.find_by_start_end(like['onclick'],"url:'","'") for like in unliked]

    def get_all_questions(self):
        r =  self.get_questions().keys()
        print r
        return r
        return [e.strip(' \\') for e in self.find_by_start_end(self.source, '"div id="question_box_', '"', True)]
        
    def get_questions(self):
        raws=self.bs.select('.questionBox')
        results = {}
        for raw in raws:
            try:
                results[raw['id'].split('_')[-1]]= raw.select('.question')[0].text.strip()
            except:
                pass
        return results
    
class AccountDatabase:
    def __init__(self, path='accounts.cpi'):
        self.path=path
        self.data={}
        self.load()
        if self.data:
            self.make_backup()

    def load(self, path=False):
        if path:
            self.path=path
        try:
            self.data=load_data(self.path)
        except:
            self.data={}
            self.save()

    def save(self, path=False):
        if not path:
            path=self.path
        save_data(path, self.data)
        
    def make_backup(self):
        self.save(''.join(self.path.split('.')[:-1])+'.bak.'+self.path.split('.')[-1])

    def load_backup(self):
        try:
            self.data=load_data(self.path.split('.')[:-1]+'.bak.'+self.path.split('.')[-1])
        except:
            pass

    def add_account(self, name, login, password, email,age,male, egg=False):
        self.data[login]={'login':login, 'password':password,
                         'email': email, 'clone':egg,
                         'created':time.time(), 'last_time':0,
                         'name':name, 'age':age, 'male':male, 'q':0,
                         'questions':0, 'likes':0, 'v10':0, 'v25':0,'targets':{}}
        self.save()

    def just_used(self,login):
        self.data[login]['last_time']=time.time()
        
    def del_account(self, login):
        if not login in self.data:
            return False
        del self.data[login]
        self.save()
        return True

    def get_ready_acc(self, interval=3600, minimal_number_of_possible_likes=25, target='targetslogin', target_questions=1000, dont=[]):
         for login in self.data:
             if not login in dont:
                 if time.time()-self.data[login]['last_time']>=interval:
                     possible = self.get_possible_likes(login, target, target_questions)
                     if len(possible)>=minimal_number_of_possible_likes:
                         return self.data[login], possible
         return False, xrange(0)

    def get_possible_likes(self, login, target, target_questions):
        if  target in self.data[login]['targets']:
            r = xrange(self.data[login]['targets'][target], target_questions)
            return r
        return xrange(target_questions)

    def update_liked_questions(self, login, target, n):
        if  target in self.data[login]['targets']:
            self.data[login]['targets'][target]+=n
        else:
            self.data[login]['targets'][target] = n
        


    
def check_account(login):
    '''Returns the number of likes and questions. If suspended or not valid returns false.
    Returns None otherwise.'''
    base = 'http://ask.fm/'
    try:
        res=urllib.urlopen(base+login)#br.open(base+login)
        source = res.read()
        bs=BeautifulSoup(source, "lxml")
    except:
        return None
    try:
        ls = int(bs.select('#profile_liked_counter')[0].text.strip())
        qs = int(bs.select('#profile_answer_counter')[0].text.strip())
    except IndexError:
        if 'suspended-headline' in source or 'kitten-image-anybody' in source:
            return False
        else:
            return None
    except:
        return None
    return ls, qs



