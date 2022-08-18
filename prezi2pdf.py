import requests
import re, os, json
from img2pdf import convert
import yt_dlp
import argparse


# ArgParse
parser = argparse.ArgumentParser(description='Download Prezi Presentations and Videos')
parser.add_argument('--url','-u',dest='url', action='store', help='Prezi URL', required=True)
parser.add_argument('--download-json','-j',dest='download_json', action='store_true', help='Download JSON file', required=False)

args = parser.parse_args()


def download_video(id):
    
    url = f"https://prezi.com/api/v5/presentation-content/{id}/"
    data = requests.get(url).json()
    try:
        os.mkdir(f"./videos")
    except FileExistsError:
        pass
    print(f"Downloading {data['meta']['title']}")
    video_url = data['meta']['video_signed_url_with_title']
    ydl = yt_dlp.YoutubeDL({'outtmpl': f'./videos/{id}.%(ext)s',
                            'merge_output_format': 'mp4', 'ignoreerrors': 'True',
                            'writethumbnail': 'True', 'retries': 100,
                            'add-header': 'user-agent:Mozilla/5.0',})
    info_dict = ydl.extract_info(video_url, download=True)
    if args.download_json:
        with open(f"./videos/{id}.json", 'w') as outfile:
            outfile.writelines(json.dumps(data, indent=4))



def download_presentation(id):
    url = f"https://prezi.com/api/v2/storyboard/frames/{id}/"
    data = requests.get(url).json()
    try:
        os.mkdir(f"./presentations")
    except FileExistsError:
        pass
    content = []
    i = 0
    total = len(data['frames'])
    for frame in data['frames']:
        r = requests.get(frame['images'][0]['urls']['png'])
        content.append(r.content)
        print(f"Downloading slide {i+1}/{total}")
        i += 1
    with open(f'presentations/{id}.pdf', 'wb') as pdf:
        pdf.write(convert(content))
    if args.download_json:
        with open(f"./presentations/{id}.json", 'w') as outfile:
            outfile.writelines(json.dumps(data, indent=4))

id = re.findall('([0-z]{12})', args.url)[0]

if "prezi.com/v/" in args.url:
    download_video(id)

elif "prezi.com/i/" in args.url:
    print("Prezi design not supported yet")

elif "prezi.com/" in args.url:
    download_presentation(id)
else:
    print("Please provide a valid prezi URL")



