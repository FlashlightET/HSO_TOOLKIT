import PySimpleGUI as sg
import os
import subprocess
import shutil
sg.theme('DarkAmber')
sg.theme_background_color('#9AC7F5')
sg.theme_text_color('#000000')
sg.theme_button_color('#9AC7F5')
sg.theme_input_background_color('#894AD3')
sg.theme_input_text_color('#F0AEF1')
BtTexCol='#BF4AD4'
TexBGCol='#9AC7F5'
print(vars(sg.theme))
input_video='video.mp4'
output_video='output'
palette=32
width=256
height=192
fps=15
dither='sierra2'
acd='vorbis'
asr=22050
abr=32



layout =   [[sg.Text('Input video',background_color=TexBGCol, size=(10, 1)),sg.Input(key='ipath'), sg.FileBrowse(key='input',target='ipath')],
            [sg.Text('Output video',background_color=TexBGCol, size=(10, 1)),sg.Input(key='opath'), sg.FileSaveAs(key='output',target='opath')],
            [sg.Text('                              Palette size',background_color=TexBGCol, size=(24, 1)),sg.Input(key='palette', size=(12, 1),default_text='32')],
            [sg.Text('                               Video width',background_color=TexBGCol, size=(24, 1)),sg.Input(key='width', size=(12, 1),default_text='256')],
            [sg.Text('                              Video height',background_color=TexBGCol, size=(24, 1)),sg.Input(key='height', size=(12, 1),default_text='192')],
            [sg.Text('                                Frame rate',background_color=TexBGCol, size=(24, 1)),sg.Input(key='fps', size=(12, 1),default_text='15')],
            [sg.Text('                              Video dither',background_color=TexBGCol, size=(24, 1)),sg.Combo(['bayer','heckbert','floyd_steinberg','sierra2','sierra2_4a'],key='dither', size=(12, 1),default_value='sierra2')],
            [sg.Text('                    Audio compression     ',background_color=TexBGCol, size=(24, 1)),sg.Combo(['vorbis','wma','pcm'],key='acd',size=(12, 1),default_value='wma')],
            [sg.Text('                     Audio sample rate    ',background_color=TexBGCol, size=(24, 1)),sg.Combo(['8000','11025','16000','22050','24000','32000','44100','48000'],key='asr', size=(12, 1),default_value='44100')],
            [sg.Text('                            Audio bit rate',background_color=TexBGCol, size=(24, 1)),sg.Combo(['8k','16k','24k','32k','40k','48k','56k','64k','80k','96k','128k'],key='abr', size=(12, 1),default_value='32k')],
            [sg.Text('Ready!',background_color=TexBGCol,size=(69,1),key='status')],
            [sg.Button('Go!'), sg.Button('Exit')]]

window = sg.Window('vid2htv', layout)

def update_text(window,text):
    window['status'].update(text)
    window.refresh()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Go!':
        update_text(window,'Setting up variables...')
        input_video=values['input'].replace('/','\\')
        output_video=values['output'].replace('/','\\')
        palette=int(values['palette'])
        width=int(values['width'])
        height=int(values['height'])
        fps=int(values['fps'])
        dither=values['dither']
        acd=values['acd']
        asr=int(values['asr'])
        abr=int(values['abr'][:-1])
        update_text(window,'Clearing old work directory...')
        try:
            shutil.rmtree('working\\')
        except OSError:
            pass
        update_text(window,'Generating new work directory...')
        subprocess.run('mkdir working\\',shell=True)
        subprocess.run('mkdir working\\in',shell=True)
        subprocess.run('mkdir working\\out',shell=True)
        update_text(window,'Extracting palette...')
        #extract palette
        subprocess.run('ffmpeg -i "'+input_video+'" -lavfi scale=256x192,fps=1,palettegen=max_colors='+str(palette)+' "working\\palette.png" -y',shell=True)
        #extract frames
        update_text(window,'Extracting frames from video...')
        subprocess.run('ffmpeg -i "'+input_video+'" -vf scale='+str(width)+'x'+str(height)+',fps='+str(fps)+' "working\\in\\frame_%04d.png" -y',shell=True)
        #make it funky
        update_text(window,'Running color reduction...')
        subprocess.run('ffmpeg -i "working\\in\\frame_%04d.png" -i "working\\palette.png" -lavfi paletteuse=dither='+dither+' "working\\outgif.gif" -y',shell=True)
        #extract frames again
        update_text(window,'Extracting frames from gif...')
        subprocess.run('ffmpeg -i "working\\outgif.gif" "working\\out\\frame_%04d.png" -y',shell=True)
        #preprocess audio
        #subprocess.run('ffmpeg -i "'+input_video+'" #uhhh stuff I'll figure it out tonight it involves sample formats and stuff and interpolation stuff i dotmng (autocorrect sucks) know from the top of my head    "working\\preprocessed_audio.wav" -y')
        update_text(window,'Preprocessing audio...')
        subprocess.run('ffmpeg -i "'+input_video+'" "working\\preprocessed_audio.wav" -y',shell=True) #Audio preprocessing is not done yet...
        #process audio
        update_text(window,'Processing audio...')
        if acd=='vorbis':
            if abr<50: asr=22050
            subprocess.run('ffmpeg -i "working\\preprocessed_audio.wav" -vn -b:a '+str(abr)+'k -ac 1 -ar '+str(asr)+' "working\\processed_audio.ogg" -y',shell=True)
            os.system('del working\\processed_audio.mkv')
            os.system('rename "working\\processed_audio.ogg" "processed_audio.mkv"') #This should NOT be necessary.
        if acd=='wma':
            subprocess.run('ffmpeg -i "working\\preprocessed_audio.wav" -vn -b:a '+str(abr)+'k -ac 1 -ar '+str(asr)+' "working\\processed_audio.wma" -y',shell=True)
            os.system('del working\\processed_audio.mkv')
            os.system('rename "working\\processed_audio.wma" "processed_audio.mkv"') #This should NOT be necessary.
        if acd=='pcm':
            subprocess.run('ffmpeg -i "working\\preprocessed_audio.wav" -vn -c copy "working\\processed_audio.mkv" -y',shell=True) #itll just use the pcm settings from preprocessing
        #mux
        #this first one is incase the 2nd one fails due to no stream
        #subprocess.run('ffmpeg -r '+str(fps)+' -i "working\\out\\frame_%04d.png" -c:v libvpx-vp9 -crf 12 -speed 4 -an "'+output_video+'.webm" -y')
        update_text(window,'Muxing video...')
        subprocess.run('ffmpeg -r '+str(fps)+' -i "working\\out\\frame_%04d.png" -i "working\\processed_audio.mkv" -map 0:v:0 -map 1:a:0 -c:v libvpx-vp9 -crf 12 -speed 4 -c:a libopus -b:a 64k "'+output_video+'.webm" -y',shell=True)
        #rename
        update_text(window,'Removing old htv if exists...')
        subprocess.run('del "'+output_video+'.htv"',shell=True)
        update_text(window,'Renaming webm to htv...')
        goofy_goober='rename "'+output_video+'.webm" "'+output_video.split('\\')[-1]+'.htv"'
        print(goofy_goober)
        subprocess.run(goofy_goober,shell=True)
        update_text(window,'Done!')

window.close()
