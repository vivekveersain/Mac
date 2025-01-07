cd "../Shared/"

for file in *.mp3; do
  base_name="${file%.mp3}"
  output_file="output/${base_name}.mp4"
  
  # Skip if the output file already exists
  if [ -e "$output_file" ]; then
    echo "Skipping $file, $output_file already exists."
    rm "$output_file"
    # continue
  fi
  
  ffmpeg -loop 1 -i input_image.jpg -i "$file" -c:v mpeg4 -c:a aac -b:a 256k -shortest "$output_file"
  curl -d "$base_name" ntfy.sh/kaptaan
  rm "$file"
done


# Send a notification after all files are converted
curl -d "All converted!" ntfy.sh/kaptaan
