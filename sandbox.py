import traceback
import copy
import sys


#thats a bit primitive...
def execute(code, allow_exec=False, allow_import=False):
    import clientless
    d = clientless.__dict__
    try:
        if 'import ' in code and not allow_import:
            raise Exception('import not allowed!') 
        if ('exec ' in code or 'exec(' in code) and not allow_exec:
            raise Exception('exec and eval not allowed!')
        if not allow_exec: 
            code='eval=1;__builtins__["eval"]=1;'+code
        exec(code,d,d)
    except:
        return traceback.format_exc()
    del locals()['clientless']
    del sys.modules['clientless']
    return None


    
