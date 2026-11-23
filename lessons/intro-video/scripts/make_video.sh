#!/bin/sh
# Export the 紹介動画 (30 s intro video) with its narration from Egatari, then lay the music under it
# as one uncut track at a lower level. Usage: sh scripts/make_video.sh [music file, default music/wa-modern-30s.m4a] [music gain, default 0.35]
# The video is 30.5 s: the music fades out over 28.5–30.0 s and the logo holds 0.5 s of silence (owner 11/24).
# music/wa-modern-30s.m4a: AI-composed with ACE-Step 1.5 (MIT License), chosen and edited by the author (11/23); 96 BPM, bars every 2.5 s.
set -e
rm -rf video
npx egatari@0.6.x video .
G=${2:-0.35}
ffmpeg -v error -y -i video/full.mp4 -i "${1:-music/wa-modern-30s.m4a}" -filter_complex "[1:a]volume=$G,afade=t=out:st=28.5:d=1.5,apad[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k egatari-intro-video-30s.mp4
echo "wrote egatari-intro-video-30s.mp4"
