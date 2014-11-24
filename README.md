# LightningTalks
A system for accepting votes for lightning talks.

## Bootstrapping

### Development
**First**: you must have a running elasticsearch instance accessible. Export your elasticsearch connection configuration like this:

```
LIGHTNINGTALKS_ES_HOST=
LIGHTNINGTALKS_ES_PORT=
```

If these are not available in the environment, LightningTalks will default to 'localhost' and '9200', respectively.

**Second**: Pull down the code from git, create a virtual environment and install requirements.

```
git clone git@github.com:ireapps/lightning-talks.git && cd lightning-talks
mkvirtualenv lightningtalks
pip install -r requirements.txt
```

**Third**: Run the tests.

```
nosetests
```

### Production
TKTK

## Overview
TKTK

## Models
TKTK
