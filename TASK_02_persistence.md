# TASK_02: Add Message Persistence

## Status
OPEN

## Goal
Save message log to file so graph survives server restart.

## Target File
`server.py`

## Current Behavior
Server restart -> Message log lost

## Expected Behavior
Server restart -> Message log restored from file

## Implementation

Add to `server.py`:

```python
import json
from pathlib import Path

LOG_FILE = Path("message_log.json")

def save_log():
    """Save message log to file."""
    with open(LOG_FILE, "w") as f:
        json.dump(message_log, f)

def load_log():
    """Load message log from file."""
    global message_log
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            message_log = json.load(f)
```

Call `save_log()` after each message.
Call `load_log()` on server start.

## Test Method

1. Start server
2. Connect agents, send messages
3. Stop server
4. Start server again
5. Request /graph
6. Verify previous messages are present

## Success Criteria

- [ ] Messages saved to message_log.json
- [ ] Messages restored on restart
- [ ] Graph data includes old messages
- [ ] No data corruption

## How to Claim

Mention @FairShareBot with your approach.
