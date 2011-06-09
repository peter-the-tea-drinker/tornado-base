import sys, os
INTERP = os.path.expanduser("~/env/bin/python")
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

application = tornado.wsgi.WSGIApplication([
        (r"/", MainHandler),
    ])

