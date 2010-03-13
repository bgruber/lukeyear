from common import SOURCE_URL
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from models import Item, ChangeDate, CHANGE_DATE_KEY
import os

PAGE_CACHE_NAMESPACE = "lukeyear.pageCache"

RSS_CACHE_KEY = "RSS_CACHE_KEY"
RSS_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %ZGMT"
def genrss():
    page = memcache.get(RSS_CACHE_KEY, PAGE_CACHE_NAMESPACE)
    if page is None:
        params = gettemplateparams()
        params['changedate'] = ChangeDate.get_by_key_name(CHANGE_DATE_KEY).date.strftime(RSS_DATE_FORMAT)
        for item in params['items']:
            item.pubDateString = item.pubDate.strftime(RSS_DATE_FORMAT)
        page = template.render(os.path.join(os.path.dirname(__file__), 'rss.xml'),
                           params)
        memcache.set(RSS_CACHE_KEY, page, 0, 0, PAGE_CACHE_NAMESPACE)
    return page

ATOM_CACHE_KEY = "ATOM_CACHE_KEY"
ATOM_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
def genatom():
    page = memcache.get(ATOM_CACHE_KEY, PAGE_CACHE_NAMESPACE)
    if page is None:
        params = gettemplateparams()
        params['changedate'] = ChangeDate.get_by_key_name(CHANGE_DATE_KEY).date.strftime(ATOM_DATE_FORMAT)
        for item in params['items']:
            item.pubDateString = item.pubDate.strftime(ATOM_DATE_FORMAT)
        page = template.render(os.path.join(os.path.dirname(__file__), 'atom.xml'),
                           params)
        memcache.set(ATOM_CACHE_KEY, page, 0, 0, PAGE_CACHE_NAMESPACE)
    return page

def gettemplateparams():
    params = {}
    params['sourceUrl'] = SOURCE_URL
    params['items'] = Item.all().order("-pubDate").fetch(365)
    return params

def clearCache():
    memcache.delete_multi([RSS_CACHE_KEY, ATOM_CACHE_KEY],
                          namespace=PAGE_CACHE_NAMESPACE)
