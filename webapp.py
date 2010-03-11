from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from handlers import adminhandler, feedhandler
from util import errorhandler

application = \
    webapp.WSGIApplication([(r'/admin(?:/(.*))?', adminhandler),
                            (r'/feeds(?:/(.*))?', feedhandler),
                            (r'.+', errorhandler)
                            ])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
