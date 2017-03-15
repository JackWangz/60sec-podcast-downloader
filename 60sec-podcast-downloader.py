try:
	import threading
except ImportError:
	import dummy_threading as threading
import requests, urllib, sys, os, queue, time
from html.parser import HTMLParser
from bs4 import BeautifulSoup as Soup

num_threads = 2
idPool = queue.Queue()
lock = threading.Lock()

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

def add_history(id, file_name):
	if id not in historyId:
		print("store %s to history" % id)
		historyIdtoAdd.append(id)
		idPool.put(dict(id=id, name=file_name))

def add_thread():
	thrd = threading.Thread(target=download_podcast, args=(idPool))
	thrd.setDaemon(True)
	thrd.start()

def download_podcast(pool):
	global lock
	lock.acquire()
	#local_filename = "C:\\Users\\JackWang\\Downloads\\60-sec Science\\"+file_name+".mp3"
	url = "https://www.scientificamerican.com/podcast/podcast.mp3"
	data = pool.get()
	id   = data['id']
	name = data['name']
	payload = {'fileId': id}
	print("downloading: %s.mp3" % name)
	r = requests.get(url, params=payload, stream=True)
	#with open(local_filename, "wb") as f:
	with open(name, "wb") as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk:
				f.write(chunk)
	print("downloaded: %s.mp3 " % name)
	lock.release()

def fetch_url(url, page_no):
	payload = {'page': page_no}
	return requests.get(url, params=payload)

if __name__ == "__main__":
	url = "https://www.scientificamerican.com/podcasts/"
	r = fetch_url(url, 1)
	#http://marsray.pixnet.net/blog/post/61040521-%5Bpython3%5D-%E7%94%A8-python3-%E5%AF%AB%E4%B8%80%E5%80%8B%E7%B6%B2%E8%B7%AF%E7%88%AC%E8%9F%B2
	if not os.path.exists('history.txt'):
		print('create history.txt')
		open('history.txt', 'w').close()
	historyId = {}
	historyIdtoAdd = []
	
	threads = []
	file = open('history.txt', 'r+')

	soup = Soup(r.text.encode(sys.stdin.encoding, 'replace').decode(sys.stdin.encoding), 'html.parser')
	divArr = soup.find_all('div', attrs={"data-podcast-type": "gridded-podcast"})
	for i in range(0, len(divArr)):
		title = divArr[i]['data-podcast-title'].replace(' ', '')
		download_tag = divArr[i].find('a', attrs={"data-tooltip-bounds-id": "podcast-group"})
		podcast_id = download_tag['href'].split('fileId=')[1]
		#download_podcast(podcast_id, title)
		add_history(podcast_id, title)

	#起thread
	for i in range(2):
		thrd = threading.Thread(target=download_podcast, args=(idPool), name='thread-'+str(i))
		thrd.start()
	time.sleep(2)

	#for loop download by queue裡的id
	#idPool.join()
	print('download completed...')