#LightningTalks
A system for accepting votes for lightning talks.

##Table of Contents
[Bootstrapping](#bootstrapping)

* [Development](#development)
* [Production](#production)

    * [Installs](#installs)
    * [Varnish](#varnish)
    * [Nginx](#nginx)
    * [Daemons](#daemons)

[Software](#software)

* [Overview](#overview)
* [Assumptions](#assumptions)
* [Models](#models)
* [Routes](#routes)

[Tests](#tests)

##Bootstrapping
Here's how to get the thing running, either on your own local computer for development or on a server for a production deployment.

###Development
####Step Zero
You should have some Python development bits pre-installed. I love this guide from NPR Visuals. [How to Setup Your Mac to Develop News Applications Like We Do](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html)

####Step One
Install a local version of MongoDB to hold the data.
```sh
brew install mongodb
ln -sfv /usr/local/opt/mongodb/*.plist ~/Library/LaunchAgents
launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mongodb.plist
```

####Step Two
Pull down the code from Git, create a virtual environment and install requirements.
```sh
git clone git@github.com:ireapps/lightning-talks.git && cd lightning-talks
mkvirtualenv lightningtalks
pip install -r requirements.txt
```

####Step Three
Load some fake data.
```sh
fab fake_data
```

####Step Four
Run the app.
```sh
python app.py
```

###Production
####Installs
```sh
sudo apt-get install python-pip python-27 python-27-dev mongodb nginx libffi-dev libssl-dev lib32ncurses5 lib32ncurses5-dev varnish apache2-utils
sudo service nginx stop
sudo service varnish stop
sudo pip install virtualenv virtualenvwrapper
```

####Varnish
In production, the site is served by Varnish. We exclude the `/api/` routes so that the responses are dynamic. We wouldn't want to cache which sessions a single user had voted for, for example, because we'd be sending out of date information to the client. Still, caching just the homepage route means that we serve the most popular (and largest) page from Varnish rather than from an application server.

* `/etc/default/varnish` sets the startup defaults for the Varnish daemon. Notice we're only allocating 8mb of cache -- that's because we're only caching the homepage route.
```
START=yes
NFILES=131072
MEMLOCK=82000
DAEMON_OPTS="-a :80 \
             -T localhost:81 \
             -f /etc/varnish/default.vcl \
             -S /etc/varnish/secret \
             -s malloc,8m"
```

* `/etc/varnish/default.vcl` sets the rules for caching responses. We ignore any route that starts with `/api/` because these must be dynamic.
```
backend default {
    .host = "127.0.0.1";
    .port = "8001";
}
sub vcl_recv {
    if (req.url ~ "^/api/(.*)") { return(pass); }
    set req.url = regsuball(req.url,"[?&]_=[^&]{1,25}","");
    set req.backend = default;
    set req.grace = 10h;
    return(lookup);
}
sub vcl_miss {
    return(fetch);
}
sub vcl_hit {
    return(deliver);
}
sub vcl_fetch {
    set beresp.ttl = 10h;
    set beresp.grace = 10h;
    set beresp.http.X-Cacheable = "YES";
    unset beresp.http.Vary;
    return(deliver);
}
sub vcl_deliver {
    set resp.http.X-NICAR-SLOGAN = "I code like a journalist.";
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
        set resp.http.X-Cache-Hits = obj.hits;
        set resp.http.X-Cache-Backend = req.backend;
    } else {
        set resp.http.X-Cache = "MISS";
    }
    return(deliver);
}
```

####Nginx
In production, Varnish passes its requests to Nginx for processing. For the homepage route, the index.html file is served from a folder inside the app. On deploy, we bake a copy of the file and push it up to our Git repository and then pull it down to the server.

* `/etc/nginx/nginx.conf` controls our Nginx server. It listens on port 8001 and passes to uWSGI, our Python application server, for any URL that starts with `/api/`. Special treatment is given to the `/api/dashboard/` URL -- it's protected with HTTP BasicAuth -- and with the default `/` route, which sends straight to flat files in our app folder.
```
worker_processes  2;
error_log  /var/log/nginx/error.log crit;
pid        /var/run/nginx.pid;
events {
    worker_connections 2048;
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_names_hash_bucket_size 128;
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    access_log off;
    gzip on;
    gzip_disable "msie6";
    server {
        #listen 80;
        #location ^~ /api/dashboard/ { auth_basic "Restricted"; auth_basic_user_file /etc/nginx/.htpasswd; uwsgi_pass 127.0.0.1:8000; include uwsgi_params;  }
        #location / { uwsgi_pass 127.0.0.1:8000; include uwsgi_params; }

        listen 8001;
        location ^~ /api/dashboard/ { auth_basic "Restricted"; auth_basic_user_file /etc/nginx/.htpasswd; uwsgi_pass 127.0.0.1:8000; include uwsgi_params;  }
        location ^~ /api/ { uwsgi_pass 127.0.0.1:8000; include uwsgi_params; }
        location / { root /home/ubuntu/lightning-talks/www/; }
    }
}
```
####Daemons
Both `confs/tally.conf` and `confs/uwsgi.conf` are symlinked in `/etc/init/` on the production server.
* `confs/tally.conf` runs as a daemon on a 15-second delay. This daemon calculates vote counts on sessions and by users and updates the totals in the database asynchronously.
* `confs/uwsgi.conf` runs as a daemon. This daemon runs the dynamic `/api/` routes that handle user registration and login, session creation, and vote creation and deletion.

##Software
###Overview
Lightning talks is a Flask application that uses PyMongo to read from and write to a MongoDB server.

###Assumptions
Lightning talks sends all of its data via HTTP GET requests and URL parameters. We do this because we cannot be certain that the app may not need to send messages across domains, and cross-domain POST is still [fraught with difficulty](https://developer.mozilla.org/en-US/docs/Web/HTTP/Access_control_CORS#Preflighted_requests).

###Models
We've broken down the lightning talks data model into three model classes.

####User
Represents a single user. Users can create a `Session` and can also vote for a `Session`. See [models.py](https://github.com/ireapps/lightning-talks/blob/master/models.py) for more info.

####Session
Represents a single session. See [models.py](https://github.com/ireapps/lightning-talks/blob/master/models.py) for more info. A `User` can create a session.

####Vote
Represents a single `User`'s vote on a single `Session`. A `User` can both create a vote and delete a vote. See [models.py](https://github.com/ireapps/lightning-talks/blob/master/models.py) for more info.

###Routes
The core logic of the site is handled via a series of Flask routes that recieve URL parameters and return JSON. There are several AJAX requests in [site.js](https://github.com/ireapps/lightning-talks/blob/master/templates/static/site.js) where you can see this in action.

####Route `/api/user/action/`
This route handles two behaviors.
* **Register a new user**: If `email`, `password` and `name` are sent as URL parameters, the route will attempt to register this user. If an existing user has this email address, the user will be logged in. If there is no existing user with this email address, the user will be registered and a message will be sent returning the new user's `_id`, a `success` flag and an `action` key with the value `register`.
```json
{
    "_id": "97984267-ab75-46c4-b113-016a5555e92b",
    "success": true,
    "action": "register",
    "name": "jeremy bowers"
}
```
* **Login an existing user**: If only an `email` and `password` URL parameter are sent, the route will attempt to login the specified user. Success will return a user's `_id`, a `success` flag and an `action` key with the value `login`. It will also return a cookie-friendly pipe-delimited list of session `_id`'s as `votes`. Failure will return an error message with `success` false and a message that a matching user cannot be found.
```json
{
    "action": "login",
    "votes": "ef16edee-2292-49c8-b990-4d52b77529eb|d2650553-9e4f-4dc2-adee-f831419cf3e0|60b27f91-9506-498c-8758-90edfa1ad0b1",
    "_id": "638d66e1-3304-4d86-8224-5149d4dedbb9",
    "name": "jeremy bowers",
    "success": true
}
```

###Route `/api/session/action`
This route expects a `user` parameter that contains a valid `_id` for an existing `User`. It also expects a session `title` and `description`, though these are not absolutely required, only rather quite nice to have. Using this information, the app will create a new `Session` object with these fields and return the newly created `Session`'s `_id` and a `success` key. If a valid `User` could not be found, it will return an error.
```json
{
    "action": "create",
    "session": "34c0ef1b-8d9d-41ff-8819-e079ba0e6157",
    "success": true
}
```

###Route `/api/vote/action`
This route expects a `user` parameter and a `session` parameter where each resolves to an `_id` field of a valid `User` and `Session` respectively. The app will query the database to establish that both the `User` and the `Session` exist. If both exist, it will see if any existing `Vote` objects exist for this `User` and `Session` combination.

* If there is no existing `Vote` for this `User` on this `Session`, the app will create a vote and update the `Session`'s vote total.

* If there is an existing `Vote` for this `User` on this `Session`, the app will delete that vote and update the `Session`'s vote total.

##Tests
To run tests, do `fab tests`.