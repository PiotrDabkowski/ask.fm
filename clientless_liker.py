from ask_utils import *
import threading
import time
from bs4 import BeautifulSoup,NavigableString
from hmaproxylist import get_proxies
import httplib2
import urllib


def save_res(res, read=True):
    f=open('response.html','wb')
    if read:
        f.write(res.read())
    else:
        f.write(res)
    f.close()

Client = False
FRAME = False
   
class LIKER:
    def __init__(self, acc_db = AccountDatabase('accounts.cpi'), max_parallel = 10, max_from_acc = 71,
                  acc_rest_interval = 3600, max_per_second = 10.8):
        self.h = httplib2.Http()
        
        self.acc_db = acc_db
        self.max_parallel  = max_parallel
        self.max_from_acc = max_from_acc
        self.acc_rest_interval = acc_rest_interval
        self.max_per_second = max_per_second
        self.total_likes = 0
        
        
        if max_per_second:
            self.like_inerval = float(max_parallel)/max_per_second - 0.14
        if (not max_per_second) or self.like_inerval<=0:
            self.like_inerval = 0
        self.accs = []
        self.proxies = []
        self.proxies_in_use = []
        self.proxies_bad = []
        self.total_likes = 0
        self.proxy_last_updated  = 0
        self.accs_in_use =  []

    def load_accs(self):
        while len(self.accs)!=self.max_parallel:
            new_acc, q_numbers = self.acc_db.get_ready_acc(interval=self.acc_rest_interval,
                                                           target=self.target,
                                                           target_questions=self.target_questions,
                                                           minimal_number_of_possible_likes=1,
                                                           dont=self.accs_in_use)
            proxy = self.get_available_proxy()
            if not new_acc:
                print('Not enough ready accs! Only %d accs out of possible %d will be used!'%
                      (len(self.accs),self.max_parallel))
                break
            if proxy is None:
                print 'No working proxy available!'
                break

            q_numbers = list(q_numbers)[:self.max_from_acc]
            q_list = [self.q_conversion[nr] for nr in q_numbers]
            like_data = { 'q_list': q_list,
                          'target': self.target,
                          'max_per_second': self.max_per_second}
            cl = Client(new_acc['login'], new_acc['password'], timeout=self.max_from_acc*4,
                        auto_like=like_data, real_proxy=proxy)
            t = threading.Thread(target=cl.start_auto_like, args = ())
            t.daemon = True
            t.start()

            self.accs.append(cl)
            self.accs_in_use.append(new_acc['login'])

            
    def get_target_data(self):
        res=urllib.urlopen('http://ask.fm/'+self.target)
        source = res.read()
        self._sr  = SourceReader(source, bs=True, ajaxed=True)
        self.target_likes = int(self._sr.bs.select('#profile_liked_counter')[0].text.strip())
        self.target_questions = int(self._sr.bs.select('#profile_answer_counter')[0].text.strip())
        self.AUTH_TOKEN = self._sr.get_auth_token()

        questions = self._sr.get_all_questions()
        page = 1
        print len(questions)
        while self._load_more_results(page):
            cand=self._sr.get_all_questions()
            print len(cand)
            questions.extend(cand)
            page+=1
            print 'Page', page
        self.q_conversion= list(reversed(questions))
        
    def get_available_proxy(self):
        for proxy in self.proxies:
            if not ((proxy in self.proxies_bad) or (proxy in self.proxies_in_use)):
                self.proxies_in_use.append(proxy)
                return proxy
        #if time.time()-self.proxy_last_updated>600:
        #     self.update_proxies()
        #     self.proxy_last_updated = time.time()
        #     return self.get_available_proxy()
        return None

    def update_proxies(self, n=30):
        if FRAME:
            FRAME.account_panel.liker_log.SetValue('Please wait, I have to find %d proxies for you...'%n)
        self.proxies = [False] + get_proxies(n)

    def _load_more_results(self, page):
        more_data  = urllib.urlencode( { 'time': time.strftime("%a+%b+%d+%X+UTC+%Y", time.gmtime()),
                                         'page': str(page),
                                         'authenticity_token': self.AUTH_TOKEN})
        new = self._GET('http://ask.fm/'+self.target+'/more?'  +more_data, '')[1]
        if len(new)<50:
            return False
        self._sr  = SourceReader(new, bs=False, ajaxed=False)
        return True
    
    def _GET(self, url, data):
        return self.h.request(url, 'GET', data, {},0)

    def finish_acc(self, acc):
        his_proxy = acc.real_proxy
        his_likes = acc.total_likes
        if acc.LOGIN_FAILED:
            # remove account if failed because of account suspended
            if acc.LOGIN_FAILED=='account':
                self.acc_db.del_account(acc.acc_login)
        else:
            self.total_likes+=his_likes
            dif = time.time()-self.f_time
            if FRAME:
                FRAME.account_panel.liker_log.SetValue('Likes per second: '+str(round(self.total_likes/dif,2)))
            self.acc_db.update_liked_questions(acc.acc_login, self.target, his_likes)
            self.acc_db.just_used(acc.acc_login)
            self.acc_db.save()
        if his_proxy and (acc.LOGIN_FAILED=='proxy' or his_likes/float(self.max_from_acc)<0.4):
            self.proxies_bad.append(his_proxy)
        self.accs.remove(acc)
        self.accs_in_use.remove(acc.acc_login)
        self.proxies_in_use.remove(his_proxy)
        
    def start_liking(self, target, max_likes=False):
        if not self.proxies:
            self.update_proxies()
        max_likes = max_likes if max_likes else 10000000
        if FRAME:
            FRAME.account_panel.liker_log.SetValue('Preparing question IDs...')
        self.target = target
        self.get_target_data()
        if FRAME:
            FRAME.account_panel.liker_log.SetValue('Started Liking... Wait for speed...')
        self.likes_here = 0
        self.t=time.time()
        self.f_time = time.time()
        self.total_likes = 0
        self.load_accs()
        
        while self.accs and self.total_likes<max_likes and not (FRAME and FRAME.STOP):
            to_finish = []
            for acc in self.accs:
                time.sleep(0.01)
                if (not acc.BUSY) or acc.timeout_reached():
                    to_finish.append(acc)
            for acc in to_finish:
                self.finish_acc(acc)
            if to_finish and not self.total_likes>max_likes:
                self.load_accs()
            time.sleep(0.01)
                

            
