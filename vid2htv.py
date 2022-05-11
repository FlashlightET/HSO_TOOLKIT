import os

input_video='video.mp4'
output_video='output'
#os.system('run things that get the info (ffprobe) to set defaults for gui')


#then set res to input res and stuff in the GUI and do GUI stuff


#width=whatever the user put for size x in the GUI
#height=whatever the user put for size y in the GUI
#fps=whatever the user put for fps in the GUI
#palette=colors (32 by default? a global palette is generated with this. 32 includes the transparent color)
#dither=ffmpeg dither options, sierra2 by default
#acd=audio codec, (low quality PCM, vorbis, wma)
#asr=sample rate, automatically set to 22.5k for vorbises under 50kbps
#abr=audio bitrate, 32k by default for vorbis
#preprocess variables=stuff

palette=32
width=256
height=192
fps=15
dither='sierra2'
acd='vorbis'
asr=22050
abr=32







#os.system('clear and create working directories')
os.system('mkdir working\\')
os.system('mkdir working\\in')
os.system('mkdir working\\out')
#extract palette
os.system('ffmpeg -i "'+input_video+'" -lavfi scale=256x192,fps=1,palettegen=max_colors='+str(palette)+' "working\\palette.png" -y')
#extract frames
os.system('ffmpeg -i "'+input_video+'" -vf scale='+str(width)+'x'+str(height)+',fps='+str(fps)+' "working\\in\\frame_%04d.png" -y')
#make it funky
os.system('ffmpeg -i "working\\in\\frame_%04d.png" -i "working\\palette.png" -lavfi paletteuse=dither='+dither+' "working\\outgif.gif" -y')
#extract frames again
os.system('ffmpeg -i "working\\outgif.gif" "working\\out\\frame_%04d.png" -y')
#preprocess audio
#os.system('ffmpeg -i "'+input_video+'" #uhhh stuff I'll figure it out tonight it involves sample formats and stuff and interpolation stuff i dotmng (autocorrect sucks) know from the top of my head    "working\\preprocessed_audio.wav" -y')
os.system('ffmpeg -i "'+input_video+'" "working\\preprocessed_audio.wav" -y')

#process audio
if acd=='vorbis':
    if abr<50: asr=22050
    os.system('ffmpeg -i "working\\preprocessed_audio.wav" -vn -c:a vorbis -b:a '+str(abr)+'k -ac 1 -ar '+str(asr)+' "working\\processed_audio.mkv" -y')
if acd=='wma':
    os.system('ffmpeg -i "working\\preprocessed_audio.wav" -vn -c:a wma -b:a '+str(abr)+'k -ac 1 -ar '+str(asr)+' "working\\processed_audio.mkv" -y')
if acd=='pcm':
    os.system('ffmpeg -i "working\\preprocessed_audio.wav" -vn -c copy "working\\processed_audio.mkv" -y') #itll just use the pcm settings from preprocessing
#mux
#this first one is incase the 2nd one fails due to no stream
os.system('ffmpeg -r '+str(fps)+' -i "working\\out\\frame_%04d.png" -c:v libvpx-vp9 -crf 12 -speed 4 -an "'+output_video+'.webm" -y')

os.system('ffmpeg -r '+str(fps)+' -i "working\\out\\frame_%04d.png" -i "working\\processed_audio.mkv" -map 0:v:0 -map 1:a:0 -c:v libvpx-vp9 -crf 12 -speed 4 -c:a libopus -b:a 64k "'+output_video+'.webm" -y')
#rename
os.system('del "'+output_video+'.htv"')
os.system('rename "'+output_video+'.webm" "'+output_video+'.htv"')
