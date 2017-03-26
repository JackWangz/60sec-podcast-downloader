'''
author: JackWangz
email : jy821022@gmail.com
last update: 2017/03/17
description: This program is used specifically for the website Scientific American's podcast page.
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
historyId = []
historyIdtoAdd = []

def add_history(id, file_name):
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
	fetch_result = requests.get(url, params=payload)

	soup = Soup(fetch_result.text.encode(sys.stdin.encoding, 'replace').decode(sys.stdin.encoding), 'html.parser')
	divArr = soup.find_all('div', attrs={"data-podcast-type": "gridded-podcast"})

	for i in range(0, len(divArr)):
		download_tag = divArr[i].find('a', attrs={"data-tooltip-bounds-id": "podcast-group"})
		podcast_id = download_tag['href'].split('fileId=')[1]
		title = filter_title(divArr[i]['data-podcast-title'])
		add_history(podcast_id, title)

def main():
	global historyId, historyIdtoAdd, idPool
	url = "https://www.scientificamerican.com/podcasts/"

	time_start = time.time()
	option = page_no_start = page_no_end = 0

	if not os.path.exists('history.txt'):
		print('create history.txt')
		open('history.txt', 'w').close()

	# read lines of Id from history records
	history_file = open('history.txt', 'r+')
	historyId = history_file.read().splitlines()

	option = input("Which way to download:\n1) Certain page\n2) A range of pages\nYour choice: ")
	if option == "1":
		while True:
			page_no_start = input("Insert a page number: ")
			if str.isnumeric(page_no_start) > 0: break
		# starting parsing url
		fetch_url(url, int(page_no_start))
	elif option == "2":

			while True:
				page_no_start = input("Starting page number: ")
				page_no_end = input("Ending page number: ")
				if str.isnumeric(page_no_start) and str.isnumeric(page_no_end):
					if int(page_no_start) > 0 and int(page_no_end) > 0:
						if int(page_no_end) > int(page_no_start): break

			for page in range(int(page_no_start), int(page_no_end)+1):
				fetch_url(url, page)

	# if there are no files need to download
	if not historyIdtoAdd:
		print("No files here need to download")
		return

	print("====================================================")	
	print("Start downloading")
	time.sleep(1)

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