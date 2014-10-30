cd %~dp0
ffmpeg.exe -f image2 -framerate 30 -pattern_type sequence -start_number 0 -i "img_%05d.png" -s 300x500 -pix_fmt yuv420p -vcodec libx264 -b:v 10000k -sws_flags neighbor output.mkv
pause