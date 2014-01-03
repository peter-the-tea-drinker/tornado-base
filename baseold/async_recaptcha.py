# Copyright (c) 2011 mikecrawford, jabronson, and ben.maurer, and Peter Row.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this 
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
# to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# based on recaptcha.client.captcha, by mikecrawford, jabronson, and ben.maurer

API_SSL_SERVER="https://www.google.com/recaptcha/api"
API_SERVER="http://www.google.com/recaptcha/api"
VERIFY_SERVER="www.google.com"

class RecaptchaResponse(object):
    def __init__(self, is_valid, error_code=None):
        self.is_valid = is_valid
        self.error_code = error_code


# calls callback with RecaptchaResponse
def tornado_async_submit(recaptcha_challenge_field,
                 recaptcha_response_field,
                 private_key,
                 remoteip,
                 callback):
    """
    Submits a reCAPTCHA request for verification. Returns RecaptchaResponse
    for the request

    recaptcha_challenge_field -- The value of recaptcha_challenge_field from the form
    recaptcha_response_field -- The value of recaptcha_response_field from the form
    private_key -- your reCAPTCHA private key
    remoteip -- the user's ip address
    """
    from tornado.httpclient import HTTPRequest, AsyncHTTPClient
    from tornado.httputil import url_concat
    import urllib

    if not (recaptcha_response_field and recaptcha_challenge_field and
            len (recaptcha_response_field) and len (recaptcha_challenge_field)):
         callback(RecaptchaResponse (is_valid = False, error_code = 'incorrect-captcha-sol'))
         return

    def encode_if_necessary(s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        return s

    # setup a callback for the request to call
    def handle_response(response):
        return_values = response.body.splitlines()
        return_code = return_values[0]
        if (return_code == "true"):
             callback( RecaptchaResponse (is_valid=True) )
        else:
             callback( RecaptchaResponse (is_valid=False, error_code = return_values [1]))

    # make an async request, then the callback will be called.
    params =  {
            'privatekey': encode_if_necessary(private_key),
            'remoteip' :  encode_if_necessary(remoteip),
            'challenge':  encode_if_necessary(recaptcha_challenge_field),
            'response' :  encode_if_necessary(recaptcha_response_field),
            }

    url = url_concat("http://%s/recaptcha/api/verify" % VERIFY_SERVER, params)

    request = HTTPRequest(url, headers ={
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "reCAPTCHA Python Async"
            })

    AsyncHTTPClient().fetch( request, handle_response )


