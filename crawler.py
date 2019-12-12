import requests
import threading
import time
import sys

from html.parser import HTMLParser

############ CONFIGURATION PARAMETERS ############

# File configuration
SAVE_FILE = 'crawled' 
READ_FILE = 'to-crawl'

# Crawler configuration
NUM_SPIDERS = 3			# number of spiders
TIME_TO_RUN = 20		# running time of spiders
BUFFER_TIME = 10		# buffer time after running time expires
REQUEST_TIME = 3		# time for each request
MAX_TRIES = 2			# maximum number of tries for each request

###################### TIMER ######################

def exit_crawl():
    global TIMEOUT
    TIMEOUT = True
    time.sleep(BUFFER_TIME)
    visited_file.close()
    print("Timeout... crawling exiting...")
    sys.exit(0)

TIMEOUT = False
timer = threading.Timer(TIME_TO_RUN, exit_crawl);
timer.start()

################# FILE READ/ WRITE #################

# these methods should be synchronised across spiders

# read initial db
with open(READ_FILE, 'r') as f:
    initial_sites = set(f.read().splitlines())

visited_file = open(SAVE_FILE, 'a')
visited_file_lock = threading.Lock()

def write_to_file(data):
    visited_file_lock.acquire()
    visited_file.write(data)
    visited_file.write('\n')
    visited_file_lock.release()

################# HTML PARSING #################

def add_link_to_database(link):
    if link.startswith('http'):
        visited_sites_lock.acquire()
        if link not in visited_sites:
            add_site(link)
        visited_sites_lock.release()

class FindLinksHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for a in attrs:
                if a[0] == 'href':
                    link = a[1]
                    add_link_to_database(link)

###################### SPIDER ######################

# calls the parser module
def find_links(html_response):
    parser = FindLinksHTMLParser()
    parser.feed(html_response)

def visit(s):
    response_ok = False
    num_tries = 0
    try:
        while not response_ok and num_tries <= MAX_TRIES:
            response = requests.get(url=s, timeout=REQUEST_TIME)
            num_tries += 1
            if response.status_code == requests.codes.ok:
                response_ok = True
        find_links(response.text)
        delay = response.elapsed.total_seconds()
        add_visited_data(s, delay)
    except requests.exceptions.RequestException:
        return

def crawl():
    while not TIMEOUT:
        site = get_next_site()
        if site is None:
            time.sleep(0.2)
            continue

        visited_sites_lock.acquire()
        to_visit = site not in visited_sites
        if to_visit:
            visited_sites.add(site)
        visited_sites_lock.release()

        if to_visit:
            visit(site)

################## SET OF SITES TO VISIT/ VISITED ##################

# a set of all sites to visit
to_visit_sites_lock = threading.Lock() 
to_visit_sites = set().union(initial_sites)

# unvisited sites
def get_next_site():
    to_visit_sites_lock.acquire()
    try:
        data = to_visit_sites.pop()
    except KeyError: # no more sites to pop
        data = None
    to_visit_sites_lock.release()
    return data

def add_site(link):
    to_visit_sites_lock.acquire()
    to_visit_sites.add(link)
    to_visit_sites_lock.release()

# a set of all visited sites
visited_sites_lock = threading.Lock() 
visited_sites = set()

# visited sites
def add_visited_data(s, delay):
    data = s + '\t\t\t\t(' + str(delay*1000) + 'ms)'
    print(data)
    write_to_file(data)

###################### MAIN ######################

print("Crawler, running with", NUM_SPIDERS, "spiders for", TIME_TO_RUN + BUFFER_TIME, "seconds")
for i in range(NUM_SPIDERS):
    threading.Thread(target=crawl).start()
