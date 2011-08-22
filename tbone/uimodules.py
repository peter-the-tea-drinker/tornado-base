import tornado.web

class browserID_login(tornado.web.UIModule):
    def render(self, js_on_login, js_on_fail, js_on_logout):
        return '''
    $(document).ready(function()
      {
        $("#logout").click(function(e)
            {
             e.preventDefault();
             
             $.post("/logout",
                    $.param({_xsrf:COOKIES["_xsrf"]}),%s
                   );
            });
        $("#browserid-login").click(function(e)
        {
            e.preventDefault();

            navigator.id.getVerifiedEmail(
                function(assertion) 
                    {
                     if (assertion) 
                        {
                         // selected an email address they control to sign in with.
                         $.post("",
                                $.param({assertion:assertion,_xsrf:COOKIES["_xsrf"]}),
                                %s
                               );
                        }
                    else
                        {
                        %s
                        }
                    }
                );
        });
    });'''%(js_on_logout , js_on_login, js_on_fail)
