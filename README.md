# LightningTalks
A system for accepting votes for lightning talks.

## Bootstrapping

### Development
**First**: you must have a running mongodb instance accessible.
```sh
brew install mongodb
ln -sfv /usr/local/opt/mongodb/*.plist ~/Library/LaunchAgents
launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mongodb.plist
```
**Second**: Pull down the code from git, create a virtual environment and install requirements.
```sh
git clone git@github.com:ireapps/lightning-talks.git && cd lightning-talks
mkvirtualenv lightningtalks
pip install -r requirements.txt
```

**Third**: Load some fake data.
```sh
fab fake_data
```

**Fourth**: Run the app.
```sh
python app.py
```

### Production
#### Crons
```
*/1 * * * * ubuntu /bin/bash /home/ubuntu/apps/lightning-talks/repository/run_on_server.sh fab tally > /var/log/lightning-talks.log 2>&1
```
#### Software
```
sudo apt-get install easy_install python2.7-dev
sudo easy_install pip
sudo pip install virtualenv virtualenvwrapper
```

## Overview
### Routes
####`/api/user/action/`
The `/api/user/action/` route can execute two actions. If only an `email` and `password` URL parameter are sent, the route will attempt to login the specified user. Success will return a user's `_id`, a `success` flag and an `action` key with the value `login`. It will also return a cookie-friendly pipe-delimited list of session `_id`'s as `votes`. Failure will return an error message with `success` false and a message that a matching user cannot be found.
```json
{
    "action": "login",
    "votes": "ef16edee-2292-49c8-b990-4d52b77529eb|d2650553-9e4f-4dc2-adee-f831419cf3e0|60b27f91-9506-498c-8758-90edfa1ad0b1",
    "_id": "638d66e1-3304-4d86-8224-5149d4dedbb9",
    "name": "jeremy bowers",
    "success": true
}
```
If `email`, `password` and `name` are sent as URL parameters, the route will attempt to register this user. If an existing user has this email address, the user will be logged in. If there is no existing user with this email address, the user will be registered and a message will be sent returning the new user's `_id`, a `success` flag and an `action` key with the value `register`.
```json
{
    "_id": "97984267-ab75-46c4-b113-016a5555e92b",
    "success": true,
    "action": "register",
    "name": "jeremy bowers"
}
```
####`/api/user/`
The `/api/user/` route expects `_id`, a valid `uuid4` UUID matching a user in our database. It returns a cached list of `sessions_pitched`, a cached list of `sessions_voted_for`, the `_id` and the `email` address this user logs in with.
```json
{
    "sessions_pitched": [
        "60b27f91-9506-498c-8758-90edfa1ad0b1",
        "d2650553-9e4f-4dc2-adee-f831419cf3e0",
        "ef16edee-2292-49c8-b990-4d52b77529eb"
    ],
    "sessions_voted_for": [
        "ef16edee-2292-49c8-b990-4d52b77529eb",
        "d2650553-9e4f-4dc2-adee-f831419cf3e0"
    ],
    "_id": "97984267-ab75-46c4-b113-016a5555e92b",
    "email": "jeremy.bowers@fake.fake"
}
```
####`/api/session/`
The `/api/session/` route expects '_id', a valid `uuid4` UUID matching a session in our database. It returns a cached number of `votes`, the `_id`, the session `title` and `description`, the session's `created` and `updated` dates, and an accepted flag, along with the `user` who proposed the session.
```json
{
    "votes": 1,
    "_id": "60b27f91-9506-498c-8758-90edfa1ad0b1",
    "description": "This is a test description that is rather long. This is a test description that is rather long. This is a test description that is rather long. This is a test description that is rather long. This is a test description that is rather long. This is a test description that is rather long. This is a test description that is rather long. This is a test description that is rather long. This is a test description that is rather long. This is a test description that is rather long. This is a test description that is rather long. This is a test description that is rather long.",
    "created": 1416886310,
    "title": "Having The Time Of Your Life",
    "updated": 1416886667,
    "user": "97984267-ab75-46c4-b113-016a5555e92b",
    "accepted": false
}
```

## Models
### User
Represents a single user. Users can originate a `Session` and can also vote for a `Session`. See [models.py](https://github.com/ireapps/lightning-talks/blob/master/models.py#L59:L66) for more info.
### Session
Represents a single session. See [models.py](https://github.com/ireapps/lightning-talks/blob/master/models.py#L107:L112) for more info.
### Vote
Represents a single `User`'s vote on a single `Session`. See [models.py](https://github.com/ireapps/lightning-talks/blob/master/models.py#L137:L139) for more info.

## Tests
To run tests, do `fab tests`.