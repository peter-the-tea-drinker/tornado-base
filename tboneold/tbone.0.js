COOKIES=JSON.parse('{}');
jQuery.map(document.cookie.split(";"),
        function(cookie){
        cookie = cookie.split('=');
        key = cookie.shift().replace(/^\s+|\s+$/g,"");
        value = unescape(cookie.join());
        COOKIES[key]=value;
        }
)


