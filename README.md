A simple interface - ffmpeg script in python 
for an MKV file with a corrupted PTS/DTS.
It detects corrupted timestamps (if present)
then decides whether to copy or encode.
If file is corrupted → reconstructs the timeline correctly (with the actual FPS).

Get video info, choose CRF(depending on bitrate = adaptive CRF).

Asks for video file, subtitle file (srt) and output filename.mkv.

Built the ffmpeg command, re-encode the mkv file (if necessary), 
add subtitle file (srt) and saves as mkv file.
