(ns lukeyear.update
  (:use [lukeyear.common]
	[lukeyear.util :only [caching-urlfetch caching-urlfetches make-header-map]]
	[clojure.contrib.singleton :only [global-singleton]])
  (:require [appengine.datastore :as ds])
  (:import [com.google.appengine.api.urlfetch HTTPRequest HTTPMethod]
	   [java.net URL]
	   [java.text SimpleDateFormat]))

;;  example date: Sun, 13 Sep 2009 04:03:04 GMT
(def *dateformatter*
     (SimpleDateFormat. "EEE, dd MMM yyyy HH:mm:ss z"))

(defn make-guid [mp3path]
	   (str "tag:iheardata.com," ":/lukeyear/" *source-hostname* mp3path))

(defn puts [entitymaps]
  (.put (ds/datastore) (map ds/map->entity entitymaps)))

(defn make-item-map [group headers mp3url]
  (let [mp3path (nth group 2)
	guid (make-guid (nth group 2))]
    {:kind *item-kind*
     :name guid
     :title (nth group 1)
     :link mp3url
     :description (str (.trim (nth group 3))
		       (.trim (nth group 4)))
     :pubDate (.parse *dateformatter* (headers "last-modified"))
     :length (headers "content-length")
     :mimeType (headers "content-type")
     :guid guid}))

(defn update []
  (let [page-response (caching-urlfetch *source-url*)
	groups (re-seq #"\s*(\d\d\d):\s*<a href=\"(.*mp3)\".*?>(.*)</a>(.*)<br>"
		       (String. (.getContent page-response)))
	mp3urls (map #(str "http://" *source-hostname* (nth % 2)) groups)
	headerss (map make-header-map
		      (caching-urlfetches
		       (map #(HTTPRequest. (URL. %) HTTPMethod/HEAD) mp3urls)))]
    ;; put in the changedate
    (ds/put
     (doto (com.google.appengine.api.datastore.Entity. (changedate-key))
       (.setProperty
	"date"
	(.parse *dateformatter*
		((make-header-map page-response) "Last-Modified")))))
    ;; put in the data about the individual items
    (puts (map make-item-map groups headerss mp3urls)))
  ;; return an "ok" HTTP response code
  200)