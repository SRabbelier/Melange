from google.appengine.ext import db

class Profile(db.Model):
  """
  """

  #:
  profile = db.StringProperty(required=True)

  #:
  path = db.StringProperty(required=True)
