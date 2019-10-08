"""
@author: Vievk V. Arya [github.com/vivekveersain]
"""

import mutagen
import os

class Browser:
    def __init__(self, base_folder = None, what = ''):
        self.base = base_folder
        self.what = what.lower()
        
    def run(self): self.browser(self.base)

    def browser(self, folder):
        List = os.listdir(folder)
        for l in List:
            abs_path = folder + '/' + l
            if self.what in abs_path.lower(): print(abs_path)
            if os.path.isdir(abs_path): 
                try: self.browser(abs_path)
                except: pass

what = input("What to search for?: ")
browser = Browser('/Library', what)
browser.run()
