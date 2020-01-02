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
        fname = file.split("/")[-1]
        path = "/".join(file.split("/")[:-1])
        audio = mutagen.File(file, easy = True)
        back = dict(audio.tags)
        f2 = mutagen.File(file)
        back2 = dict(f2.tags)
        flag = False
        for value in back.values():
            if "(" in value[0]: flag  = True
        for tag in back2:
            if tag not in ['APIC:FRONT_COVER', 'TPE1', 'TALB', 'TCON', 'TIT2']:
                print("Edit: ", file, tag, back2[tag])
                audio = mutagen.File(file)
                audio.tags.clear()
                audio.save()
                flag = True
                audio = mutagen.File(file, easy = True)
                break

        if flag:
            for tag in ['title', 'artist', 'album', 'genre']:
                try: audio[tag] = back[tag][0].split("(")[0].strip(" ")
                except:
                    if tag == 'album': audio[tag] = ["Single Track"]
                    else: audio[tag] = [u""]
            audio.save()

        if back.get("genre", [""])[0] == "Archive": path = "~/Music/Archive"
        clean_name = path + "/" + back.get("title", ["Unknown"])[0] + "." + ext
        if back.get("title", ["Unknown"])[0]+"."+ext != fname or flag:
            print(file, '->', clean_name)
            os.rename(file, clean_name)

    def browser(self, folder):
        List = os.listdir(folder)
        for l in List:
            abs_path = folder + '/' + l
            if os.path.isdir(abs_path): self.browser(abs_path)
            elif os.path.isfile(abs_path):
                if abs_path[-4:].lower() == '.mp3': self.clean(abs_path)
                else: os.remove(abs_path)

music = Music('~/Music/Music')
music.run()
