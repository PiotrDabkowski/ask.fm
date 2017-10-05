import wx, sys, os
import security
from ask_utils import easy_licence_check
import time

try:
    f=open('licence.txt','rb')
    key = f.read()
    f.close()
except:
    key = ''
    
class TextEntryDialog(wx.Dialog):
    def __init__(self, parent, title, caption):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super(TextEntryDialog, self).__init__(parent, -1, title, style=style)
        text = wx.StaticText(self, -1, caption)
        input = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        input.SetInitialSize((305, 150))
        buttons = self.CreateButtonSizer(wx.OK|wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALL, 5)
        sizer.Add(input, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(buttons, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizerAndFit(sizer)
        self.input = input
    def SetValue(self, value):
        self.input.SetValue(value)
    def GetValue(self):
        return self.input.GetValue()

if True:  # set to True to add some sort of license protection
    app = wx.App()
    if not key:
        dialog = TextEntryDialog(None, 'Please confirm your licence', 'Please enter your licence key (Anything will work for this demonstration version):')
        dialog.Center()
        if dialog.ShowModal() == wx.ID_OK:
            key = dialog.GetValue()
        else:
            sys.exit()
        dialog.Destroy()
        app.MainLoop()

    STOP=False
    easy_check =  easy_licence_check(key)
    if easy_check:
        if False and not easy_check>time.localtime():
            ex = time.strftime("%d %B %Y", easy_check)
            wx.MessageBox('This licence key has expired on %s.\n\nSorry... '%ex,'Licence', wx.OK | wx.ICON_INFORMATION)
            try:
                os.remove('licence.txt')
            except:
                pass
            STOP=True
    else:
        wx.MessageBox('Invalid key!\n\n Please check the key and try again.','Licence', wx.OK | wx.ICON_INFORMATION)
        STOP=True
    if not STOP:
        s=security.Security(key)
        f=open('licence.txt','wb')
        f.write(key)
        f.close()
        wx.MessageBox('Congratulations your bot has been activated! \n\nExpires on: '+s.expires, 'Licence', wx.OK | wx.ICON_INFORMATION)
    del app
    del wx
    
