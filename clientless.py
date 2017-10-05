import mechanize
from bs4 import BeautifulSoup
import urllib
import sys
import httplib2 
from PIL import Image
import security
from time import gmtime, strftime
import random
from ask_utils import AccountDatabase
from pygoogle import Google
import cPickle
import os
import cookielib
from cookielib import Cookie
from ask_utils import SourceReader

try:
    f=open('licence.txt','rb')
    key = f.read()
    f.close()
except:
    os.abort()
    raise
sec_u = security.Security(key)
if not sec_u.OK:
    os.abort()
    sys.exit()
    raise

time = sec_u.OK

#Global classes
g=Google()
#d=AccountDatabase('accounts.cpi')


FRAME = False
def _set_info_sink(wxFrame):
    global FRAME
    FRAME = wxFrame
    
def save_data(path,data):
    f=open(path,'wb')
    cPickle.dump(data,f,protocol=2)
    f.close()

def load_data(path):
    f=open(path,'rb')
    data=cPickle.load(f)
    f.close()
    return data

def valid_encoding(text):
        if type(text)!=unicode:
            #print 'not unicode'
            try:
                text  = text.decode('windows-1250')
            except:
                #print 'error'
                return text
        #print 'unicode'
        return text.encode('UTF-8')
    
def save_res(res, read=True):
    f=open('response.html','wb')
    if read:
        f.write(res.read())
    else:
        f.write(res)
    f.close()

def update_acc_data(db):
    base = 'http://ask.fm/'
    #br = mechanize.Browser()
    #br.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0")]
    todel = []
    for login in db.data:
        try:
            res=urllib.urlopen(base+login)#br.open(base+login)
            source = res.read()
            bs=BeautifulSoup(source, "lxml")
            
            ls = int(bs.select('#profile_liked_counter')[0].text.strip())
            qs = int(bs.select('#profile_answer_counter')[0].text.strip())

            db.data[login]['likes']=ls
            db.data[login]['questions']=qs
        except IndexError:
            if 'suspended-headline' in source:
                todel.append(login)
    for login in todel:
        del db.data[login]
    db.save()
            
           
def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '---------------------------3313324117326'
    CRLF = '\r\n'
    fields.reverse()
    L = []
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % 'image/png')
        L.append('')
        L.append(value)
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body



    
if sec_u.OK.strftime:
 class Client:
    def __init__(self, login='testa7486', password='thisisatest', debug=False,
                 standby=False, auto_complete=False, db='accounts.cpi',
                 proxy=False, real_proxy=False, auto_like=False, timeout=False,
                 requests_per_second=2.85):
        self.auto_like = auto_like
        self.timeout = timeout
        self.acc_login = login
        self.total_likes = 0
        self.rps = requests_per_second
        self.dks= sec_u.OK.time
        self.last_req = time.time()
        if auto_like:
            self.BUSY=True
            self.LOGIN_FAILED = False
            self.AUTO_LIKE_RESULT = {q_id:False for q_id in auto_like['q_list']}
        if real_proxy:
            host, port = real_proxy.values()[0].split(':')
            self.h = httplib2.Http(proxy_info = httplib2.ProxyInfo(3, host, int(port)))
        else:
            self.h = httplib2.Http()
        self.logged = False
        self.INIT_TIME = time.time()
        self.real_proxy=real_proxy
        
        self.base = 'http://ask.fm'
        self.br = mechanize.Browser()
        if self.real_proxy:
                self.br.set_proxies(real_proxy)
        self.proxy=proxy
        self.br.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0")]
        self.br.set_debug_redirects(debug)
        self.br.set_debug_responses(debug)
        self.br.set_debug_http(debug)
        self.br.set_handle_robots(False)
        self.acc_login = login
        self.acc_password  =password 
        if not (standby or auto_like):
            if not self._login(login, password):
                 raise Exception('Try again with correct password')
        try:
            if (not auto_complete) or auto_like:
                    raise 
            self.db = AccountDatabase(db)
            self.get_questions() # <--- Useless but does not work without it!
            if login in self.db.data:
                if not self.db.data[login]['clone']['bio_complete']:
                    try:
                        name = self.db.data[login]['clone']['name']
                        city = self.db.data[login]['clone']['city']
                        description = self.db.data[login]['clone']['info']
                        links = self.db.data[login]['clone']['links']
                        avatar_link = self.db.data[login]['clone']['avatar']
                        urllib.urlretrieve(avatar_link, 'ask.png')
                        if not self.complete_info(name, city, description, links):
                                print 'Fuck complete info!'
                        if not self.upload_avatar('ask.png'):
                                print 'Fuck upload avatar!'
                        self.db.data[login]['clone']['bio_complete'] = True
                        self.db.save()
                        print 'Profile has been completed and is ready to use!'
                    except KeyError, err:
                        print err
                        print 'Could not complete the profile!'
            del self.db
        except:
            pass
            #self.get_questions()
        if FRAME:
            FRAME.update_status_bar(login)

    def _wait(self):
        '''Waits if needed in order to not exceed maximum number of requests
           per second (self.rps)'''
        delay = 1.1/self.rps
        tot = 0
        while time.time()-self.last_req<delay:
            time.sleep(0.005)
            tot+=0.005
        print 'Waited for', tot
        self.last_req = time.time()
            
        
    def start_auto_like(self):
        try:
            self._login(self.acc_login, self.acc_password)
        except ValueError:
            self.LOGIN_FAILED = 'account'  # fail reason
        except RuntimeError:
            self.LOGIN_FAILED = 'proxy'  # shit proxy
        if not self.LOGIN_FAILED:
            print 'Logged in!'
            try:
                self.open_profile(self.auto_like['target'])
                print 'starting likes!'
                self.AUTO_LIKE_RESULT = self.like_list(self.auto_like['q_list'], self.auto_like['max_per_second'])
                print 'done likes!'
            except:
                print self.acc_login, 'could not open target\'s profile page!'
            try:
                self.logout()
            except:
                print self.acc_login, 'could not logout!'
        self.BUSY=False


    def __repr__(self):
        return 'Client(login="%s")'%self.acc_login
        
    def _login(self, login='testa7487', password='thisisatest'):
        if self.logged:
                raise Exception('Already logged in!')
        url = self.base+'/login'
        try:
            res=self.br.open(url)
        except:
            raise RuntimeError('Could not open login page!')
        if 'robocat' in res.read():
            raise RuntimeError('IP banned! Please wait or change IP.')
        try:
            self.br.select_form(nr=0)
            self.br['login'] = login
            self.br['password'] = password
            self.res = self.br.submit()
        except:
            raise RuntimeError('Could not complete the login form!')
        so = self.res.read()
        if not 'tlb_menu_inbox' in so:
            raise ValueError('Invalid login or password! OR account blocked')
        self.AUTH_TOKEN = SourceReader(so, bs=False, ajaxed=False).get_auth_token()
        self.logged = True
        self.profile=''
        self.acc_login = login
        self.acc_password = password
        self.login_time = time.time()
        return True

    def get_online_time(self):
        return time.time()-self.login_time

    def standard_post(self, url):
         std = urllib.urlencode({'authenticity_token': self.AUTH_TOKEN})
         self.POST2(url, std)

    def get_random_question(self):
        self._wait()
        self.standard_post('http://ask.fm/questions/random')

    def convert_cookies(self):
        aim=[Cookie(version=0, name='country_code', value='GB', port=None, port_specified=False, domain='.ask.fm', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1425227711, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False),
             Cookie(version=0, name='country_id', value='5', port=None, port_specified=False, domain='.ask.fm', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1425227711, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False),
             Cookie(version=0, name='l', value='1', port=None, port_specified=False, domain='.ask.fm', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1425227711, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False),
             Cookie(version=0, name='language_id', value='10', port=None, port_specified=False, domain='.ask.fm', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1425227711, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False),
             Cookie(version=0, name='mobile_view', value='false', port=None, port_specified=False, domain='.ask.fm', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={}, rfc2109=False),
             Cookie(version=0, name='_ask.fm_session', value='BAh7CjoQb2xkX2dl', port=None, port_specified=False, domain='ask.fm', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False),
             Cookie(version=0, name='auth_token', value='e21c288190ce22', port=None, port_specified=False, domain='ask.fm', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1394901311, discard=False, comment=None, comment_url=None, rest={}, rfc2109=False)
             ]
        current = [e for e in self.br._ua_handlers['_cookies'].cookiejar]
        cj = cookielib.CookieJar()
        str_cookie = []
        for cookie in current:
            name = urllib.unquote(cookie.name).split('[')[-1][0:-1]
            valid = False
            for cand in aim:
                if cand.name == name:
                    valid = cand
                    break
            if not valid:
                continue
            print name, cookie.value
            valid.value = cookie.value
            valid.expires = str(14425227711)
            cj.set_cookie(valid)
            str_cookie.append('%s=%s'%(valid.name, valid.value))
        str_cookie = '; '.join(str_cookie)
        #Convert back to normal
        self.br.request.add_header('Cookie',str_cookie)
        self.br._ua_handlers['_cookies'].cookiejar = cj
                 
    def upload_avatar(self, path ):
        # 2 Days lost on this fucking function but it works!!!!
        self._wait()
        self.open_profile(self.acc_login)
        JsID=str(13978588979082-random.randrange(17299336792)) #bullshit
        #Convert to png
        im=Image.open(path)
        path='avatar.png'
        im.save(path)
        
        url = 'http://upload1.ask.fm/upload/web-avatar/xhr?JsHttpRequest='+str(JsID)+'-form'
        
        data = {"authenticity_token": self.AUTH_TOKEN,
                "RequestID": str(int(JsID)/10-random.randrange(10)+1),
                "ObjectSpec": self.sr.find_by_start_end(self.sr.source, '"ObjectSpec":"', '"').replace('\\n','\r\n')
                }
        files = ("file", os.path.split(path)[-1], open(path,'rb').read())
        typ, body = encode_multipart_formdata(data.items(), [files])
        
        headers = {'Content-Type': typ,
                   'Content-Length': str(len(body)),
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Connection': 'keep-alive',
                   'Referer': 'http://ask.fm/'+self.acc_login,
                   'Accept-Encoding': 'gzip, deflate',
                   'Host': 'upload1.ask.fm',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0',
                   'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3'
                   }
        headers['Cookie'] = self.generate_headers()['Cookie']
        response  = self.h.request(url,'POST', body, headers)
        del headers['Content-Length']
        del headers['Content-Type']
        headers['Host'] = 'ask.fm'
        response = self.h.request(response[0]['location'],'GET', '', headers)
        #Check if ok
        try:
            if 'error' in response[0]['content-location']:
                return False
            elif 'succcess' in response[0]['content-location']:
                return True
        except:
            print 'Error in upload avatar'
            return False
        raise Exception('Repair error detection!')
        

    def get_cookie(self):
        return self.generate_headers()['Cookie']

    def logout(self):
        self._wait()
        logout_data = urllib.urlencode({'authenticity_token': self.AUTH_TOKEN,
                                        'commit': ""})
        self.br.open(self.base+'/logout', data=logout_data)
        self.logged = False
        self.sr = False
        self.profile = ''
        self.AUTH_TOKEN = False
        self.__class__ = DeadClient
        if FRAME:
            FRAME.update_status_bar('None')
    
    def open_profile(self, login):
        self._wait()
        self.res = self.br.open(self.base+'/'+login)
        self.page=0
        self.profile = login
        self.ajaxed=False
        self.sr  = SourceReader(self.res.read(), bs=False, ajaxed=False)
        self.total_likes = int(self.sr.bs.select('#profile_answer_counter')[0].text.strip())
        
    def get_questions(self):
        self._wait()
        self.res = self.br.open(self.base+'/account/questions')
        return SourceReader(self.res.read()).get_questions()
        
    def del_question(self, q_id):
        self._wait()
        if not q_id: #Delete all
            url = 'http://ask.fm/questions/delete'
        else:
            url = 'http://ask.fm/questions/%d/delete'%int(q_id)
        body  = urllib.urlencode({'_method': 'delete',
                                'authenticity_token': self.AUTH_TOKEN
                                  })
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Content-Length': str(len(body)),
                   'Connection': 'keep-alive',
                   'Referer': 'http://ask.fm/account/questions',
                   'Accept-Encoding': 'gzip, deflate',
                   'Host': 'ask.fm',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0',
                   'Accept': 'text/javascript, application/javascript, */*, text/javascript',
                   'Accept-Language': 'pl,en-us;q=0.7,en;q=0.3',
                   'Pragma': 'no-cache',
                   'Cache-Control': 'no-cache'
                   }
        headers['Cookie'] = self.generate_headers()['Cookie']
        if '200'==self.h.request(url,'POST', body, headers)[0]['status']:
            return True
        return False
        

    def answer_question(self, q_id, answer):
        self._wait()
        url = 'http://ask.fm/questions/%d/answer'%int(q_id)
        body  = urllib.urlencode({'_method': 'put',
                                'authenticity_token': self.AUTH_TOKEN,
                                'question[answer_text]':valid_encoding(answer),
                                'photo_request_id': '',
                                'commit': 'Odpowiedz',
                                'question[submit_stream]': '0',
                                'question[submit_twitter]': '0',
                                'question[submit_facebook]': '0'
                                })
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Content-Length': str(len(body)),
                   'Connection': 'keep-alive',
                   'Referer': 'http://ask.fm/testa7486/questions/%d/reply'%int(q_id),
                   'Accept-Encoding': 'gzip, deflate',
                   'Host': 'ask.fm',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'pl,en-us;q=0.7,en;q=0.3'
                   }
        headers['Cookie'] = self.generate_headers()['Cookie']

        if '302'==self.h.request(url,'POST', body, headers)[0]['status']:
            return True
        return False
        
    def like_visible(self, n=False, interval=0):
        if not self.logged:
            print('Login before liking!')
            return 0
        if not self.profile:
            print('Open profile before liking!')
        if self.total_likes>80:
            print 'Soon you will get banned, I suggest changing account'
        #like_data = urllib.urlencode({'authenticity_token': self.AUTH_TOKEN})
        n = n if n else 10000
        done=0
        t=time.time()
        for question in self.sr.get_unliked_questions():
            #self.br.open(self.base+'/likes/'+self.profile+'/question/'+question+'/add', data=like_data)
            #self.POST2(self.base+'/likes/'+self.profile+'/question/'+question+'/add', data=like_data)
            self._post_like(question)
            done+=1
            if n<=done:
                break
        print 'Done', done,'likes in',round(time.time()-t,2),'seconds. '
        print 'It is', round(done/(time.time()-t),2) ,'likes per second!'
        self.total_likes+=done
        return done

    def complete_info(self, name, city, description, links):
        self._wait()
        url = 'http://ask.fm/account/settings/profile/quick_save'
        info = urllib.urlencode({'_method': 'put',
                'authenticity_token': self.AUTH_TOKEN,
                'name': valid_encoding(name),
                'location': valid_encoding(city),
                'about_me': valid_encoding(description),
                'website': valid_encoding(links),
                'allow_anonymous': 'true'
                })
        add_cookies = {'Content-Type': 'application/x-www-form-urlencoded',
                      'Content-Length': str(len(info))
                       }
        response = self.POST2(url, info, {}, add_cookies)
        try:
            if response[0]['status']!='302':
                return False
        except:
                return False
        return True

    def like(self, n=70, try_empty_pages = 4, interval = 0, target=False):
        self.BUSY = True
        if target:
            self.open_profile(target)
        if not self.logged:
            print('Login before liking!')
            return 0
        if not self.profile:
            print('Open profile before liking!')
        done = 0
        while n>done:
            add = self.like_visible(n-done, interval)
            if not add:
                try_empty_pages+=-1
                if try_empty_pages<0:
                   print('Nothing on this page, quiting...')
                   break
                print('Nothing on this page, checking other page...')
            done+=add
            if done!=n:
                if not self.load_more_results():
                    break
        self.BUSY = False
        return done

    def _post_like(self, q_id, method2=False):
        '''like a question by q_id'''
        self._wait()
        url = self.base+'/likes/'+self.profile+'/question/'+str(q_id)+'/add'
        
        body = urllib.urlencode({'authenticity_token': self.AUTH_TOKEN})
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Content-Length': str(len(body)),
                   'Connection': 'keep-alive',
                   'Referer': 'http://ask.fm/'+self.profile,
                   #'Accept-Encoding': 'gzip, deflate',
                   'Host': 'ask.fm',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0',
                   'Accept': 'text/javascript, application/javascript, */*, text/javascript',
                   'Accept-Language': 'pl,en-us;q=0.7,en;q=0.3',
                   'Pragma': 'no-cache',
                   'Cache-Control': 'no-cache'
                   }
        headers['Cookie'] = self.generate_headers()['Cookie']
        if not method2:
            return self.h.request(url,'POST', body, headers)[1]
        return self.br_request(url, headers, body).read()

    def like_list(self, q_list, max_per_second = 100):
        '''This function supports FRAME update'''
        results = {q_id:False for q_id in q_list}
        for q_id in q_list:
            try:
                raw = self._post_like(q_id, False) #No way to get the total number of likes anymore :(
                self.total_likes+=1
                if FRAME:
                    FRAME.account_panel.likes_added.SetValue(str(int(FRAME.account_panel.likes_added.GetValue())+1))
                res = True
            except:
                res=False
            if not res or (FRAME and FRAME.STOP): #something is wrong, check if banned or captcha
                print 'Something is wrong...'
                break # <<<<<<<<<<<<<<<<<<<<<
            results[q_id] = res
        return results
        
    def smart_answer(self, n, search=True):
        while n>5 and not (FRAME and FRAME.STOP):
            n = n - self._smart_answer(5, search)
        while n>0 and not (FRAME and FRAME.STOP):
            n = n - self._smart_answer(n, search)
        return n
    
    def _smart_answer(self, n, search):
        if n>5:
                raise ValueError('Cannot answer more than 15 question at once')
        elif n<=0:
                return 0
        for e in xrange(n):
            self.get_random_question()
        done = 0
        questions = self.get_questions()
        known=load_data('answers.cpi')
        updated = False
        for question in questions:
            if FRAME and FRAME.STOP:
                return done
            query = questions[question]
            if query not in known:
                if not search:
                    print 'Not in database. Deleting...'
                    self.del_question(question)
                    continue
                print 'Not in database. Searching...'
                try:
                    new = g.answer_question(query)
                except IndexError, err:
                    print 'an error in pygoogle fix it!'
                    print err
                    new = []
                known[query] = new
                updated = True
            if len(known[query])<3:
                self.del_question(question)
                continue
            ans = random.choice(known[query])
            #print ans
            self.answer_question(question, ans)
            done+=1
            try:
                if FRAME:
                    a=FRAME.account_panel.questions_answered
                    a.SetValue(str(int(a.GetValue().strip())+1))
            except:
                print 'lol'
            if done>=n:
                break
        if updated:
            save_data('answers.cpi', known)
        return done
    
    def generate_headers(self, headers={}, cookies={}):
        base_headers= dict(self.br.request.header_items())
        text_cookies = '; '.join(['='.join(cookie) for cookie in cookies.items()])
        text_cookies = '; '+text_cookies if text_cookies else ''
        base_headers['Cookie'] = base_headers['Cookie']+text_cookies
        for head in base_headers:
                headers[head]=base_headers[head]
        return headers
        
    def POST2(self, url, data, headers = {}, cookies={}):
        #req = mechanize.Request(url, data)
        #req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0")
        #self.br._ua_handlers['_cookies'].cookiejar.add_cookie_header(req)
        #response = self.h.request(url, 'POST', data, dict(self.br.request.header_items()+cookies.items()),0)
        base_headers= dict(self.br.request.header_items())
        text_cookies = '; '.join(['='.join(cookie) for cookie in cookies.items()])
        text_cookies = '; '+text_cookies if text_cookies else ''
        #print 'old cookies: ', base_headers['Cookie']
        #print 'adding: ', text_cookies
        base_headers['Cookie'] = base_headers['Cookie']+text_cookies
        #print 'new_cookies: ' , base_headers['Cookie']
        for head in base_headers:
                headers[head]=base_headers[head]
        #response = requests.post(url, data=data, headers=headers)
        response = self.h.request(url, 'POST', data, headers)
        return response

    def load_more_results(self):
        self._wait()
        more_data  = urllib.urlencode( { 'time': strftime("%a+%b+%d+%X+UTC+%Y", gmtime()),
                                         'page': str(self.page+1),
                                         'authenticity_token': self.AUTH_TOKEN
                                         })
        print self.base+'/'+self.profile+'/more?'  +more_data                    
        new = self.GET2(self.base+'/'+self.profile+'/more?'  +more_data, '')[1]
        if len(new)<50:
            return False
        self.page+=1
        self.ajaxed = True
        self.sr  = SourceReader(new, bs=False, ajaxed=True)
        return True

    def br_request(self, url, headers, data):
        for header in headers:
            self.br.request.add_header(header, headers[header])
        self.br.request._Request__r_host = url
        self.br.request._Request__original = url
        return self.br.open(self.br.request, data)
        
    
    def GET2(self, url, data):
        #req = mechanize.Request(url, data)
        #req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0")
        #self.br._ua_handlers['_cookies'].cookiejar.add_cookie_header(req)
        hhhh= dict(self.br.request.header_items()) if not self.proxy else {}
        return self.h.request(url, 'GET', data, hhhh,0)

    def timeout_reached(self):
        if (not self.timeout) or time.time()-self.INIT_TIME<self.timeout:
            return False
        print 'Timeout bye!'
        return True
        
class DeadClient(Client):
    def _wait(self):
        raise Exception('The client is dead!')

while False:
    try:
        cmd = raw_input('>>> ')
        try:
           print eval(cmd)
        except SyntaxError:
           exec(cmd)
        except Exception, err:
                print err
    except Exception, err:
        print err

    
        

if __name__ == '__main__':
    import clientless_liker
    clientless_liker.Client = Client
    a = clientless_liker.LIKER()
    a.start_liking('crazykasia14', 30000)



