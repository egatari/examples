#!/bin/sh
# Export the 30 s CM for learners (no voice) from Egatari and lay the music under it as one uncut track.
# music/wa-modern-30s.m4a: AI-composed with ACE-Step 1.5 (MIT License) from the settings of the 15 s take 3 the author chose (11/24), made 30 s long (11/25); 96 BPM, bars every 2.5 s. It fades out over 28.5–30.0 s under the logo.
# Usage: sh scripts/make_video.sh [music file, default music/wa-modern-30s.m4a]
set -e
rm -rf video
npx egatari@0.6.x video .
ffmpeg -v error -y -i video/full.mp4 -i "${1:-music/wa-modern-30s.m4a}" -filter_complex "[1:a]afade=t=out:st=28.5:d=1.5,apad,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest egatari-cm-30s-learner.mp4
echo "wrote egatari-cm-30s-learner.mp4"
