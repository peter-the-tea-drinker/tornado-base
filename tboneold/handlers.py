import tornado.web
from appbase import orm
import config

# introduce classes of users - real users, shadow users, and admins.

# login handler
# render - get captcha (if needed), 

class LoginHandler(tornado.web.RequestHandler):
    def render_login(self , **errors):
        # Remember to propagate "next page"
        next_page = self.get_argument("next", "/")
        # I'm using a common page (with 3 forms) for login, registration, and
        # password reset, so I'm keeping a common method here to render it.

        public_key = config.PUBLIC_RE_KEY
        use_ssl = False # set to True if this page is https
        # Note, you *can* 
        if public_key:
            # my javascript needs work ;)
            head = '''
<script type="text/javascript">
    function makeRecaptcha(div_id){
        if (document.getElementById(div_id).created !== true)
        {
            document.getElementById('new-user-re').created = false;
            document.getElementById('forgot-re').created = false;
            Recaptcha.create("%s", div_id);
            document.getElementById(div_id).created = true;
        }
    }
    function onNewUser(){makeRecaptcha('new-user-re');}
    function onForgot(){makeRecaptcha('forgot-re');}
</script>
'''%public_key
            new_user_re= '<div id="new-user-re"></div>'
            forgot_re =  '<div id="forgot-re"></div>'
            # static (no js) - should this be included for graceful
            # degredation?
            # import recaptcha.client.captcha
            #rehtml = recaptcha.client.captcha.displayhtml(public_key, use_ssl)
        else:
            head = ""
            new_user_re = ''
            forgot_re = ''

        self.render('login-form.html',title='login',new_user_re = new_user_re, 
                forgot_re=forgot_re,
                head=head, next_page=next_page,errors=errors, greeting = None)


    def recaptcha_result(self):
        import recaptcha.client.captcha, RecaptchaResponse
        private_key= config.PRIVATE_RE_KEY
        if not private_key: # for dev
            return RecaptchaResponse(True)

        recaptcha_response_field = self.get_argument('recaptcha_response_field')
        recaptcha_challenge_field = self.get_argument('recaptcha_challenge_field')
        remoteip = self.request.remote_ip
        response = recaptcha.client.captcha.submit (
                   recaptcha_challenge_field,
                   recaptcha_response_field,
                   private_key,
                   remoteip)
        return response.is_valid

    def async_recaptcha_result(self, callback):
        from async_recaptcha import async_submit, RecaptchaResponse
        private_key= config.PRIVATE_RE_KEY
        if not private_key: # for dev
             callback(RecaptchaResponse(True))
             return

        recaptcha_response_field = self.get_argument('recaptcha_response_field')
        recaptcha_challenge_field = self.get_argument('recaptcha_challenge_field')
        remoteip = self.request.remote_ip
        tornado_async_submit (
                   recaptcha_challenge_field,
                   recaptcha_response_field,
                   private_key,
                   remoteip,
                   callback)


    def get(self):
        self.render_login()

    def post(self):
        import user
        import time

        # get the form data
        password = self.get_argument('password','')
        email = self.get_argument('email','')
        #
        # if the login data is *obviously* wrong, give some feedback
        errors = []
        if not email or (not "@" in email): errors.append('Please enter a valid email.')
        if not password: errors.append('Please enter a valid password.')
        if errors:
            self.render_login(login_errors=errors)
            return
        #
        # check password
        result,uid = user.check_login(email, password)
        if result:
            self.set_secure_cookie("user", str(uid))
            self.redirect(self.get_argument("next", "/"))
        else:
            # on fail, re-render the login form
            time.sleep(1.0)
            errors.append('Login failed.')
            errors.append('Please check your email and password, and try again.')
            self.render_login(login_errors=errors)

forgot_template = """Hi, %s<p>
You just requested a new password. Please click go to 
<a href="%s">%s</a>, to log in and set a new password.<p>
If you did not request a new password, you don't have to do
anything.<p>
Have a nice day!
"""

class ForgotHandler(LoginHandler):
    # I'm using a common page for login and forgotten passwords, so inherit the
    # rendering of the page

    @tornado.web.asynchronous
    def post(self):
        self.async_recaptcha_result(self.finish_post)

    def finish_post(self, response):
        import mail
        from appbase import orm
        from user import User, MagicToken

        errors = []
        if not response.is_valid:
            errors.append('Please type the two words.')
        # get form data
        email = self.get_argument('email','')
        #
        # if email is obviously wrong, bounce it.
        if not email or (not "@" in email):
            errors.append('please enter a valid email.')
        if errors:
            self.render_login(forgot_errors=errors)
            return
        #
        # find out if the account exists. (There should be a CAPTCHA guarding
        # this, to stop people searching for accounts).
        session = orm.Session()
        user = session.query(User).filter(User.email==email).first()
        if user is None:
            # user not found, give feedback
            errors = ["email not found"]
            self.render_login(forgot_errors=errors)
            return
        else:
            self.write('Sending a new token<p>')
            try:
                mt = MagicToken(user.id, 10*60, can_set_password=1,
                        validate_user=1, next_page = self.get_argument("next", "/"))
                link = mt.url
                to_addr = email
                html=forgot_template%(user.name,link,link)
                mail.send_html_email('Password reset requested', html, to_addr)
                session.add(mt)
                session.commit()
                self.write('OK, you should get an email shortly')

            except:
                errors = ["Sorry, our email didn't work. Please try again."]
                self.render_login(forgot_errors=errors)
                raise


class NewUserHandler(LoginHandler):
    @tornado.web.asynchronous
    def post(self):
        self.async_recaptcha_result(self.finish_post)

    def finish_post(self, response):
        from appbase import orm
        from user import User

        errors = []
        password = self.get_argument('password','')
        email = self.get_argument('email','')
        TOS = self.get_argument('TOS','No')
        can_spam = (self.get_argument('CanEmail','No')=='CanEmail')
        if not password: errors.append('Please enter a valid password.')
        if not email or (not "@" in email): errors.append('Please enter a valid email.')
        if not TOS == 'TOS': errors.append('Please accept our terms of service.')
        if not response.is_valid: errors.append('Please type the two words.')
        if email and response.is_valid:
            session = orm.Session()
            user = session.query(User).filter(User.email==email).first()
            if user is not None:
                errors.append('User already exists.')
        if errors:
            self.render_login(new_user_errors=errors)
            return
        self.write('Welcome!')
        user = User(name = email.split('@')[0], email = email, password = password,
                    valid=True, can_spam = can_spam)
        session.add(user)
        session.commit()
        self.set_secure_cookie("user", str(user.id))
        self.redirect(self.get_argument("next", "/"))

# (strtolower(trim(preg_replace('/\\s+/'
class MagicHashHandler(tornado.web.RequestHandler):
    def get(self,token):
        from user import User
        print 'checking',token
        entry = self._validate(token)

        # login
        self.set_secure_cookie("user", str(entry.user_id))

        if entry.validate_user:
            session = orm.Session()
            user = session.query(User).filter_by(id=entry.user_id).first()
            user.valid = True
            session.commit()
        self.write('Welcome!<p>')
        if entry.can_set_password:
            self.render('modify-settings.html',token=token)
        else:
            next_page = entry.next_page
            self.redirect(next_page)

    def post(self,token):
        from user import User
        entry = self._validate(token)
        password = self.get_argument('password','')
        if entry.validate_user:
            self.write('Welcome, your account has been validated!')
        if not password:
            self.write('Please enter a new password.')
            self.render('change-pw.html',token=token)
            return
        self.write('setting password ... ')
        session = orm.Session()
        user = session.query(User).filter_by(id=entry.user_id).first()
        user.can_set_password(password)
        session.commit()
        self.write('New password!')
        next_page = entry.next_page
        self.redirect(next_page)


    def _validate(self,token):
        import time
        from user import get_magic_token
        entry = get_magic_token(token)
        if entry is None:
            time.sleep(1.0)
            raise tornado.web.HTTPError(404)
        if entry.expiry_time < time.time():
            err = 'Sorry, this link expired on%s'%time.ctime(entry.expiry_time)
            raise tornado.web.HTTPError(410,err)
        return entry


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))

class TOSHandler(tornado.web.RequestHandler):
    def get(self):
        # FOR GOODNESS SAKE, DON'T USE THIS. GET A LAWYER TO WRITE YOUR TOS
        # THIS IS MAY NOT BE SUITABLE FOR YOUR USE.
        self.render('tos-stub.html', mysite='Example.com', mycompany='Example',
                mycompany_long = "Example Inc.", blog = 'blog', 
                a_blog = 'a blog')

urls =  [
        (r"/logout",LogoutHandler),
        (r"/login", LoginHandler),
        (r"/forgot",ForgotHandler),
        (r"/new-user",NewUserHandler),
        (r"/tos",TOSHandler),
        (r"/m/([a-zA-Z0-9\-_]+)",MagicHashHandler),
        ]

