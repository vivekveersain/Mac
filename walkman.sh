#"""
#@author: Vievk V. Arya [github.com/vivekveersain]
#"""

python3 ~/Github/Mac/music_cleaner.py
find ~/Music -type d -empty -delete

if mount | grep -q '/Volumes/WALKMAN'
	then
		rsync ~/Music/Music/ /Volumes/WALKMAN/MUSIC/ -r --stats --human-readable --info=progress2 --info=name --ignore-existing --delete --include '*/' --include '*.mp3' --exclude '*'
		echo ''
		echo Total Files on Walkman : $(ls /Volumes/WALKMAN/MUSIC/*/*/*.mp3 | wc -l)
		if [ $1 ]
			then
			       diskutil eject WALKMAN
			fi
	else echo Walkman NOT mounted!
	fi
