import requests
import re
from img2pdf import convert

input_url = input("Enter prezi url: ")
id = re.findall('([0-z]{12})', input_url)[0]

url = f"https://prezi.com/api/v2/storyboard/frames/{id}/"
data = requests.get(url).json()
content = []
i = 0
for frame in data['frames']:
    r = requests.get(frame['images'][0]['urls']['png'])
    content.append(r.content)
    i+=1
with open(f'{id}.pdf', 'wb') as pdf:
    pdf.write(convert(content))
