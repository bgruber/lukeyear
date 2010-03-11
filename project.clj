(defproject lukeyear "1.0.0-SNAPSHOT"
  :compile-path "war/WEB-INF/classes"
  :dependencies [[org.clojure/clojure "1.1.0"]
		 [org.clojure/clojure-contrib "1.1.0"]
		 [appengine "0.0.1-SNAPSHOT"]
		 [compojure "0.3.2"]
		 [com.google.appengine/appengine-api-1.0-sdk "1.3.1"]]
  :resource-path "war/"
  :library-path "war/WEB-INF/lib"
  :description "FIXME: write"
  :namespaces [lukeyear.servlet])
