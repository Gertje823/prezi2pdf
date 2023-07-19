

import requests
import re
import os
import json
from img2pdf import convert
import yt_dlp
import argparse

# ArgParse
parser = argparse.ArgumentParser(description='Download Prezi Presentations and Videos')

# Remove the '--url' argument from the parser

parser.add_argument('--download-json','-j',dest='download_json', action='store_true', help='Download JSON file', required=False)

# Remove the 'args.url' assignment

args = parser.parse_args()

# Remove the 'id' assignment from the URL

url = input("Enter the Prezi URL: ")
id = re.findall('([0-z|-]{12})', url)[0]

# Add prompt to ask for PDF name
pdf_name = input("Enter the PDF name: ")

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
    # Modify the img2pdf conversion options here
    pdf_options = {
        'resolution': 300,  # Increase the resolution (dpi) for better quality
        'jpegopt': {'quality': 100},  # Set JPEG quality to maximum (100%)
        # Add more options as needed
    }
    with open(f'presentations/{pdf_name}.pdf', 'wb') as pdf:
        pdf.write(convert(content, **pdf_options))
    if args.download_json:
        with open(f"./presentations/{id}.json", 'w') as outfile:
            outfile.writelines(json.dumps(data, indent=4))

if "prezi.com/v/" in url:
    download_video(id)

elif "prezi.com/i/" in url:
    print("Prezi design not supported yet")

elif "prezi.com/" in url:
    download_presentation(id)
else:
    print("Please provide a valid prezi URL")
