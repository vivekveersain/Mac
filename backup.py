#"""
#@author: Vievk V. Arya [github.com/vivekveersain]
#"""

import subprocess
import time
import json

class TimeMachine:
    def __init__(self):
        print("Initializing Time Machine Utility...")

    def backup_disk_exists(self):
        return len(subprocess.getoutput("mount | grep '/Volumes/Seagate'")) > 0

    def run(self):
        self.phase = "Starting..."
        self.mount = None
        self.start_time = time.time()
        subprocess.getoutput("tmutil startbackup")
        while self.phase != "BackupNotRunning": self.check_progress()
        if self.mount is not None: self.eject()

    def _time_conversion(self, secs):
        if secs == "Calculating": return "__:__"
        secs = int(secs)
        if secs < 3600: return '%02d:%02d' % (secs//60, secs%60)
        return '%02d:%02d:%02d' % (secs//3600, (secs//60)%60, secs%60)

    def check_and_parse(self):
        status = subprocess.getoutput("tmutil status").replace('"','').replace("\n"," ")[23:]
        while '  ' in status: status = status.replace("  ", " ")
        status = status.replace("Progress = {", "").replace("; };", ";").replace(" = ", '" : "').replace('; ','", "').replace("{ ", '{"').replace(";",'"').replace(', "}', "}")
        return json.loads(status)

    def parse_data(self, data):
        units, r = list('BKMGTP'), 0
        while data > 1024:
            data = data/1024
            r += 1
        return '%.2f%s' % (data, units[r])

    def check_progress(self):
        status = self.check_and_parse()
        self.phase = status.get("BackupPhase", "BackupNotRunning")
        if self.phase == "BackupNotRunning": return
        elif self.phase == "Copying" or self.phase == "Finishing":
            raw_percent = float(status.get("_raw_Percent", -100))*100
            TimeRemaining = self._time_conversion(status.get(" TimeRemaining", "Calculating"))
            TimeElapsed = self._time_conversion(time.time() - self.start_time)
            processed_data = self.parse_data(int(status.get("bytes", -10)))
            total_data = self.parse_data(int(status.get("totalBytes", -10)))
            processed_files = status.get("files", -99)
            total_files = status.get("totalFiles", -99)
            self.mount = status.get("DestinationMountPoint", None)

            line = '%s...: %.2f%% %s<%s %s/%s Files []%s/%s]   ' % (self.phase,
                                                                    raw_percent,
                                                                    TimeElapsed,
                                                                    TimeRemaining,
                                                                    processed_files,
                                                                    total_files,
                                                                    processed_data,
                                                                    total_data)
        elif self.phase == "ThinningPreBackup": line = "Preparing..."
        elif self.phase == "ThinningPostBackup": line = "Cleaning..."
        else: line = self.phase + '...'

        print("\r%s" % line, end = '')
        time.sleep(1)

    def eject(self):
        print("\nTrying to eject...")
        print(subprocess.getoutput('diskutil eject "%s"' % self.mount))

engine = TimeMachine()
if engine.backup_disk_exists(): engine.run()
else: print("Backup disk NOT mounted!")
