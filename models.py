from google.appengine.ext import db

class Item(db.Model):
    title = db.StringProperty()
    link = db.LinkProperty()
    description = db.StringProperty()
    pubDate = db.DateTimeProperty()
    length = db.IntegerProperty()
    mimeType = db.StringProperty()
    guid = db.StringProperty()

CHANGE_DATE_KEY = "the_date"
class ChangeDate(db.Model):
    date = db.DateTimeProperty()