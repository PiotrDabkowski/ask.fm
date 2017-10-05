# -*- coding: cp1250 -*-
import urllib2,urllib
from bs4 import BeautifulSoup
import string
import time,random
from selenium import webdriver
from HideFox import HideFox

class LanguageNotSupported(Exception):
    pass

class Google:
    def __init__(self, language='pl'):
        self.phantom = False
        #To add new languages or sites simply edit extractors and this class will handle the rest :)
        self.extractors = {'zapytaj.onet.pl': ('Zapytaj', '.question-content', 'http://zapytaj.onet.pl/', 'pl'),
                      'www.pytano.pl': ('Pytano', '#komentarze li p', 'http://www.pytano.pl/', 'pl'),
                      'answers.yahoo.com': ('Yahoo', '.answer .content', 'answers.yahoo.com', 'en')
                      }
        self.sites = {e:[site[2] for site in self.extractors.values() if site[3]==e] for e in set([inf[3] for inf in self.extractors.values()])}
        self.set_language(language)
       
    def set_language(self, language):
        '''currently supported: en, pl'''
        if language not in self.sites:
            raise LanguageNotSupported('Language %s is not supported! Supported languages: '%language +str(self.sites.keys()))
        self.__language = language
        
    def get_url(self, query,site='', phantom=False):
        query='%20'.join(urllib.quote(self.valid_encoding(query).encode('utf8')).split())
        if site:
           if type(site)==list:
               site='%20OR%20'.join(['site:'+urllib2.quote(s) for s in site])+'%20'
           else:
               site='site:'+urllib2.quote(site)+'%20'
           if phantom:
                return site
        query=site+query
        if not phantom:
          add='&oq='+query+'&btnG=Google+Search'
        else:
            add=''
        return 'http://www.google.com/search?q='+query+add

    def get_data(self, url): 
        headers = {'User-agent':"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0"}
        req = urllib2.Request(url,None,headers)
        site = urllib2.urlopen(req)
        data = site.read()
        site.close()
        return data

    def search(self, query, site=''):
        url=self.get_url(query, site)
        links=[]
        try:
          bs=BeautifulSoup(self.get_data(url), "lxml")
        except:
            try:
               bs=BeautifulSoup(self.search2(query, site), "lxml")
               results=bs.select('h3.r a')
               for result in results:
                   link=result.attrs['href']
                   l=urllib.unquote(link).decode('utf8')
                   links.append((link, result.text.strip()))
               return links
            except KeyError:
                print('Could not bypass google block:( we need to give up')
        results=bs.select('h3.r a')
        for result in results:
            l=result['href']
            links.append((l, result.text))
        return links

    def search2(self, query, site=''):
        query=self.valid_encoding(query)
        if site:    
            query+=urllib.unquote(' '+self.get_url(query, site, True)).decode('utf8')
        if not self.phantom:
            print 'Probably google blocked our search. We need to do something!'
            print 'This method is longer but will bypass the problem'
            if not self.phantom:
                self.phantom = webdriver.Firefox()
            self.phantom.get('https://www.google.pl/')
            self.hider=HideFox(False, window_name=self.phantom.title+' - Mozilla Firefox')
            self.hider.hide()
            time.sleep(0.6+random.random())
        main_input=self.phantom.find_element_by_id('gbqfq')
        self.phantom.execute_script("document.getElementById('" +'gbqfq'+"').value = '"+self.valid_encoding(query)+"';")
        #main_input.send_keys(query)
        time.sleep(1+random.random())
        try:
           confirm=self.phantom.find_element_by_id('gbqfb')
           confirm.click()
        except:
            confirm=self.phantom.find_element_by_id('gbqfba')
            confirm.click()
        time.sleep(3)
        return self.phantom.page_source
        
    
    def valid_encoding(self, text):
        if type(text)!=unicode:
            return text.decode('windows-1250')
        return text

    def get_answers_from_link(self, link, method):
        try:
             bs=BeautifulSoup(self.get_data(link), "lxml")
             raw=bs.select(method)
             answers=[]
             n=0
             for answer in raw:
                 t=answer.text.strip()
                 if t and ('#' in method or n) and not '[LINK]' in t:
                     answers.append(t)
                 n+=1
             return answers
        except:
               pass

    def get_answers_from_links(self, links):
        total=[]
        data={k[0]:[0,0] for k in self.extractors.values()}
        for link in links:
            for url_fingerprint, extractor in self.extractors.iteritems():
                if url_fingerprint in link:
                    now, method, _, _ = extractor
                    break 
            else:
                print 'No valid extractor for:', link
                continue
            try:
               add=self.get_answers_from_link(link, method)
               total+=add
               data[now]=[data[now][0]+len(add),data[now][1]+1]
            except:
                pass
        for e in data:
            if data[e][1]>2 and not data[e][0]:
                print 'Probably the extractor for ',e, 'does not work anymore!'
        return total
    
    def answer_question(self, question):
        '''returns a list of answers for the given question'''
        sites = self.sites[self.__language]
        cands = self.search(question, site=sites)
        cands = [e for e in cands if any([site in e[0] for site in sites])]   #('zapytaj.onet.pl' in e[0]) or ('www.pytano.pl' in e[0])]
        good = []
        #print
        #print
        #print 40*'='
        #print 'Question:',question
        #print
        for cand in cands:
            if self.smart_compare(self.valid_encoding(question.strip()), self.valid_encoding(cand[1])):
                good.append(cand[0])
                #print 'GOOD: ',self.valid_encoding(cand[1]),'\n'
            else:
                #print 'BAD: ',self.valid_encoding(cand[1]),'\n'
                pass
        if not good:
            return []
        return self.get_answers_from_links(good)

    def translate_polish_letters(self,string):
        string=self.valid_encoding(string)
        translation={
                self.valid_encoding('ą'):'a',
                self.valid_encoding('ć'):'c',
                self.valid_encoding('ę'):'e',
                self.valid_encoding('ł'):'l',
                self.valid_encoding('ń'):'n',
                self.valid_encoding('ó'):'o',
                self.valid_encoding('ś'):'s',
                self.valid_encoding('ź'):'z',
                self.valid_encoding('ż'):'z',
                self.valid_encoding('Ą'):'A',
                self.valid_encoding('Ć'):'C',
                self.valid_encoding('Ę'):'E',
                self.valid_encoding('Ł'):'L',
                self.valid_encoding('Ń'):'N',
                self.valid_encoding('Ó'):'O',
                self.valid_encoding('Ś'):'S',
                self.valid_encoding('Ź'):'Z',
                self.valid_encoding('Ż'):'Z'
                }
        out=''
        for s in string:
            if s in translation:
                out+=self.valid_encoding(translation[s])
            else:
                out+=s
        return out

    def smart_compare(self,s1, s2):
        s1=self.translate_polish_letters(s1)
        s2=self.translate_polish_letters(s2)
        s1=filter(lambda x: x in string.ascii_letters+' ',s1).lower()
        s2=filter(lambda x: x in string.ascii_letters+' ',s2).lower()
        s1=s1.split()
        length=len(s1)
        score=0
        for word in s1:
            if word in s2:
                score+=1
        if float(score)/length>=0.7:
            return True
        return False

def talk(language='en'):
    g=Google(language)
    while True:
        inq = raw_input('--> ')
        print 'Samantha:', random.choice(g.answer_question(inq))
        
    
