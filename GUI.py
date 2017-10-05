import wx
import wx.html2
from wx.lib.intctrl import IntCtrl
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import sys
import random
import os
import traceback
import time
from ask_utils import *

while True: # set to true to allow license check!
    try:
        f = open('licence.txt','rb')
        key = f.read()
        f.close()
        ch = easy_licence_check(key)
        assert os.path.exists('licence.txt') or ch and ch>time.localtime()
        break
    except:
        if 'activate_licence' in globals():
            reload(activate_licence)
        else:
            import activate_licence
ch = time.localtime()


import clientless
import threading
import cPickle
from clientless_creator import Creator
import clientless_liker
clientless_liker.Client = clientless.Client
import upgrade_accs 


VERSION = '1.1'



    
def save_data(path,data):
    f=open(path,'wb')
    cPickle.dump(data,f,protocol=2)
    f.close()

def load_data(path):
    f=open(path,'rb')
    data=cPickle.load(f)
    f.close()
    return data



UPDATED=False

def update_accounts(progress):
    global UPDATED
    db = AccountDatabase()
    #br = mechanize.Browser()
    #br.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0")]
    todel = []
    size=len(db.data)
    n=0
    for login in db.data:
        n+=1
        try:
            res = check_account(login)
            if res is False:
                todel.append(login)
                continue
            elif res is None:
                raise
            db.data[login]['likes'], db.data[login]['questions'] = res
            if 100*n/size!=100:
               progress.Update(100*n/size,login)
        except:
            print 'Wtf'
    for login in todel:
        del db.data[login]
        print 'DELETED: ',login
    db.save()
    UPDATED=True
    progress.Destroy()
    progress.Close()
    print 'end'


if 0:
   APP=wx.App()
   progress = wx.ProgressDialog("ASK.FM - Updating account information...","", style = wx.PD_CAN_ABORT| wx.PD_APP_MODAL| wx.PD_ELAPSED_TIME| wx.PD_REMAINING_TIME)
   t = threading.Thread(target=update_accounts, args = (progress,))
   t.daemon = True
   t.start()
   APP.MainLoop()
   print 1
   while not UPDATED:
       time.sleep(0.01)
   print 2
   


class PasswordDialog(wx.Dialog):
    def __init__(self, parent, id=-1, title="ASK.fm"):
        wx.Dialog.__init__(self, parent, id, title, size=(320, 145))
        self.CentreOnScreen()
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.label = wx.StaticText(self, label="Please enter your DeathByCaptcha login and password:")

        self.login_label =wx.StaticText(self, label="Login   ")
        self.login = wx.TextCtrl(self, value="", size=(240, 20), style=wx.TE_PROCESS_ENTER)

        self.password_label =wx.StaticText(self, label="Password")
        self.password = wx.TextCtrl(self, value="", size=(240, 20), style=wx.TE_PROCESS_ENTER)

        self.okbutton = wx.Button(self, label="OK", id=wx.ID_OK)
        self.h_login = wx.BoxSizer(wx.HORIZONTAL)
        self.h_login.Add(self.login_label)
        self.h_login.Add(self.login,0, wx.LEFT, 15)

        self.h_password = wx.BoxSizer(wx.HORIZONTAL)
        self.h_password.Add(self.password_label)
        self.h_password.Add(self.password,0, wx.LEFT, 5)

        
        self.mainSizer.Add(self.label, 0, wx.ALL, 5 )
        self.mainSizer.Add(self.h_login, 0, wx.ALL, 5 )
        self.mainSizer.Add(self.h_password, 0, wx.LEFT , 5 )

        self.buttonSizer.Add(self.okbutton, 0, wx.ALL| wx.ALIGN_RIGHT, 5 )
        
        self.mainSizer.Add(self.buttonSizer, 0, wx.ALL, 0)
        self.Bind(wx.EVT_BUTTON, self.onOK, id=wx.ID_OK)
        self.Bind(wx.EVT_TEXT_ENTER, self.onOK)
        self.SetSizer(self.mainSizer)
        self.result = None

    def onOK(self, event):
        password = self.password.GetValue()
        login = self.login.GetValue()
        self.result = {'login': login,
                       'password': password
                       }
        print self.result
        self.Destroy()

    

def sup(event):
    frame.account_panel.browser.RunScript('document.kupa="lol";')
    frame.account_panel.browser.LoadURL('http://www.ask.fm/')
    prev_title = frame.account_panel.browser.GetCurrentTitle()
    frame.account_panel.browser.RunScript("document.title = document.cookie")
    frame.account_panel.browser.RunScript("funcs")
    #cookies = frame.account_panel.browser.GetCurrentTitle()
    frame.account_panel.browser.RunScript("document.title = %s" % prev_title)
    frame.account_panel.browser.RunScript("document.cookie = \""+cook+"\"")
    
class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
        
class AccountPanel(wx.Panel):
    def __init__(self, parent):
        super(AccountPanel, self).__init__(parent)
        self.db = AccountDatabase()
        
        #Some Variables
        self.parent = parent
        self.c=False
        self.UPGRADER_SHOWN = True
        self.LIKING = False
        self.ANSWERING = False
        self.CREATING = False
        self.selected=False
        self.captcha_solver = False
        self.BUSY = False
        self.indexes = {}
        self.last_error = 0
        self.allowed_error_interval = 30 # If last error was more than this number of seconds before then it will be ignored

        #Viewer
        self.browser = wx.html2.WebView.New(self)
        

        #Creator and Upgrader Boxes
        account_creator = wx.StaticBox(self, label="Account creator")
        account_upgrader  = wx.StaticBox(self, label="Account upgrader")

        
        
        # LIKER --------
      
        #Liker Box
        liker_box = wx.StaticBox(self, label="Add likes")
        
        #Liker settings
        self.liker_target = wx.TextCtrl(self)
        self.liker_target_label = wx.StaticText(self, label='Target:'+29*' ')
        
        self.likes_requested = IntCtrl(self, value=10000)
        self.likes_requested_label = wx.StaticText(self, label='Number of likes to add:')
        
        self.likes_per_account = IntCtrl(self, value=75)
        self.likes_per_account_label = wx.StaticText(self, label='Likes per account:'+9*' ')
        
        #Liker status
        self.start_liking_btn = wx.Button(self, label = 'Like!')
        self.start_liking_btn.Bind(wx.EVT_BUTTON, self.start_liking)
        self.likes_added = wx.TextCtrl(self, size=(90,20),style = wx.TE_READONLY)
        self.likes_added.SetValue('0')
        likes_added_info = wx.StaticText(self, label='Target\'s likes: ')
        self.liker_progress  = wx.Gauge(self, range=100)
        
        #Liker log
        self.liker_log =  wx.TextCtrl(self, style = wx.TE_READONLY|wx.TE_MULTILINE| wx.TE_BESTWRAP)
        
        
        #List
        self.list = AutoWidthListCtrl(self)
        self.list.SetMaxSize((240,2000))
        self.list.InsertColumn(0, 'Login', width=110)
        self.list.InsertColumn(1, 'Questions', width = 70)
        self.list.InsertColumn(2, 'Likes',width = 60)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_acc_select)
        self.on_list = []
        self.update_acc_list()
        
            
        #List buttons
        self.login_btn = wx.Button(self, label = 'Login!')
        self.login_btn.SetMaxSize((240,2000))
        self.login_btn.Bind(wx.EVT_BUTTON, self.client_login)
        self.change_mode_btn = wx.Button(self, label = 'Change mode to:\nLIKE')
        self.change_mode_btn.SetMaxSize((240,2000))
        self.change_mode_btn.Bind(wx.EVT_BUTTON, self.switch_panels)
        
        # CREATOR ---------------
        
        #Creator Settings
        self.copy_account = wx.CheckBox(self, label="Copy accounts from real ask users")
        self.copy_account.SetValue(True)
        self.copy_account.Disable()
        self.complete_acc  = wx.CheckBox(self, label="Don't add profile picture and description")
        self.solve_captcha = wx.CheckBox(self, label="Solve captcha (DeathByCaptcha account required)")
        self.acc_number = wx.Slider(self, value=10, minValue=0, maxValue=100, name = 'Number of accounts to create', style = wx.SL_LABELS)
        self.acc_number_label = wx.StaticText(self, label='Number of accounts you want to create:')

        #Creator Status
        self.start_create_btn = wx.Button(self, label = 'Create!')
        self.start_create_btn.Bind(wx.EVT_BUTTON, self.create_accounts)
        self.creator_progress = wx.Gauge(self)
        self.creator_log =  wx.TextCtrl(self, style = wx.TE_READONLY|wx.TE_MULTILINE| wx.TE_BESTWRAP)


        # UPGRADER --------------
        
        #Upgrader settings
        self.answer_all = wx.CheckBox(self, label="Answer on every account")
        self.answer_all.SetValue(True)
        self.answer_all.Bind(wx.EVT_CHECKBOX, self.answer_all_event)
        
        self.target_info = wx.StaticText(self, label='Target:')
        self.upgrader_target = wx.TextCtrl(self)
        self.upgrader_target.Hide()
        self.target_info.Hide()

        self.upgrader_order = wx.CheckBox(self, label="Start from accounts with \nsmallest number of questions.")
        
        self.number_of_questions_to_answer = IntCtrl(self, size=(45,20))
        self.number_info = wx.StaticText(self, label='Number of questions\n to answer per account:')

        self.questions_answered = wx.TextCtrl(self, size=(45,20),style = wx.TE_READONLY)
        self.questions_answered.SetValue('0')
        self.qans_info = wx.StaticText(self, label='Questions answered:')
        self.questions_answered.Hide()
        self.qans_info.Hide()
        
        
        #Upgrade Status
        self.start_upgrade_btn = wx.Button(self, label = 'Start Answering!')
        self.start_upgrade_btn.Bind(wx.EVT_BUTTON, self.upgrade_accounts)
        self.upgrader_progress  = wx.Gauge(self, range=100)
        self.upgrader_progress.Hide()
        
        #SIZERS
        
        #List sizer V + Buttons On Bottom Left Corner ( Mode + login)
        vbox1  =wx.BoxSizer(wx.VERTICAL)
        vbox1.Add(self.list,10, wx.BOTTOM | wx.TOP| wx.EXPAND, 2)
        
        bottom_left_buttons = wx.BoxSizer(wx.HORIZONTAL)
        bottom_left_buttons.Add(self.change_mode_btn, 1, flag=wx.EXPAND, border=2)
        bottom_left_buttons.Add(self.login_btn, 1, flag=wx.EXPAND)
        vbox1.Add(bottom_left_buttons, 1, wx.BOTTOM| wx.EXPAND, 2)
        
        
        
        #Creator Settings Sizer V
        creator_settings  = wx.BoxSizer(wx.VERTICAL)
        creator_settings.Add(self.acc_number_label, flag=wx.LEFT, border=10)
        creator_settings.Add(self.acc_number, flag=wx.ALL|wx.EXPAND, border=1)
        creator_settings.Add(self.copy_account, flag=wx.TOP, border=-15)
        creator_settings.Add(self.complete_acc, flag=wx.TOP, border=1)
        creator_settings.Add(self.solve_captcha, flag=wx.TOP, border=5)

        #Creator Status Sizer V
        creator_status  = wx.BoxSizer(wx.VERTICAL)
        creator_status.Add(self.start_create_btn, 
            flag=wx.LEFT|wx.ALIGN_LEFT|wx.EXPAND, border=5)
        creator_status.Add(self.creator_progress, 
            flag=wx.LEFT|wx.ALIGN_LEFT|wx.TOP|wx.EXPAND, border=5)
        creator_status.Add(self.creator_log, 
            flag=wx.LEFT|wx.TOP| wx.EXPAND, border=5)
    
        #Upgrader Settings Sizer V
        upgrader_settings  = wx.BoxSizer(wx.VERTICAL)
        upgrader_settings.Add(self.answer_all, 
            flag=wx.LEFT|wx.TOP, border=5)
        
        target_input = wx.BoxSizer(wx.HORIZONTAL)
        target_input.Add(self.target_info)
        target_input.Add(self.upgrader_target, 
            flag=wx.LEFT, border=5)  
        upgrader_settings.Add(target_input, flag=wx.LEFT|wx.TOP, border=5)
        
        upgrader_settings.Add(self.upgrader_order,
            flag=wx.LEFT|wx.TOP, border=5)
        
        number_input = wx.BoxSizer(wx.HORIZONTAL)
        number_input.Add(self.number_info)
        number_input.Add(self.number_of_questions_to_answer, flag=wx.LEFT|wx.TOP, border=7)
        upgrader_settings.Add(number_input, flag=wx.LEFT|wx.TOP, border=5)



        #Upgrader Status Sizer V
        upgrader_status  = wx.BoxSizer(wx.VERTICAL)
        upgrader_status.Add(self.start_upgrade_btn, 
            flag=wx.LEFT|wx.TOP|wx.EXPAND, border=5)

        nr_info = wx.BoxSizer(wx.HORIZONTAL)
        nr_info.Add(self.qans_info)
        nr_info.Add(self.questions_answered, flag=wx.LEFT, border=5)
        upgrader_status.Add(self.upgrader_progress, flag=wx.LEFT|wx.TOP|wx.EXPAND, border=5)
        upgrader_status.Add(nr_info, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT, border=5)
        
        # Liker Settigs Sizer V
        liker_settings = wx.BoxSizer(wx.VERTICAL)
        
        liker_target_input = wx.BoxSizer(wx.HORIZONTAL)
        liker_target_input.Add(self.liker_target_label)
        liker_target_input.Add(self.liker_target, flag=wx.LEFT, border=5)
        liker_settings.Add(liker_target_input, flag=wx.ALL, border=1)
        
        likes_requested_input = wx.BoxSizer(wx.HORIZONTAL)
        likes_requested_input.Add(self.likes_requested_label)
        likes_requested_input.Add(self.likes_requested, flag=wx.LEFT, border=5)
        liker_settings.Add(likes_requested_input, flag=wx.ALL, border=1)
        
        likes_per_account_input = wx.BoxSizer(wx.HORIZONTAL)
        likes_per_account_input.Add(self.likes_per_account_label)
        likes_per_account_input.Add(self.likes_per_account, flag=wx.LEFT, border=5)
        liker_settings.Add(likes_per_account_input, flag=wx.ALL, border=1)
        #<<<<<<<<<<<<<<<<<<
        
        # Liker Status Sizer V
        self.liker_status = wx.BoxSizer(wx.VERTICAL)
        self.liker_status.Add(self.start_liking_btn, 1, wx.EXPAND |wx.ALL, 3)
        self.liker_status.Add(self.liker_progress, 0.9, wx.EXPAND|wx.ALL, 3)
        
        self.like_info = wx.BoxSizer(wx.HORIZONTAL)
        self.like_info.Add(likes_added_info)
        self.like_info.Add(self.likes_added)
        self.liker_status.Add(self.like_info, 1, wx.ALIGN_RIGHT | wx.ALL, 3)
        self.liker_status.Hide(self.like_info, True) # Hide this info for now...
        self.liker_status.Hide(self.liker_progress, True)
        # <<<<<<<<<<<<<<<<<
        
        #Liker Log Sizer V
        liker_log_sizer = wx.BoxSizer(wx.VERTICAL)
        liker_log_sizer.Add(self.liker_log, 1, wx.EXPAND |wx.ALL, 3)
        
        #Creator Sizer H
        account_creator_sizer = wx.StaticBoxSizer(account_creator, wx.HORIZONTAL)
        account_creator_sizer.Add(creator_settings, 1, wx.EXPAND |wx.ALL, 3)
        account_creator_sizer.Add(creator_status, 1, wx.EXPAND |wx.ALL, 3)

        #Upgrader Sizer H
        account_upgrader_sizer = wx.StaticBoxSizer(account_upgrader, wx.HORIZONTAL)
        account_upgrader_sizer.Add(upgrader_settings, 1, wx.EXPAND |wx.ALL, 3)
        account_upgrader_sizer.Add(upgrader_status, 1, wx.EXPAND |wx.ALL, 3)
        
        #Liker Sizer H
        liker_sizer = wx.StaticBoxSizer(liker_box, wx.HORIZONTAL)
        liker_sizer.Add(liker_settings, 1, wx.EXPAND |wx.ALL, 3)
        liker_sizer.Add(self.liker_status, 1, wx.EXPAND |wx.ALL, 3)
        liker_sizer.Add(liker_log_sizer, 3, wx.EXPAND |wx.ALL, 3)

        #Top H Sizer (Creator + Upgrader)
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(account_creator_sizer, 1, wx.EXPAND|wx.ALL, 5)
        self.hbox1.Add(account_upgrader_sizer, 1, wx.EXPAND|wx.ALL, 5)

        #Second top H sizer - Liker
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(liker_sizer, 1, wx.EXPAND|wx.ALL, 5)
        
        
        #Bottom H Sizier (List + Viewer)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(vbox1, 1, wx.EXPAND, 0) 
        self.hbox2.Add(self.browser, 30,wx.TOP| wx.LEFT|wx.EXPAND, 2) 

        #Main V Sizer (Top H+ Bottom H)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.hbox1, 2, wx.EXPAND, 1)
        self.vbox.Add(self.hbox3, 2, wx.EXPAND, 1)
        self.vbox.Add(self.hbox2, 7, wx.EXPAND, 1)
        

        #Init Main V Sizer
        self.SetSizer(self.vbox)
        self.creator_progress.Hide()
        self.creator_log.Hide()
        self.vbox.Hide(self.hbox3, True)

    def switch_panels(self, event=1):
        try:
            if self.UPGRADER_SHOWN:
                self.vbox.Hide(self.hbox1,True)
                self.vbox.Show(self.hbox3, True)
                if not self.LIKING:
                    self.liker_status.Hide(self.like_info, True)
                    self.liker_status.Hide(self.liker_progress, True)
            else:
                self.vbox.Hide(self.hbox3, True)
                self.vbox.Show(self.hbox1,True)
                if not self.CREATING:
                    self.creator_progress.Hide()
                    self.creator_log.Hide()
                if not self.ANSWERING:
                    self.questions_answered.Hide()
                    self.upgrader_progress.Hide()
                    self.qans_info.Hide()
                self.answer_all_event(1) # <- so that the target to answer questions is displayed correctly 
        except:
            return False
        finally:
            label = (self.change_mode_btn.GetLabel().split('\n')[0]+'\n'+
                     ('UPGRADE' if self.UPGRADER_SHOWN else 'LIKE'))
            self.change_mode_btn.SetLabel(label)
            self.UPGRADER_SHOWN = not self.UPGRADER_SHOWN
            self.Layout() # <- Allways finish with this
        return True
            
    def start_liking(self, event):
        if self.BUSY:
            if self.LIKING:
                self.parent.STOP = True
                return None
            wx.MessageBox('Please wait...', 'Help', wx.OK | wx.ICON_INFORMATION)
            return None
        per_account = int(self.likes_per_account.GetValue())
        if per_account>130 or per_account<25:
            wx.MessageBox('Likes per account should not be smaller than 25 or greater than 130!', 'Help', wx.OK | wx.ICON_INFORMATION)
            return None
        target = self.liker_target.GetValue().strip()
        res = check_account(target)
        if not res:
            wx.MessageBox('Account with login %s does not exist!'%target, 'Help', wx.OK | wx.ICON_INFORMATION)
            return None
        if res[1]<per_account:
            info = ('Account with login %s has only %d answers. '
                    'Number of his/her answers cannot be smaller '
                    'than number of likes per account.')%(target, res[1]) 
            wx.MessageBox(info, 'Help', wx.OK | wx.ICON_INFORMATION)
            return None
        requested_likes = int(self.likes_requested.GetValue())
        possible_likes = min(per_account*len(self.indexes), 100000000)#self.db.get_total_possible_likes(target))
        if possible_likes<requested_likes:
            info = ('You have requested %d likes. The maximal possible number of likes'
                    ' I can add to this account is %d. Do you want to continue?\n\nIf you want to add more please '
                    'create more accounts or answer more questions. Note: Each account can add'
                    ' max 130 likes per hour.')%(requested_likes, possible_likes)
            res = wx.MessageBox(info, 'Help', wx.YES|wx.NO | wx.ICON_INFORMATION)
            if res!=wx.YES:
                return None
            self.likes_requested.SetValue(possible_likes)
        self.likes_added.SetValue(str(res[0]))
        t = threading.Thread(target=self._start_liking, args=(target, min(possible_likes,requested_likes), per_account))
        t.daemon = True
        t.start()
    
    def set_liking_state(self, state):
        if state:
            self.parent.STOP = False
            self.BUSY = True
            self.LIKING = True
            self.liker_status.Show(self.like_info, True)
            self.liker_status.Show(self.liker_progress, True)
            self.liker_progress.Pulse()
            self.parent.update_status_bar()
            self.start_liking_btn.SetLabel('Stop Liking')
            self.Layout()
            self.Refresh()
        else:
            self.BUSY = False
            self.LIKING = False
            self.liker_status.Hide(self.like_info, True)
            self.liker_status.Hide(self.liker_progress, True)
            self.liker_progress.SetValue(0)
            self.parent.update_status_bar()
            self.start_liking_btn.SetLabel('Like!')
            self.Layout()
            
    def _start_liking(self, target, total, per_acc):
        survived = False
        try:
            self.set_liking_state(1)
        except:
            pass
        try:
            liker = clientless_liker.LIKER(max_from_acc=per_acc)
            survived = True
            liker.start_liking(target, total)
            wx.MessageBox('Finished adding likes. "%s" has %d likes more!\n\n '%(target, liker.total_likes), 'Help', wx.OK | wx.ICON_INFORMATION)
        except:
            if survived:
                wx.MessageBox(('Errors occured. I was able to add only %d likes.\n\n'%liker.total_likes)+traceback.format_exc(),'Help', wx.OK | wx.ICON_INFORMATION)
            else:
                err = 'Strange error:\n\n '+traceback.format_exc()
                wx.MessageBox(err,'Help', wx.OK | wx.ICON_INFORMATION)
        finally:
            self.set_liking_state(0)
        
    def answer_all_event(self, event):
        if self.answer_all.GetValue():
            self.target_info.Hide()
            self.upgrader_target.Hide()
            self.upgrader_order.Show()
        else:
            self.upgrader_order.Hide()
            self.target_info.Show()
            self.upgrader_target.Show()
        if event is not 1:
            self.vbox.RecalcSizes()

    def ignore_error(self):
        if time.time()-self.last_error<self.allowed_error_interval:
            self.last_error = time.time()
            return False
        return True
        
        
    def on_acc_select(self, event):
        self.selected = event.Text
        self.browser.LoadURL('http://www.ask.fm/'+self.selected)

    def update_creator_status(self, msg='', prc=0, show=True):
        self.creator_progress.SetValue(prc)
        self.creator_log.SetValue(msg)

    def update_acc_list(self, reload_db=False):
        if reload_db:
            self.db = AccountDatabase()
        for login in sorted(self.db.data.keys(), key=lambda x: x.lower()):
            if not login in self.on_list:
                x=self.db.data[login]
                index = self.list.InsertStringItem(sys.maxint, login)
                self.list.SetStringItem(index, 1, str(x['questions']))
                self.list.SetStringItem(index, 2, str(x['likes']))
                self.on_list.append(login)
                self.indexes[login] = index

    def update_acc_likes_and_questions(self, login, ls, qs):
            index = self.indexes[login]
            print ls, qs
            self.list.SetStringItem(index, 1, str(qs))
            self.list.SetStringItem(index, 2, str(ls))
            self.db.data[login]['questions'] = qs
            self.db.data[login]['likes'] = ls
            self.db.save()
    
    def client_login(self, event):
        print len(self.db.data)
        if not 'Login.togglePopup' in self.browser.GetPageSource():
              wx.MessageBox('Please logout first!', 'Help', wx.OK | wx.ICON_INFORMATION)
              return None
        if not self.selected:
            wx.MessageBox('Please select account to login from the list!', 'Help', wx.OK | wx.ICON_INFORMATION)
            return None
        self.c = clientless.Client(self.selected, password=self.db.data[self.selected]['password'])
        self.browser.LoadURL('http://www.ask.fm/')
        self.browser.RunScript("document.cookie = \""+self.c.get_cookie()+"\"")
        self.parent.update_status_bar(acc=self.selected)
        
        
    def get_cookie(self):
        prev_title = frame.account_panel.browser.GetCurrentTitle()
        self.browser.RunScript("document.title = document.cookie")
        cookies = self.browser.GetCurrentTitle()
        self.browser.RunScript("document.title = %s" % prev_title)
        return cookies

    def create_accounts(self, event):
        if self.BUSY:
            if self.CREATING:
                self.parent.STOP = True
                wx.MessageBox('Stopped creating accounts!', 'Help', wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox('Please wait...', 'Help', wx.OK | wx.ICON_INFORMATION)
            return None
        copy =  self.copy_account.GetValue()
        complete = self.complete_acc.GetValue()
        while self.solve_captcha.GetValue():
            if self.captcha_solver:
                break
            try:
                dbc = load_data('dbc.dat')
            except:
                dbc_dialog =PasswordDialog(self)
                dbc_dialog.ShowModal()
                dbc = dbc_dialog.result
            try:
                self.captcha_solver = CaptchaSolver(dbc['login'],dbc['password'])
                self.captcha_solver_status = self.captcha_solver.solver.get_user()
                wx.MessageBox('Successfully logged in to DeathByCaptcha service!\n\n', 'Help', wx.OK | wx.ICON_INFORMATION)
                try:
                   save_data('dbc.dat', dbc)
                except:
                    pass
                break
            except:
                res = wx.MessageBox('Invalid login or password! \n\nDo you want to try again?', 'Help', wx.YES|wx.NO | wx.ICON_INFORMATION)
                if res==wx.NO:    
                   return None
        t = threading.Thread(target=self._create_account, args = (not complete, not copy))
        t.daemon = True
        t.start()

    def set_creating_state(self, state):
        if state:
            self.parent.STOP = False
            self.BUSY = True
            self.CREATING = True
            self.parent.update_status_bar()
            self.creator_progress.Show()
            self.creator_log.Show()
            self.start_create_btn.SetLabel('Stop!')
            self.vbox.Layout()
        else:
            self.BUSY = False
            self.CREATING = False
            self.parent.update_status_bar()
            self.creator_progress.Hide()
            self.creator_progress.SetValue(0)
            self.creator_log.Hide()
            self.start_create_btn.SetLabel('Create!')
            self.vbox.Layout()
            
    def _create_account(self, complete, random_acc):
        self.set_creating_state(1)
        while True:
            try:
                c = Creator(master=self.captcha_solver)
                c.create_account(complete, self.captcha_solver, random_acc, self)
                break
            except Exception:
                if not False:#self.ignore_error():
                    message = traceback.format_exc()
                    res = wx.MessageBox(message+'\n\nDo you want to continue account creation?', 'Error', wx.YES|wx.NO | wx.ICON_INFORMATION)
                    if res==wx.NO:
                         break
        self.set_creating_state(0)
        
    def upgrade_accounts(self, event):
        if self.BUSY:
            if self.ANSWERING:
                self.parent.STOP = True
                wx.MessageBox('Stopped answering questions!', 'Help', wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox('Please wait...', 'Help', wx.OK | wx.ICON_INFORMATION)
            return None
        num = int(self.number_of_questions_to_answer.GetValue())
        if num<=0:
            wx.MessageBox('Number of questions to answer must be greater than 0!', 'Help', wx.OK | wx.ICON_INFORMATION)
            return None
        if self.answer_all.GetValue():
            order = self.upgrader_order.GetValue()
            t = threading.Thread(target=self.answer_many, args = (order, num))
            t.daemon = True
            t.start()
        else:
            target = self.upgrader_target.GetValue().strip()
            if not target:
                wx.MessageBox('Please specify a target!', 'Help', wx.OK | wx.ICON_INFORMATION)
                return None
            if target not in self.db.data:
                wx.MessageBox('Target\'s login (%s) is invalid! Target must be on the account list!'%target, 'Help', wx.OK | wx.ICON_INFORMATION)
                return None
            try:
                if check_account(target):
                    t = threading.Thread(target=self.answer_single, args = (target, num))
                    t.daemon = True
                    t.start()
            except:
                wx.MessageBox('Could not login on %s. Probably account suspended or IB ban!'%target, 'Help', wx.OK | wx.ICON_INFORMATION)

    def set_answering_state(self, state):
        if state:
            self.parent.STOP = False
            self.BUSY = True
            self.ANSWERING = True
            self.parent.update_status_bar()
            self.upgrader_progress.Show()
            self.qans_info.Show()
            self.questions_answered.Show()
            self.upgrader_progress.Pulse()
            self.start_upgrade_btn.SetLabel('Stop!')
            self.Layout()
            self.Refresh()
        else:
            self.BUSY = False
            self.ANSWERING = False
            self.parent.update_status_bar()
            self.upgrader_progress.SetValue(0)
            self.qans_info.Hide()
            self.questions_answered.Hide()
            self.upgrader_progress.Hide()
            self.start_upgrade_btn.SetLabel('Start Answering!')
            self.Layout()
            self.Refresh()
            
    def answer_single(self, target, num, just_single=True):
        #Quite messy but simplifies other function!
        '''If not just_just single then 1 return value
        means error while answering -1 means error while
        logging and None means no errors'''
        if just_single:
            self.set_answering_state(1)
        try:
            client = clientless.Client(target, self.db.data[target]['password'])        
        except:
            self.BUSY = False
            self.ANSWERING = False
            self.parent.update_status_bar()
            if just_single:
                wx.MessageBox('Could not login on %s. Probably account suspended or IB ban!'%target, 'Help', wx.OK | wx.ICON_INFORMATION)
                self.set_answering_state(0)
            return -1
        try:
            client.smart_answer(num)
            client.logout()
        except:
            self.ignore_error() # I have to stop here...
            if not just_single:
                return 1
            else:
                wx.MessageBox('Error while answering questions on '+client.acc_login+'\n\n\n'+traceback.format_exc(), 'Help', wx.OK | wx.ICON_INFORMATION)
        if just_single:
            self.set_answering_state(0)
        res = check_account(client.acc_login)
        if res:
            likes, questions = res
            self.update_acc_likes_and_questions(client.acc_login, likes, questions)
        
    def answer_many(self, sort, number):
        self.set_answering_state(1)
        lis = self.db.data.keys()
        if sort:
            lis = sorted(lis, key=lambda x: self.db.data[x]['questions'])
        for target in lis:
            if self.parent.STOP:
                break
            if not check_account(target):
                continue
            q=number+int((random.random()-0.5)*number/2)
            try:
                res = self.answer_single(target, q, False) #max 25% difference
            except:
                print('A very strange error in answering multiple questions')
                res = 1
            if res and not self.ignore_error():
                wx.MessageBox('Error while answering questions on %s. Quit!'%target, 'Help', wx.OK | wx.ICON_INFORMATION)
                break
        self.set_answering_state(0)
        
                               
   
     
class Frame(wx.Frame):
    def __init__(self):
        title = 'AskBot-v%s By Piotr Dabkowski.  Expires on %s.  '%(VERSION, clientless.sec_u.expires)
        super(Frame, self).__init__(None, size=(1051,700), title=title)
        self.CentreOnScreen()
        self.account_panel = AccountPanel(self)
        self.acc = 'None'
        
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.fitem = self.fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.menubar.Append(self.fileMenu, '&File')
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MENU, self.account_panel.client_login, self.fitem)
        
        self.status_bar = wx.StatusBar(self)
        self.SetStatusBar(self.status_bar)
        self.update_status_bar('None')
        self.Show(True)
        self.SetMinSize((1050,500))

    def update_status_bar(self, acc=None):
        if acc:
            self.acc=acc
        actions = {0:'None',1:'LIKING',2:'ANSWERING',4:'CREATING'}
        val = self.account_panel.LIKING+2*self.account_panel.ANSWERING+4*self.account_panel.CREATING
        label = ('Acount online: %s  |  '
                 'Current action: %s  |  '
                 'Total number of accounts: %d')%(str(self.acc), actions[val], len(self.account_panel.indexes))
        self.status_bar.SetLabel(label)


app = wx.App(useBestVisual=True)
frame= Frame()
clientless._set_info_sink(frame)
clientless_liker.FRAME = frame
upgrade_accs.clientless._set_info_sink(frame)
app.MainLoop()
del app # sypeder fix
