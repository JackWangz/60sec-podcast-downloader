import requests, urllib, sys
from html.parser import HTMLParser
from bs4 import BeautifulSoup as Soup

class PodcastParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.inLink = False
		self.dataArray = []
		self.countLanguages = 0
		self.lasttag   = None
		self.lastname  = None
		self.lastvalue = None

	def handle_starttag(self, tag, attrs):
		prevUrl = "https://www.scientificamerican"
		if tag == 'a':
			for name, value in attrs:
				if name == 'href':
					fullFileUrl = prevUrl + value;
					print(fullFileUrl)
					#downloadPodcast(fullFileUrl, "test.mp3")
					#https://www.scientificamerican.com/podcast/podcast.mp3
					
def download_podcast(id, file_name):
	local_filename = "C:\\Users\\JackWang\\Downloads\\60-sec Science\\"+file_name+".mp3"
	url = "https://www.scientificamerican.com/podcast/podcast.mp3"
	payload = {'fileId': id}
	r = requests.get(url, params=payload, stream=True)
	with open(local_filename, "wb") as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk:
				f.write(chunk)
	print("Downloaded: "+local_filename)
	return local_filename

def fetch_url(url, page_no):
	payload = {'page': page_no}
	return requests.get(url, params=payload)

if __name__ == "__main__":
	url = "https://www.scientificamerican.com/podcasts/"
	r = fetch_url(url, 1)
	#http://marsray.pixnet.net/blog/post/61040521-%5Bpython3%5D-%E7%94%A8-python3-%E5%AF%AB%E4%B8%80%E5%80%8B%E7%B6%B2%E8%B7%AF%E7%88%AC%E8%9F%B2
	soup = Soup(r.text.encode(sys.stdin.encoding, 'replace').decode(sys.stdin.encoding), 'html.parser')
	divArr = soup.find_all('div', attrs={"data-podcast-type": "gridded-podcast"})

	for i in range(0, len(divArr)):
		title = divArr[i]['data-podcast-title'].replace(' ', '')
		download_tag = divArr[i].find('a', attrs={"data-tooltip-bounds-id": "podcast-group"})
		podcast_id = download_tag['href'].split('fileId=')[1]
		download_podcast(podcast_id, title)

	print('download completed...')

