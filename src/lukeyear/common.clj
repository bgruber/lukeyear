(ns lukeyear.common
  (:require [clojure.contrib.singleton]))

(def *item-kind* "Item")
(def changedate-key
  (clojure.contrib.singleton/global-singleton
   #(com.google.appengine.api.datastore.KeyFactory/createKey "ChangeDate" "the_date")))

(def *source-hostname* "music.columbia.edu")
(def *source-url* (str "http://" *source-hostname* "/~luke/music/year.html"))
