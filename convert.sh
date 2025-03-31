#!/bin/bash

DOWNLOADS_DIR=~/Downloads
OUTPUT_DIR=~/Downloads/converted

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Convert images to .jpg
for img in "$DOWNLOADS_DIR"/*.webp; do
    if [[ -f "$img" ]]; then
        filename=$(basename -- "$img")
        extension="${filename##*.}"
        filename="${filename%.*}"
        ffmpeg -i "$img" "$OUTPUT_DIR/${filename}.jpg" -y
        echo "Converted: $img -> ${filename}.jpg"
        rm "$img"
    fi
done

# Convert videos to .mp4
for vid in "$DOWNLOADS_DIR"/*.{mp4,webm}; do
    if [[ -f "$vid" ]]; then
        filename=$(basename -- "$vid")
        extension="${filename##*.}"
        filename="${filename%.*}"
        ffmpeg -i "$vid" "$OUTPUT_DIR/${filename}.mp4" -y
        echo "Converted: $vid -> ${filename}.mp4"
        rm "$vid"
    fi
done

echo "Conversion complete! Files are in $OUTPUT_DIR"
cp "$OUTPUT_DIR"/* "$DOWNLOADS_DIR/"
rm -rf  "$OUTPUT_DIR"