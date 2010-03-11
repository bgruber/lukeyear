from admin import updateStore
from datetime import datetime
from feeds import genrss, genatom
from google.appengine.ext import webapp
import sys

class feedhandler(webapp.RequestHandler):
    def get(self, feedtype):
        if feedtype == "rss":
            self.response.headers['Content-Type'] = 'application/rss+xml'
            self.response.out.write(genrss())
        elif feedtype == "atom":
            self.response.headers['Content-Type'] = 'application/atom+xml'
            self.response.out.write(genatom())
        elif feedtype is None or feedtype == '':
            indexhandlerget(self)
        else:
            self.error(404)

class adminhandler(webapp.RequestHandler):
    def get(self, action):
        if action == "update":
            updateStore()
        elif action is None or action == '':
            indexhandlerget(self)
        else:
            self.error(404)

def indexhandlerget(handler):
    handler.redirect('/', permanent=True)
