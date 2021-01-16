# :bug: semacrawl :bug:

A multi-threaded web crawler. The crawler just prints the sites visited and the time taken to crawl the site.

The database is in memory so it is limited in size. However, access time is much faster than using a cloud db.

## :dolphin: Requirements

The `requests` library is great for any web crawling mechanisms.

To get started, run: `pip3 install requests`

`threading` was used to create a timer for the threads. After a specified amount of time has passed, all spiders will stop and return.

