# The user lib needs to be told about the database
# - make the tables
# - connect to the db for login / logout



# http://www.apache.org/licenses/LICENSE-2.0
# based on https://github.com/bdarnell/tornado/blob/master/demos/blog/blog.py#L105

import sqlalchemy as s
import tornado.escape
import tornado.auth
from appbase import orm
class User(orm.Base):
    __tablename__ = 'user'
    id = s.Column(s.Integer, primary_key=True)
    name = s.Column(s.String(50))
    email = s.Column(s.String(150), unique=True)
    permissions = s.Column(s.Integer)

    def __init__(self, name, email, permissions = 0):
        self.name = name
        self.email = email
        self.permissions = permissions

    def __repr__(self):
        return '<User %r>' % (self.name)

def get_user(handler,session):
    user_id = handler.get_secure_cookie("user")
    if not user_id: return None
    return session.query(User).filter_by(id=user_id).first()

class LoginHandler(tornado.web.RequestHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()
    
    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Google auth failed")
        session = orm.Session()
        user_row = session.query(User).filter_by(email=user["email"]).first()
        if user_row is None:
            user_row = User('New User',user['email'],0)
            session.add(user_row)
            session.commit()
        user_id = user_row.id
        self.set_secure_cookie("user", str(user_id))
        self.redirect(self.get_argument("next", "/"))

class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))

urls =  [
        (r"/logout",LogoutHandler),
        (r"/login", LoginHandler),
        ]

def make_fixtures():
    import config
    orm.Base.metadata.create_all(orm.engine)    
    session = orm.Session()
    admin = User('admin',config.ADMIN,2)
    session.add(admin)
    session.commit()
    print session.query(User).first()

