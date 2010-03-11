(ns lukeyear.util
  (:use (clojure.contrib [singleton :only [global-singleton]]
			 [fnmap :only [fnmap]]))
  (:import [com.google.appengine.api.urlfetch URLFetchServiceFactory
					      HTTPHeader
					      HTTPMethod
					      HTTPRequest]
	   [com.google.appengine.api.memcache MemcacheServiceFactory]
	   [java.net URL]))

(def *caching-urlfetch-namespace* "FETCHCACHE")
(def fetch-service
     (global-singleton #(URLFetchServiceFactory/getURLFetchService)))

(def cache-service
     (global-singleton #(doto (MemcacheServiceFactory/getMemcacheService)
			  (.setNamespace *caching-urlfetch-namespace*))))

(defn make-header-map [response]
  (let [headers (.getHeaders response)]
    (zipmap (map #(.toLowerCase (.getName %)) headers)
	    (map #(.getValue %) headers))))

(defn caching
  "Caches the value in MemCache, returning the cached value."
  [key value]
  (do (.put (cache-service) key value)
      value))

(defn make-cache-key [request]
  request)

(defn caching-urlfetch [url]
  (let [key url
	u (URL. url)
	cached-response (.get (cache-service) key)
	request (HTTPRequest. u)]
    (if-not (nil? cached-response)
      (let [cached-headers (make-header-map cached-response)]
	(if-let [last-mod (cached-headers "if-modified-since")]
	  (.setHeader request (HTTPHeader. "If-Modified-Since" last-mod)))
	(if-let [etag (cached-headers "etag")]
	  (.setHeader request (HTTPHeader. "ETag" etag)))))
    (let [response (.fetch (fetch-service) request)]
      (if (= 304 (.getResponseCode response))
	(:response cached-response)
	(caching key response)))))

(defn caching-urlfetches [requests]
  (map (fn [r]
	 (let [response (.get (:future-response r))]
	   (if (= 304 (.getResponseCode response))
	     (:response (:cached-response r))
	     (caching (:key r) response))))
       (map (fn [request]
	      (let [key (make-cache-key request)
		    cached-response (.get (cache-service) key)]
		(if-not (nil? cached-response)
		  (let [cached-headers (make-header-map cached-response)]
		    (if-let [last-mod (cached-headers "if-modified-since")]
		      (.setHeader request (HTTPHeader. "If-Modified-Since" last-mod)))
		    (if-let [etag (cached-headers "etag")]
		      (.setHeader request (HTTPHeader. "ETag" etag)))))
		{:future-response (.fetchAsync (fetch-service) request)
		 :cached-response cached-response
		 :key key}))
	    requests)))
