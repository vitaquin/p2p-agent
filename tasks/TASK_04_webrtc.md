# TASK_04: Add Direct P2P Connection (WebRTC)

## Status
OPEN (Advanced)

## Goal
Enable direct peer-to-peer connection without relay server.

## Target Files
New file: `p2p.py`

## Current Behavior
All messages go through relay server

## Expected Behavior
After discovery, agents can communicate directly

## Approach

Use aiortc (Python WebRTC library):

```python
from aiortc import RTCPeerConnection, RTCDataChannel

async def create_p2p_connection(remote_agent):
    pc = RTCPeerConnection()
    channel = pc.createDataChannel("messages")
    
    # Exchange SDP via relay server
    # Then communicate directly
```

## Implementation Steps

1. Install: `pip install aiortc`
2. Create offer/answer exchange via relay
3. Establish direct data channel
4. Fall back to relay if direct fails

## Test Method

1. Start server
2. Connect 2 agents
3. Establish P2P
4. Stop server
5. Verify agents can still communicate

## Success Criteria

- [ ] P2P connection established
- [ ] Messages flow without server
- [ ] Fallback to relay works
- [ ] Graph still updated

## Difficulty
Advanced - Requires WebRTC knowledge

## How to Claim

Mention @FairShareBot with your approach.
