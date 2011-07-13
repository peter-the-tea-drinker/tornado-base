# security notes:
#
# * login should use https, but I'm not enforcing it here. This means it needs
#   rewrite rules to make it secure.
#
# * use brcrypt to store user passwords. This is important, as a users password
#   may be re-used for something more valuable than a Twitter clone
#
# * try to avoid timing attacks. Don't use "database.get(password), or simple
#   string comparisms (password == password)
#
# * dont' trust user headers. This can extend to request.host, which can be 
#   faked. (note, this is usually inconsequental ... but don't take it as
#   gospel that request.host is your website).

import sqlalchemy as s
from appbase import orm

class User(orm.Base):
    __tablename__ = 'user'
    id = s.Column(s.Integer, primary_key=True)
    name = s.Column(s.String)
    email = s.Column(s.String, unique=True)
    valid = s.Column(s.Boolean, nullable=False)
    password_hash = s.Column(s.String(60))
    permissions = s.Column(s.Integer, nullable=False)
    can_spam = s.Column(s.Boolean, nullable=False)

    def __init__(self, name, email, password = None, permissions = 0, 
            valid = False, can_spam=False):
        self.name = name
        self.email = email
        self.permissions = permissions
        self.can_set_password(password)
        self.valid = valid
        self.can_spam=can_spam

    def can_set_password(self,password):
        import bcrypt
        import config
        if password is None:
            self.password_hash = None
        else:
            self.password_hash = bcrypt.hashpw(password,config.BCRYPT_SALT)

    def __repr__(self):
        return '<User %r>' % (self.name)

class MagicToken(orm.Base):
    __tablename__ = 'user_magichash'
    # no, token is not saved, as it's dangerous. token = s.Column(s.String(43))
    secret_token_hash = s.Column(s.String(43),primary_key=True) # 16**20 = plenty
    user_id = s.Column(s.ForeignKey('user.id'), nullable=False)
    expiry_time = s.Column(s.Integer, nullable=False)
    can_set_password = s.Column(s.Boolean, nullable=False)
    validate_user = s.Column(s.Boolean, nullable=False)
    next_page = s.Column(s.String, nullable=False)

    def __init__(self, user_id, dt, can_set_password, validate_user,next_page = None):
        import config
        from hashlib import sha256
        import time
        import base64
        t = time.time()

        # Create a token. This is what the user will send.
        token_raw = sha256(config.COOKIE_SECRET+str(t)+str(user_id)).digest()
        # compress the token, so the URL will be smaller

        token = base64.urlsafe_b64encode(token_raw)[:-1] # rstrip the '='

        url = config.magic_token_url
        assert url.endswith('/')
        self.url = url+token
        # make it a full URL, i.e. 'www.example.com/m/asoi1231298fsfbiu312
        # Don't use request.host to make this. It's a security hole, as the
        # Host can be set by an attacker (hoping to harvest magic tokens)
        #
        # on the attacker's machine
        # req = urllib2.Request('http://example.org/forgot?email=user@example.org')
        # req.add_header('Host', 'http://www.attacker.org/')
        # r = urllib2.urlopen(req)


        # I DON'T want to query the db using "token", as that is too vulnerable
        # to timing attacks.
        secret_token_raw = sha256(token+config.COOKIE_SECRET).digest()
        secret_token_hash = base64.urlsafe_b64encode(secret_token_raw)[:-1]
        self.secret_token_hash = secret_token_hash
        # add some expiry times, etc.
        # Use seconds-since-epoch, GMT (aka UTC), to avoid brain-damaging
        # and insecure conversions.

        self.user_id = user_id
        self.expiry_time = t+dt
        self.can_set_password = can_set_password
        self.validate_user = validate_user
        self.next_page = next_page

        # A note on brute forcing COOKIE_SECRET
        #
        # Can the user steal "COOKIE_SECRET", by guessing ctime?
        #
        # A good cookie secret is at least 30 chars. That's over 10**50
        # combinations (just with [a-z,A-Z,0-9]).
        #
        # With 1000 trillion (10**15) hashes a second, on a trillion (10**12)
        # cores it would take 10**23 seconds, or ~3 * 10**15 years max (half
        # that on average)
        #
        # I'm comfortable with that for now.

def get_magic_token(token):
    import config
    from hashlib import sha256
    import base64
    # cut and paste, from _MagicToken.__init__
    secret_token_raw = sha256(token+config.COOKIE_SECRET).digest()
    secret_token_hash = base64.urlsafe_b64encode(secret_token_raw)[:-1]

    # look up using a hash, not the token.
    return orm.Session().query(MagicToken).filter_by(secret_token_hash=secret_token_hash).first()

def get_user(handler,session):
    user_id = handler.get_secure_cookie("user")
    if not user_id: return None
    return session.query(User).filter_by(id=user_id).first()

def check_login(email, password):
        if email:
            user = orm.Session().query(User).filter(User.email==email).first()
        else:
            user = None
        if user is not None:
            # checking
            password_hash = user.password_hash
            result = _check_password(password_hash,password)
        else:
            # wasting time - don't make it too easy for an attacker to know
            # if it was username or password that failed.
            _check_password('wasting','cycles')
            result = False
        if result:
            uid = user.id
        else:
            uid = None
        return result, uid

def _check_password(password_hash,password):
    import bcrypt
    import config
    if password_hash is None:
        dummy = bcrypt.hashpw(password, config.BCRYPT_SALT)
        _s_comp(dummy,dummy)
        return False
    return _s_comp(password_hash, bcrypt.hashpw(password,config.BCRYPT_SALT))

def _s_comp(s1,s2):
    "Compare in constant time"
    # see https://code.djangoproject.com/browser/django/trunk/django/utils/crypto.py
    if not len(s1)==len(s2): return False
    result = 0
    for a,b in zip(s1,s2):
        result |= ord(a) ^ ord(b)
    return result == 0



def make_fixtures():
    import config
    orm.Base.metadata.create_all(orm.engine)    
    session = orm.Session()
    admin = User('admin',config.ADMIN,permissions=2,password='abc',
            can_spam=True)
    session.add(admin)
    session.commit()
    mt = MagicToken(admin.id, 10*60, can_set_password=1, validate_user=1,
            next_page = '/')
    print mt.url
    session.add(mt)
    session.commit()
    print session.query(MagicToken).filter_by(secret_token_hash=mt.secret_token_hash).first()
    print session.query(User).first()

