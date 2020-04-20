scrapper()
{
  recipe="$1"
  source=$(echo $recipe | tr -d "./_" )
  recipe=$(echo $recipe | tr " " "\ " )
  outfile=$news_folder/$source.mobi
  /Applications/Calibre.app/Contents/MacOS/ebook-convert "$recipe"  "$outfile" --output-profile "kindle"
  /Applications/Calibre.app/Contents/MacOS/ebook-meta -a "Vivek Arya" "$outfile"
  osascript -e "display notification \"$source completed\" with title \"News\""
}

recipes_at="/Users/vivekarya/Library/Preferences/calibre/custom_recipes/"
news_folder="/Users/vivekarya/Downloads/News"

mkdir $news_folder
cd $recipes_at

for recipe in ./*.recipe The\ Hindu.recipe
do
  scrapper "$recipe" &
done
wait

zip $news_folder/News.zip $news_folder/*

osascript -e 'display notification "Emailing..." with title "News"'
echo "E-Mailing..."
#/Applications/Calibre.app/Contents/MacOS/calibre-smtp --relay 'smtp.live.com' --port 587 --username 'vivek.chaudhary@live.com' --password "$pwd" --encryption-method 'TLS' --subject 'News' 'vivek.chaudhary@live.com' 'vivekveersain@kindle.com' 'Enjoy.' -a $news_folder/News.zip
#/Applications/Calibre.app/Contents/MacOS/calibre-smtp --subject 'News' 'vivek.chaudhary@live.com' 'vivekveersain@kindle.com' 'Enjoy.' -a $news_folder/News.zip
osascript -e 'display notification "Cleaning..." with title "News"'
#rm -r $news_folder
