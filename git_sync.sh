cd /Users/vivekarya/Github/
cp /Users/vivekarya/.bash_profile /Users/vivekarya/Github/Mac/bash_profile

for dir in */
do
	echo ""
	echo "==> $dir"
	cd $dir
	rm .DS_Store
	git pull
	git add .
	git status
	git commit -m "Minor Changes!"
	git push
	cd ..

done

cd