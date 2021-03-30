import magneturi
import requests, json
import os, time

class Torrent:
    def __init__(self):
        self.pirate_base = "/Volumes/Seagate Backup Plus Drive/Xtras/"
        self.recent_downloads = "Recent Downloads/"
        self.folders = ["Movies/", "TV Shows/"]#, self.recent_downloads]
        self.torrent_folder = self.pirate_base + "Torrent Files/"
        self.torrent_map = {}
        self._search()
        self._map_torrents()

    def get_name(self, file):
        with open(file, 'rb') as f: return magneturi.bencode.bdecode(f.read())["info"]["name"]

    def _search(self):
        self.__ds = ".DS_Store"
        content_list = []
        for folder in self.folders:
            content_list += [self.pirate_base + folder + name + "/" for name in os.listdir(self.pirate_base + folder) if name != self.__ds]
        self.hash = dict((each, folder) for folder in content_list for each in os.listdir(folder) if each != self.__ds)

    def _map_torrents(self):
        for torrent in os.listdir(self.torrent_folder):
            if torrent == self.__ds: continue
            tf = self.torrent_folder + torrent
            try:
                name = self.get_name(tf)
                if name in self.hash.keys():
                    path = self.hash[name]
                    self.torrent_map[torrent] = path
                #else: path = self.pirate_base + self.recent_downloads
            except: print(torrent)

    def distribute_loot(self):
        seeds = 0
        error = 0
        for torrent in self.torrent_map.keys():
            try:
                uri = magneturi.from_torrent_file(self.torrent_folder + torrent)
                opts = {"dir" : self.torrent_map[torrent], "bt-seed-unverified" : "true", "bt-save-metadata" : "false"}
                jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'asdf', 'method':'aria2.addUri', 'params': [[uri], opts]})
                dispatch = requests.post('http://localhost:6800/jsonrpc', jsonreq)
                seeds += 1
            except: error += 1
            print("\rSeeds: %d || Errors: %d" % (seeds, error), end = '')
            time.sleep(30)
        print("")

torrent = Torrent()
torrent.distribute_loot()
