# yt-dler-mp3-commie
YT DLer as MP3 audio intended for leftist/communist content. Don't use this script to backup revisionist garbage like Hasan Piker, Vaush, etc. (yes it will work on any YT channel). 

# Requirements
-No auth/login required to YT
-I wrote this for linux. Tweaks may be needed for other platforms
-Requires ffmpeg.
-Requires an internet connection (duh).
-Requires an additional python module: yt-dlp

# 0. Make sure you have created a python virtual environment (optional but recommended) and you have all the necessary python modules installed.
Modules to install: "pip install yt-dlp"

# 1. Create the playlist file. This command launches the Youtube channel video url extractor to output a comma-separated text file. The second script will take this as an input.
python Youtube_Channel_vidUrlExtractor.py \
  --channel-url "https://www.youtube.com/@SocialismForAll/videos" \
  --out "/media/comrade-stu/LENINKA/Audiobooks/youtubeVideoURLs.txt"

  Change the channel name and paths according to your environment/needs. 
  By default, this will create a single file containing a title and URL for EVERY SINGLE VIDEO IN THE TARGET YT CHANNEL. 
  If you don't want to download ALL of the vids as MP3 (default), you can just edit the text file to remove any you don't want (remove the entire line).
  Store this text file in the path where you want the MP3s outputted to.
  NOTE, this script does a lot of regex cleanup to make workable filenames out of the YT video titles which can contain a lot of problematic noise unless handled

# 2. Run the Playlist Audio Downloader script to pull down and transcode YT content as MP3
1. First, MODIFY LINE 7 of this script (Youtube_Playlist_Audio_Downloader.py) to match the OUTPUT path where you want the MP3s to be saved (the path where the text file lives). 
   NOTE: The script assumes your input file (you generated in step 1 above) is in this same path (recommended to leave it alone)--if it's not, modify line 8.
2. Once everything is set, run Youtube_Playlist_Audio_Downloader.py
3. What the script does: The script will iterate through every line in the text file, download a temporary video file to a folder in the path you specified, then transcode the file to MP3 and then delete the temp file.
4. Enjoy leftist content on your local media like an external hard drive (that you can plug into your car's USB port and list on drives to work), stockpile content on your home NAS, and distribute to your comrades via sneakernet.

WORKERS OF THE WORLD UNITE. ALL POWER TO THE PEOPLE!