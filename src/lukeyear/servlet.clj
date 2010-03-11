(ns lukeyear.servlet
  (:gen-class :extends javax.servlet.http.HttpServlet)
  (:require [lukeyear feeds update])
  (:use compojure.http
	[clojure.contrib prxml]))

(defroutes lukeyear
  (GET "/update"
       (lukeyear.update/update))
  (GET "/feeds/atom"
       (lukeyear.feeds/atom))
  (GET "/feeds/rss"
       (lukeyear.feeds/rss))
  (GET "/*"
       (with-out-str
	 (prxml [:html
		 [:head [:title "hello"]]
		 [:body [:h1 "Hello World"]]]))))

(defservice lukeyear)
