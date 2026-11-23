#!/bin/sh
# Export the 紹介動画 (30 s intro video) with its narration from Egatari, then lay the music under it
# as one uncut track at a lower level. Usage: sh scripts/make_video.sh /path/to/music_30s.wav [music gain, default 0.35]
set -e
rm -rf video
npx egatari@0.6.x video .
G=${2:-0.35}
ffmpeg -v error -y -i video/full.mp4 -i "$1" -filter_complex "[1:a]volume=$G[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k egatari-intro-video-30s.mp4
echo "wrote egatari-intro-video-30s.mp4"
