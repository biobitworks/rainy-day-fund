#!/bin/zsh
# usage: compress_recordings.sh OUT_DIR file1.mov file2.mov ...   (originals never modified; audio dropped)
out=$1; shift; i=1
for f in "$@"; do
  ffmpeg -nostdin -loglevel error -y -i "$f" -vf "fps=10,scale=1280:-2" -c:v libx264 -crf 30 -preset slow -pix_fmt yuv420p -an -movflags +faststart "$out/rdf_demo_$(printf %02d $i).mp4" && echo done $i
  i=$((i+1))
done
