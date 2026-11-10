#!/bin/sh
# Export the CM silent from Egatari, then lay the original music under it as one uncut track
# (owner 11/7). Usage: sh scripts/make_video.sh /path/to/full_15s.wav
set -e
rm -rf video
npx egatari@0.6.x video .
ffmpeg -v error -y -i video/full.mp4 -i "$1" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest egatari-cm-15s.mp4
echo "wrote egatari-cm-15s.mp4"
