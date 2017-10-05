import mechanize
from bs4 import BeautifulSoup
import names
import random
import time
from ask_utils import AccountDatabase, CaptchaSolver
import os
import clientless
import requests
from ask_utils import check_account



def valid_encoding_bad(text):
        enc={'\xd1': u'\u0143', '\xa3': u'\u0141', '\xea': u'\u0119',
              '\xd3': u'\xd3', '\xf3': u'\xf3', '\xe6': u'\u0107',
              '\xc6': u'\u0106', '\x8c': u'\u015a', '\xaf': u'\u017b',
              '\xf1': u'\u0144', '\xb3': u'\u0142', '\xca': u'\u0118',
              '\x8f': u'\u0179', '\xb9': u'\u0105', '\xa5': u'\u0104',
              '\xbf': u'\u017c', '\x9c': u'\u015b', '\x9f': u'\u017a'}
        res=''
        for char in text:
            if char in enc:
                res+=enc[char]
            else:
                res+=unicode(char)
        return res.encode('UTF-8')

def valid_encoding(text):
        if type(text)!=unicode:
            text  = text.decode('windows-1250')
        return text.encode('UTF-8')

def save_res(res, read=True):
    f=open('response.html','wb')
    if read:
        f.write(res.read())
    else:
        f.write(res)
    f.close()


class Creator:
    def __init__(self, master=CaptchaSolver(),
                 db=AccountDatabase('accounts.cpi'), profiles=AccountDatabase('profiles.db'), language='pl'):
        self.language = language
        self.language_ids = {'en':1, 'pl':10}
        self.egg=False
        self.base = 'http://ask.fm/'
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.br.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0")]
        self.profiles = profiles
        self.db = db
        self.master = master
        self.CREATING = False
        

    def scrape_profile(self, profile=False, max_questions=3250, max_likes=30000):
        ''' this function tries to scrape required info about the given profile
        Profile has to have a picture and a description! If it does not then the function returns False'''
        res = self.br.open(self.base+profile)
        bs = BeautifulSoup(res.read(), "lxml")
        try:
           profile_picture = bs.select('#profile-picture')[0]['src']
           if 'missing.jpg' in profile_picture:
               return False
        except:
            return False
        name = bs.select('.link-profile-name')[0].text
        try:
            description = bs.select('div.text-grey-dark.text-italic')[0].text
        except:
            description = ''
        try:
            link_seeds= bs.select('#profile-bio .text-italic')[1].children
        except:
            link_seeds = []
        links=[]
        for c in link_seeds:
            try:
                links.append(self.text)
            except:
                pass
        links = ' '.join(links)
        try:
            temp = bs.select('#profile-bio div')[0]
            if not temp.has_key('class'):
                city=temp.text
            else:
                raise
        except:
            city = ''
        likes = int(bs.select('#profile_liked_counter')[0].text)
        questions = int(bs.select('#profile_answer_counter')[0].text)
        #now performs some checks:
        if likes>max_likes or questions>max_questions:
            return False
        if not (description or links):
            return False
        data =  {'name': name,
                 'city':city,
                 'info':description,
                 'links':links,
                 'avatar':profile_picture,
                 'questions':0,
                 'last_time':0,
                 'login': profile
                 }
        print data
        return data
        
    def prepare_egg(self, complete_bio, random_acc):
        '''Prepares the info in self.egg which is necessary for account creation'''
        used=[]
        for n in self.db.data:
            try:
                used.append(self.db.data[n]['clone']['profile'])
            except KeyError:
                pass
        while True:
            profile = random.choice(self.profiles.data['all'])
            if profile not in used:
                egg = self.scrape_profile(profile)
                if egg:
                    break
        self.egg = egg

    def get_captcha_link(self):
        bs=BeautifulSoup(self.br2.response().read(), "lxml")
        return bs.select('img.image-captcha')[0]['src']


    def create_account(self, complete_bio=True, solve_captcha=True,
                       random_acc=False, acc_panel=False):
        val = int(acc_panel.acc_number.GetValue())
        if self.CREATING:
                print 'Already creating!'
                return False
        self.CREATING=True
        while val and not acc_panel.parent.STOP:
            res = bool(self._create_account(complete_bio, solve_captcha,
                       random_acc, acc_panel))
            #print 'It is %s that we have created an account successfully!'%res
            if res:
                val = int(acc_panel.acc_number.GetValue())-1
            if val<0:
                break
            acc_panel.acc_number.SetValue(val)
            print val
        self.CREATING=False
            
            
    def _create_account(self, complete_bio=True, solve_captcha=True,
                       random_acc=False, acc_panel=False):
        print 'Solving captcha', solve_captcha
        if acc_panel:
                self.db=acc_panel.db
        self.br2 = mechanize.Browser()
        self.br2.set_handle_robots(False)
        self.br2.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0")]
        if acc_panel:
            acc_panel.update_creator_status('Dealing with captcha...', 5)
        
        if solve_captcha :
            hma=False
            self.br2.open('http://ask.fm/signup')
        else:
            if not random.randrange(3):
                d21 = random.randrange(30)+1
                hma ='http://server%d.kproxy.com/servlet/redirect.srv/srl/ssbk/p1/signup'%d21
            else:
                hma='http://%d.hidemyass.com/ip-%d/encoded'%(random.randrange(7)+1, random.randrange(10)+1)+'/Oi8vYXNrLmZtL3NpZ251cA%3D%3D'
            print hma
            if 'kproxy' in hma:
                self.br2.open('http://server%d.kproxy.com/index.jsp'%d21)
            self.br2.open(hma)
            save_res(self.br2.response())
            
        ##################################################################################
        #Check if captcha present and get captcha link
            
        try:
            captcha_link = self.get_captcha_link()
            print 'Found Caprcha!'
            if solve_captcha==False:  #Try again here
                    return self._create_account(complete_bio, solve_captcha, random_acc, acc_panel)
        except:
            print 'No Captcha!'
            captcha_link = False
            captcha_result = False
        ####################################################################################                       
        #Solve captcha...
            
        if captcha_link:
            path = os.getcwd()+'\\clientlesscaptcha.jpg'
            image_response = self.br.open_novisit(captcha_link)
            image = image_response.read()
            f=open(path,'wb')
            f.write(image)
            f.close()

        if captcha_link and solve_captcha:
            try:
                captcha_result = self.master.solve(path)
                if not captcha_result:
                        return False
                print captcha_result
            except:
                print 'Solving captcha failed :('
                return False
        
        
           

        #####################################################################################
        #Prepare acc info...
        
        if acc_panel:
            acc_panel.update_creator_status('Preparing account info...', 50)
        
        if not self.egg:
            self.prepare_egg(complete_bio, random_acc)
        
        login = self.egg['login']
        name  = self.egg['name']
        
            
        #Generating random account data
        numbers = list('0123456789')
        spol = list('bcdfghjklmnprstwxzq')
        sam = list('aeiouy')
        random.shuffle(numbers)
        random.shuffle(spol)
        random.shuffle(sam)
        numbers = ''.join(numbers)
        spol = ''.join(spol)
        sam = ''.join(sam)
        age = random.randrange(5)+14
        print 2
        if login[-1] in numbers:
            addon = [numbers, numbers]
        elif login[-1] in sam+sam.upper():
            if login[-1].isupper():
                addon = [spol.upper(), sam.upper()]
            else:
                addon = [spol, sam]
        else:
            if login[-1].isupper():
                addon = [sam.upper(), spol.upper()]
            else:
                addon = [sam, spol]
                
        def get_addon(add, n):
            L1=len(add[0])
            L2=len(add[1])
            if n<=L1:
                return add[0][n-1]
            elif n<=L1*L2:
                return add[0][(n-1)%L1]+add[1][int(n/L1)-1]
            raise Exception('Very rare case')
        n=1 
        while True:
            invalid =bool(requests.get('http://ask.fm/users/check_username?login='+login+get_addon(addon,n)).json()['error'])
            if not invalid:
                login=login+get_addon(addon,n)
                break
            else:
                n+=1
        email=login+random.choice(numbers)+random.choice(numbers)+'@gmail.com'
        password = names.random_str(10)
        male=bool(random.randrange(2))
        t=time.localtime()
        year=t.tm_year-age
        month=random.randrange(12)+1
        day=random.randrange(27)+1
        if month>=t.tm_mon:
            year+=-1
        print 3
        ########################################################################################
        #Submit register form
        if acc_panel:
            acc_panel.update_creator_status('Registering account...', 70)
            
        fields = {'user[login]': login,
                  'user[name]': valid_encoding(name),
                  'user[password]': password,
                  'user[password_confirmation]': password,
                  'user[email]': email,
                  'user[born_at_day]': [str(day)],
                  'user[born_at_month]': [str(month)],
                  'user[born_at_year]': [str(year)],
                  'user[language_id]': [str(self.language_ids[self.language])],
                  'captcha': captcha_result,
                 }
        if not captcha_result:
            del fields['captcha']
        form_nr = 2 if hma  else 1
        self.br2.select_form(nr=form_nr)
        for field in fields:
            self.br2[field] = fields[field]
        res=self.br2.submit()
     
        # Check if everything went ok:
        if not 'account' in self.br2.geturl() and not hma:
            #Report wrong captcha
            if acc_panel:
                acc_panel.update_creator_status('Registration failed. Trying again...', 0)
            print 'Reporting wrong captcha...'
            try:
                self.master.report_last()
            except:
                print 'Clould not report wrong captcha. Cheaters!'
            return False
            
        #Perform last check:
        if not check_account(login):
            return False
            
        #Add to database
        self.db.add_account(name, login, password, email, 11, True)
        clone = self.egg
        clone['bio_complete'] = False
        clone['profile'] = login
        self.db.data[login]['clone'] = clone
        self.db.save()
        
        #Logout here...
        self.br2.select_form(nr=0)
        self.br2.submit()

        #Try to complete the info
        if complete_bio:
            if acc_panel:
                acc_panel.update_creator_status('Uploading avatar and adding desciption...', 90)
            clientless.Client(login, password, auto_complete=True).logout()

        if acc_panel:
            acc_panel.update_creator_status('Done. Your account %s is now ready to use!'%login, 100)
            acc_panel.update_acc_list()
        #return some info
        temp = self.egg
        temp['login'] = login
        temp['password'] = password
        self.egg = False
        print 'Now you have %d ready accounts!' %len(self.db.data)
        return True

        
        
            

