
#@author: Vievk V. Arya [github.com/vivekveersain]

cd /Users/vivekarya/Github/
cp /Users/vivekarya/.zshrc /Users/vivekarya/Github/Mac/zshrc

for dir in */
do
	echo ""
	echo "==> $dir"
	cd $dir
	rm .DS_Store 2> /dev/null
	git pull
	git add .
	git reset -- .DS_Store .gitattributes __pycache__
	#git status
	git commit -m "Minor Changes!"
	git push
	cd ..

done

cd
