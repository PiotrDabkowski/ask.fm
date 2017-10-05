import subprocess
try:
    import win32gui
    HideFox = False
except:
    class dummy:
        def __init__(self, *args):
            pass
        def __getattr__(self, a):
            def f(*a):
                return []
            return f
    HideFox = dummy
    
if not HideFox:
  class HideFox:
    def __init__(self, exe='firefox.exe', window_name=False):
        self.exe = exe
        if window_name:
            self.hwnd = win32gui.FindWindow(0,window_name)
        elif exe:
           self.get_hwnd()
        else:
            raise ValueError('You need to give either exe name or window name. Please!')
        
    def get_hwnd(self):
      win_name = self.get_win_name(self.exe)
      self.hwnd = win32gui.FindWindow(0,win_name)
      return self.hwnd

    def hide(self):
        win32gui.ShowWindow(self.hwnd, 6)
        win32gui.ShowWindow(self.hwnd, 0)

    def show(self):
        win32gui.ShowWindow(self.hwnd, 5)
        win32gui.ShowWindow(self.hwnd, 3)
        
    def add(self, iterable):
        res=iterable[0]
        iterable=iterable[1:]
        for e in iterable:
            res+=e
        return res
    
    def get_win_name(self, exe):
        '''simple function that gets the window name of the process with the given name'''
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        raw=subprocess.check_output('tasklist /v /fo csv', startupinfo=info).split('\n')[1:-1]
        data={}
        for proc in raw:
            try:
                proc=eval('['+proc+']')
                if proc[0] in data:
                    data[proc[0]].append(proc[8])
                else:
                    data[proc[0]]=[proc[8]] 
            except:
                pass
        freqs=[]
        values=data.values()
        values= self.add(values)
        for w in values:
            freqs.append([len([e for e in values if e==w]),w])
        no_window=sorted(freqs)[-1][-1]
        try:
            win_names=data[exe]
            for win_name in win_names:
                if win_name!=no_window:
                    return win_name
            raise ValueError('Process with the given name does not have any windows!')
        except KeyError:
           raise ValueError('Could not find a process with name '+exe)


