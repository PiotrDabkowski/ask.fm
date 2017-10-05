import clientless
import random
import time
import traceback


class AccUpgrader:
    def __init__(self, db):
        self.db = db

    def add_answers(self, n, acc_panel=False):
        '''Adds n+-50% answers to each acc in db!'''
        accs = self.db.data.keys()
        random.shuffle(accs)
        for acc in accs:
            #Number of answers to give
            q = n+int((n/2)*(random.random()-0.5))
            
            inf = self.db.data[acc]
            try:
                print 'Starting with', acc
                c=clientless.Client(acc, inf['password'])
                c.smart_answer(q)
                inf['questions']+=q
                self.db.save()
                acc_index = acc_panel.indexes[acc]
                if acc_panel:
                    acc_panel.list.SetStringItem(acc_index, 1, str(inf['questions']))
            except Exception, err:
                print traceback.format_exc()
            try:
                c.logout()
            except:
                print acc, 'could not logout!'
            print '%s answered %d questions!'%(acc,q)
            print
        
            
            
