(ns lukeyear.feeds
  (:refer-clojure :exclude [atom])
  (:require [appengine.datastore :as ds])
  (:use [lukeyear.common]
	[clojure.contrib.prxml :only [prxml]])
  (:import [com.google.appengine.api.datastore Query]))

(defn get-items []
  (map ds/entity->map (.asIterable (.prepare (ds/datastore) (Query. *item-kind*)))))

(defn get-changedate []
  (.get (ds/datastore) (changedate-key)))

(defn atom []
  (with-out-str
    (prxml
     [:decl! {:version "1.0" :encoding "utf-8"}]
     [:feed {:xmlns "http://www.w3.org/2005/Atom"}
      [:title "A Year in mp3s"
       [:link {:href *source-url* :rel "alternate"}]
       [:link {:href "http://lukeyear.iheardata.com/feeds/atom" :rel "self"}]
       [:updated (get-changedate)]
       [:author [:name "r. luke dubois"]]
       [:id "http://lukeyear.iheardata.com/feeds/atom"]
       (map #([:entry
	       [:title (:title %)]
	       [:link {:href (:link %)}]
	       [:link {:href (:link %)
		       :rel "enclosure"
		       :length (:length %)
		       :type (:mimeType %)}]
	       [:id (:guid %)]
	       [:updated (:pubDateString %)]
	       [:summary (:description %)]])
	    (get-items))]])))

(defn rss [])
