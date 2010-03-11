from google.appengine.api import memcache, urlfetch
from google.appengine.dist import httplib
from google.appengine.ext import webapp
from itertools import repeat

class redirecthomehandler(webapp.RequestHandler):
    def get(self):
        self.redirect('http://www.iheardata.com/', permanent=False)

class errorhandler(webapp.RequestHandler):
    def get(self):
        self.error(404)

CACHE_NAMESPACE = "util.cachingFetch"
def cachingFetch(url,
                 payload=None,
                 method=urlfetch.GET,
                 headers={},
                 allow_truncated=False,
                 follow_redirects=True,
                 deadline=None,
                 trustCache=False):
    key = url
    if payload is not None:
        key += "?" + payload
    cachedResponse = memcache.get(key, CACHE_NAMESPACE)
    if cachedResponse is not None:
        if trustCache:
            return httplib.HTTPResponse(cachedResponse)
        if "Last-Modified" in cachedResponse.headers:
            headers["If-Modified-Since"] = \
                cachedResponse.headers["Last-Modified"]
        if "ETag" in cachedResponse.headers:
            headers["If-None-Match"] = cachedResponse.headers["ETag"]
    response = urlfetch.fetch(url, payload, method, headers, allow_truncated,
                              follow_redirects, deadline)
    if response.status_code == 304:
        return httplib.HTTPResponse(cachedResponse)
    memcache.set(key, response, 0, 0, CACHE_NAMESPACE)
    return httplib.HTTPResponse(response)

def rpcCallback(rpc, key, cachedResponse, responseMap):
    response = rpc.get_result()
    if response.status_code == 304:
        responseMap[key] = httplib.HTTPResponse(cachedResponse)
    else:
        memcache.set(key, response, 0, 0, CACHE_NAMESPACE)
        responseMap[key] = httplib.HTTPResponse(response)
        
def createRpcCallback(rpc, key, cachedResponse, responseMap):
    return lambda: rpcCallback(rpc, key, cachedResponse, responseMap)

def cachingFetches(urls,
                   payloads=repeat(None),
                   methods=repeat(urlfetch.GET),
                   headerss=repeat({}),
                   allow_truncated=False,
                   follow_redirects=True,
                   trustCache=False):
    responseMap = {}
    rpcs = []
    for url, payload, method, headers in zip(urls, payloads, methods, headerss):
        key = url
        if payload is not None:
            key += "?" + payload
        cachedResponse = memcache.get(key, CACHE_NAMESPACE)
        if cachedResponse is not None:
            if trustCache:
                responseMap[key] = httplib.HTTPResponse(cachedResponse)
                continue
            if "Last-Modified" in cachedResponse.headers:
                headers["If-Modified-Since"] = \
                    cachedResponse.headers["Last-Modified"]
            if "ETag" in cachedResponse.headers:
                headers["If-None-Match"] = cachedResponse.headers["ETag"]
        rpc = urlfetch.create_rpc()
        rpc.callback = createRpcCallback(rpc, key, cachedResponse, responseMap)
        urlfetch.make_fetch_call(rpc, url, payload, method, headers,
                                 allow_truncated, follow_redirects)
        rpcs.append(rpc)
    for rpc in rpcs:
        rpc.wait()
    return responseMap
