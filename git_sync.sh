"""
@author: Vievk V. Arya [github.com/vivekveersain]
"""

cd /Users/vivekarya/Github/
cp /Users/vivekarya/.bash_profile /Users/vivekarya/Github/Mac/bash_profile

for dir in */
do
	echo ""
	echo "==> $dir"
	cd $dir
	rm .DS_Store 2> /dev/null
	git pull
	git add .
	#git status
	git commit -m "Minor Changes!"
	git push
	cd ..

done

cd
