from common import SOURCE_URL, HOSTNAME, BASE_PATH
from datetime import datetime
from google.appengine.ext import db
from models import Item, ChangeDate, CHANGE_DATE_KEY
from util import cachingFetch, cachingFetches
import feeds
import itertools
import re

LINE_PATTERN = r'\s*(\d\d\d):\s*<a href="(.*mp3)".*?>(.*)</a>(.*)<br>'

def updateStore():
    page = cachingFetch(SOURCE_URL)
    ChangeDate(key_name=CHANGE_DATE_KEY,
               date=datetime.strptime(page.getheader('last-modified'),
                                        "%a, %d %b %Y %H:%M:%S %Z")).put()
    tuples = (m.groups() for m in (re.match(LINE_PATTERN, line) for line in
                                   page.readlines()) if m != None)
    urls = dict(("http://" + HOSTNAME + BASE_PATH + tup[1], tup)
                for tup in tuples)
    responses = cachingFetches(urls.iterkeys(),
                               methods=itertools.repeat("HEAD"),
                               trustCache=True)
    db.put([makeItem(urls[url], responses[url]) for url in urls.iterkeys()])
    feeds.clearCache()
    
def makeItem(tup, response):
    mp3path = BASE_PATH + tup[1]
    mp3url = "http://" + HOSTNAME + mp3path
    guid = makeGuid(mp3path)
    return Item(key_name=guid,
                title=tup[0],
                link=mp3url,
                description=tup[2].rstrip() + tup[3].rstrip(),
                pubDate=datetime.strptime(response.getheader('last-modified'),
                                          "%a, %d %b %Y %H:%M:%S %Z"),
                length=int(response.getheader('content-length')),
                mimeType=response.getheader('content-type'),
                guid=guid)

def makeGuid(mp3path):
    return "tag:lukeyear.iheardata.com," + "2010-03-12" + ":" + HOSTNAME + mp3path
