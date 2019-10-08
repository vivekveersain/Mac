"""
@author: Vievk V. Arya [github.com/vivekveersain]
"""

python /Users/vivekarya/git/Random/music_cleaner.py
find /Users/vivekarya/Music -type d -empty -delete

if mount | grep -q '/Volumes/WALKMAN'
	then
		rsync /Users/vivekarya/Music/Music/ /Volumes/WALKMAN/MUSIC/ -r --stats --human-readable --info=progress2 --info=name --ignore-existing --delete --include '*/' --include '*.mp3' --exclude '*'
		echo ''
		echo Total Files on Walkman : $(ls /Volumes/WALKMAN/MUSIC/*/*/*.mp3 | wc -l)
		if [ $1 ]
			then
			       diskutil eject WALKMAN
			fi	
	else echo Walkman NOT mounted!
	fi
