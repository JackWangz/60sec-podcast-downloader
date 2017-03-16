try:
	import threading
except ImportError:
	import dummy_threading as threading
import requests, urllib, sys, os, re, queue, time, math
from html.parser import HTMLParser
from bs4 import BeautifulSoup as Soup

num_threads = 3
num_files = 0
idPool = queue.Queue()
#Scientific American 60-Second Science Podcast
url = "https://www.scientificamerican.com/podcast/podcast.mp3"
historyId = {}
historyIdtoAdd = []
threads = []

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
					#https://www.scientificamerican.com/podcast/podcast.mp3

def add_history(id, file_name):
	if id not in historyId:
		print("store %s to history" % id)
		historyIdtoAdd.append(id+'\n')
		idPool.put(dict(id=id, name=file_name))

# Inspect acceptable characters on Windows
def filter_title(title):
	regex = re.compile(r"[\\/:*?<>| ]", re.X)
	return regex.sub("", title)

def add_thread():
	thrd = threading.Thread(target=download_podcast, args=(idPool))
	thrd.setDaemon(True)
	thrd.start()

def download_podcast():
	global idPool, url, num_files
	while True:
		data = idPool.get()
		id   = data['id']
		name = data['name']+".mp3"
		payload = {'fileId': id}
		print("downloading: %s" % name)
		r = requests.get(url, params=payload, stream=True)
		with open(name, "wb") as f:
			for chunk in r.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)
		num_files+=1
		idPool.task_done()

def fetch_url(url, page_no):
	payload = {'page': page_no}
	return requests.get(url, params=payload)

def main():
	time_start = time.time()
	url = "https://www.scientificamerican.com/podcasts/"
	r = fetch_url(url, 2)
	#http://marsray.pixnet.net/blog/post/61040521-%5Bpython3%5D-%E7%94%A8-python3-%E5%AF%AB%E4%B8%80%E5%80%8B%E7%B6%B2%E8%B7%AF%E7%88%AC%E8%9F%B2
	if not os.path.exists('history.txt'):
		print('create history.txt')
		open('history.txt', 'w').close()

	history_file = open('history.txt', 'r+')
	historyId = history_file.read().splitlines()

	soup = Soup(r.text.encode(sys.stdin.encoding, 'replace').decode(sys.stdin.encoding), 'html.parser')
	divArr = soup.find_all('div', attrs={"data-podcast-type": "gridded-podcast"})

	for i in range(0, len(divArr)):
		title = filter_title(divArr[i]['data-podcast-title'])
		download_tag = divArr[i].find('a', attrs={"data-tooltip-bounds-id": "podcast-group"})
		podcast_id = download_tag['href'].split('fileId=')[1]
		add_history(podcast_id, title)

	print("====================================================")	
	print("Start downloading")

	# set threads
	for i in range(num_threads):
		thrd = threading.Thread(target=download_podcast)
		thrd.setDaemon(True)
		thrd.start()

	# write history
	history_file.writelines(historyIdtoAdd)
	history_file.close()

	idPool.join()
	time_end = time.time()
	print("====================================================")	
	# (1)number of files
	print('%s files downloaded.' % num_files)
	# (2)total download time
	print('Total downloading duration: %s' % round(time_end-time_start))

if __name__ == "__main__":
	main()