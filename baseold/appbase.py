import config
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base

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
    orm.Base.metadata.create_all(orm.engine)
    return tornado.wsgi.WSGIApplication(urls)

def tornado_serve(urls,debug=False,cookie_secret=None):
    import tornado.ioloop
    import tornado.web
    application = tornado.web.Application(
            urls,
            debug=debug,
            cookie_secret=cookie_secret,
            xsrf_cookies=True,
            static_path = config.STATIC
            )
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

