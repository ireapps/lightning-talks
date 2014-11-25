# LightningTalks
A system for accepting votes for lightning talks.

## Bootstrapping

### Development
**First**: you must have a running mongodb instance accessible.
```
brew install mongodb
ln -sfv /usr/local/opt/mongodb/*.plist ~/Library/LaunchAgents
launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mongodb.plist
```
**Second**: Pull down the code from git, create a virtual environment and install requirements.
```
git clone git@github.com:ireapps/lightning-talks.git && cd lightning-talks
mkvirtualenv lightningtalks
pip install -r requirements.txt
```

**Third**: Load some fake data.
```
fab fake_data
```

### Production
TKTK

## Overview
TKTK

## Models
TKTK

## Tests
To run tests, do `fab tests`.