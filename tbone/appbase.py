import config
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base

# to upgrade live
# - create an empty database (with new schema)
# - upgrade all the web apps
# - set some kind of "in_upgrade" flag
# - for all new transactions
#     - look in the new DB first.
#     - fallback to reading from the old db, and upgrade the record.
#     - post to the new DB (try "new", fallback "edit")
# - gradually move records into the new DB (upgrading).

class ORM(object):
    def __init__(self):
        self.engine = None
        self.Session = sqlalchemy.orm.sessionmaker()
        self.Base = declarative_base()

    def initialize(self,engine):
        self.engine = engine
        self.Session.configure(bind=engine)

orm = ORM()
orm.initialize(sqlalchemy.create_engine(config.DB))#, encoding='utf-8'))

sql = sqlalchemy

def wsgi_app(urls):
    import tornado.wsgi
    return tornado.wsgi.WSGIApplication(urls)

def tornado_serve(urls,debug=False,cookie_secret=None):
    import tornado.ioloop
    import tornado.web
    application = tornado.web.Application(
            urls,
            debug=debug,
            cookie_secret=cookie_secret,
            xsrf_cookies=True,
            static_path = config.STATIC,
            template_path = config.TEMPLATE
            )
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

# engine = sqlalchemy.create_engine('sqlite:///project.db')
# metadata = sqlalchemy.MetaData()
# metadata.create_all(engine) 
# python migrations/manage.py version_control sqlite:///project.db migrations
# python migrations/manage.py db_version sqlite:///project.db migrations
# python migrations/manage.py script "Add user tables" migrations

# how to migrate data:
#  
