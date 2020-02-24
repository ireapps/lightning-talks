import os

PROJECT_NAME = "lightning-talks"

MONGO_DATABASE = 'lightningtalk'

# When true: Thumbs up/down buttons will appear.
# When false: No buttons for voting.
ACTIVE = False

# When true: Shows a list of sessions.
# When false: Shows the pitch-a-session box.
VOTING = True

ENVIRONMENTS = {
    "prd": {
        "hosts": ['lt']
    }
}
