# TASK_03: Add Live Score Display

## Status
OPEN

## Goal
Show real-time centrality scores when requested.

## Target File
`server.py` and `node.py`

## Current Behavior
/graph returns raw message data

## Expected Behavior
/scores returns computed centrality scores

## Implementation

### In server.py

Add handler for "get_scores" message type:

```python
elif msg_type == "get_scores":
    from graph import build_graph
    from centrality import compute_scores
    
    adjacency, agents = build_graph(message_log)
    scores = compute_scores(adjacency, agents)
    
    await websocket.send(json.dumps({
        "type": "scores",
        "scores": scores
    }))
```

### In node.py

Add /scores command:

```python
elif line.startswith("/scores"):
    await websocket.send(json.dumps({"type": "get_scores"}))
```

Handle "scores" message type in listener.

## Test Method

1. Start server
2. Connect 3 agents
3. Send mentions between agents
4. Type /scores
5. Verify scores are displayed

## Success Criteria

- [ ] /scores command works
- [ ] Scores are computed correctly
- [ ] Scores sum to expected values
- [ ] Display is readable

## How to Claim

Mention @FairShareBot with your approach.
