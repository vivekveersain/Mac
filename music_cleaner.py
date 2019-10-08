"""
@author: Vievk V. Arya [github.com/vivekveersain]
"""
import mutagen
from mutagen.easyid3 import EasyID3
import os

class Music:
    def __init__(self, base_folder = None):
        self.base = base_folder
        
    def run(self): self.browser(self.base)
    
    def clean(self, file):
        ext = file.split(".")[-1]
        path = "/".join(file.split("/")[:-1])
        f = mutagen.File(file, easy = True)
        back = f.tags
        audio = EasyID3(file)
        unknown = {'title': [u""], 'artist':[u""], 'album':["Single Track"], 'genre':[u""]}
        flag = False
        for tag in back.keys():
            if tag in ['title', 'artist', 'album', 'genre']:
                try: audio[tag] = back[tag][0]
                except:
                    audio[tag] = unknown[tag][0]
                    flag = True
            else:
                audio.pop(tag)
                flag = True
        if flag: audio.save()
        if back.get("genre", [""])[0] == "Archive":
            path = "/Users/vivekarya/Music/Archive"
        clean_name = path + "/" + back.get("title", ["Unknown"])[0] + "." + ext
        if clean_name != file:
            print(file, '->', clean_name)
            os.rename(file, clean_name)
        elif flag: print("Metadata Edit: %s" % file)

    def browser(self, folder):
        List = os.listdir(folder)
        for l in List:
            abs_path = folder + '/' + l
            if os.path.isdir(abs_path): self.browser(abs_path)
            elif os.path.isfile(abs_path):
                if abs_path[-4:].lower() == '.mp3': self.clean(abs_path)
                else: os.remove(abs_path)

music = Music('/Users/vivekarya/Music/Music')
music.run()
