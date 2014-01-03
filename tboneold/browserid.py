import tornado.ioloop
import tornado.web

# ssh -i key.pem ec2-user@ec2-xx-xx-xx-xx.yyyy.amazonaws.com


# how to - Cache-Control: public, max-age=31536000 ?


database = {} # Just keep swimming, swimming, swimming.

# all attrs. recieve JSON. JSON-to-attrs. process attr. 
# example: setX = "onX(x)"

domain = 'localhost:8888'


class MainHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        return database.get(user_id,None)

    def get(self):
        user = self.get_current_user()
        print 'user',user
        if user is None:
            self.render('browserid.html',
            user="no user")
        else:
            self.render('browserid.html' ,
                    user=user)


    @tornado.web.asynchronous
    def post(self):
        from tornado.httpclient import AsyncHTTPClient, HTTPRequest
        from tornado.httputil import url_concat
        assertion = self.get_argument('assertion','')
        audience = domain
        url = "https://browserid.org/verify"
        url = url_concat(url, dict(assertion=assertion,audience=audience))
        request = HTTPRequest(
                url,
                validate_cert=True,
                ca_certs='../../Certificates.pem',
                )
        # You don't need ca_certs (you can comment out the arg), but if you
        # don't use them you the request to the verifier (browserid.org) isn't
        # secure.
        #
        # Your ca_certs in Chrome are under:
        #   Chrome - Preferences - Under the hood - Manage Certificates
        # You probably want to export the system roots to PEM format.
        # But I'm not a security expert.
        
        AsyncHTTPClient().fetch(request, callback=self.on_response)

    def on_response(self, response):
        import json
        response_dict = json.loads(response.body)
        print 'got',response_dict
        if not ((response_dict['status']=='okay') and
                (response_dict['audience']==domain)):
            self.write({'user-data':'error'})
            self.finish()
            return
        self.set_secure_cookie('user',response_dict['email'])
        database[response_dict['email']]=response_dict
        self.write({'user-data':'Welcome, your data: '+str(response_dict)})
        self.finish()

class LogoutHandler(tornado.web.RequestHandler):
    def post(self):
        self.set_cookie("user",'')
        self.write({"user-data":'Logged OUT!'})


urls = [('/',MainHandler),
        ('/logout',LogoutHandler)]

def tornado_serve():
    STATIC = os.path.expanduser('~/repos/ExampleTBone/static')
    UIMODULES = os.path.expanduser('~/repos/TBone/tbone/uimodules.py')
    import shutil
    tbonejs = os.path.join(os.path.dirname(__file__),'tbone.0.js')
    shutil.copy(tbonejs, STATIC)

    import uimodules
    application = tornado.web.Application(
            urls,
            debug=True,
            cookie_secret="ABCDEFG",
            xsrf_cookies=True,
            static_path=STATIC,
            ui_modules=uimodules,
            )
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    import os
    pid = os.fork()
    if pid:
        tornado_serve()
    else:
        import webbrowser
        webbrowser.get().open_new_tab('http://localhost:8888')

