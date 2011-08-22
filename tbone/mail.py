# Basic email stuff.

def send_html_email(subject, html, to_addr, from_local_addr='noreply'):
    import config
    from_addr = from_local_addr+'@'+config.email_domain
    conn= get_mail_conn()
    msg = make_msg(to_addr, from_addr, subject, html, msg_type = 'html')
    conn.sendmail(from_addr, to_addr, msg.as_string())
    conn.close()

class DummyMailbox(object):
    def sendmail(self, from_addr, to_addr, msg):
        import time
        time.sleep(3)
        print 'from',from_addr
        print 'to',to_addr
        print msg

    def close(self):
        pass

class BrokenDummyMailbox(object):
    def sendmail(self,*args,**kwargs): 
        raise IOError
    def close(self): 
        pass

def get_mail_conn():
    import smtplib
    import config
    server = config.email_server
    user = config.email_user
    password = config.email_password
    secure = config.email_secure

    if server == 'dummy':
        return DummyMailbox()
    if server == 'broken':
        return BrokenDummyMailbox

    if secure:
        conn = smtplib.SMTP(server, 587)
        conn.ehlo()
        conn.starttls()
        conn.ehlo()
    else:
        conn = smtplib.SMTP(server)
    conn.login(user, password)
    return conn

def make_msg(to_addr, from_addr, subject, text, msg_type = 'html'):
    from email.MIMEText import MIMEText
    msg = MIMEText(text,msg_type)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    return msg

