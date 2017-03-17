'''
author: JackWangz
email : jy821022@gmail.com
last update: 2017/03/17
description: This prgram is specific for the website Scientific American.
'''
try:
	import threading
except ImportError:
	import dummy_threading as threading
import requests, urllib, sys, os, re, queue, time, math
from bs4 import BeautifulSoup as Soup

num_threads = 3
num_files = 0
idPool = queue.Queue()
#Scientific American 60-Second Science Podcast
historyIdtoAdd = []
threads = []

def add_history(id, file_name):
	global historyId
	if id not in historyId:
		print("store %s to history" % id)
		historyIdtoAdd.append(id+'\n')
		idPool.put(dict(id=id, name=file_name))

# Inspect acceptable characters on Windows
def filter_title(title):
	regex = re.compile(r"[\\/:*?<>|]", re.X)
	return regex.sub("", title)

def download_podcast():
	global idPool, num_files
	url = "https://www.scientificamerican.com/podcast/podcast.mp3"
	while True:
		try:
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
		except:
			print("Download file error:", sys.exc_info()[0])

def fetch_url(url, page_no):
	payload = {'page': page_no}
	return requests.get(url, params=payload)

def main():
	global historyId, historyIdtoAdd, idPool
	time_start = time.time()
	
	url = "https://www.scientificamerican.com/podcasts/"
	page_no = input("Insert a page number: ")
	fetch_result = fetch_url(url, page_no)

	if not os.path.exists('history.txt'):
		print('create history.txt')
		open('history.txt', 'w').close()

	history_file = open('history.txt', 'r+')
	historyId = history_file.read().splitlines()

	soup = Soup(fetch_result.text.encode(sys.stdin.encoding, 'replace').decode(sys.stdin.encoding), 'html.parser')
	divArr = soup.find_all('div', attrs={"data-podcast-type": "gridded-podcast"})

	for i in range(0, len(divArr)):
		download_tag = divArr[i].find('a', attrs={"data-tooltip-bounds-id": "podcast-group"})
		podcast_id = download_tag['href'].split('fileId=')[1]
		title = filter_title(divArr[i]['data-podcast-title'])
		add_history(podcast_id, title)

	# if there are no files need to download
	if not historyIdtoAdd:
		print("No files here need to download")
		return

	print("====================================================")	
	print("Start downloading")
	time.sleep(2)

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
	print('%s files downloaded' % num_files)
	print('Total downloading duration: %s secs.' % round(time_end-time_start))

if __name__ == "__main__":
	main()