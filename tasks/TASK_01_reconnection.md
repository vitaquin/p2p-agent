# TASK_01: Add Reconnection Logic

## Status
OPEN

## Goal
If connection drops, retry 3 times with exponential backoff.

## Target File
`node.py`

## Current Behavior
Connection drops -> Agent exits

## Expected Behavior
Connection drops -> Retry after 1s, 2s, 4s -> Then exit if all fail

## Implementation

Add to `AgentNode` class:

```python
async def connect_with_retry(self, max_retries=3):
    """Connect with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            await self.connect()
            return True
        except Exception as e:
            wait_time = 2 ** attempt  # 1, 2, 4 seconds
            print(f"Connection failed, retry in {wait_time}s...")
            await asyncio.sleep(wait_time)
    return False
```

## Test Method

1. Start server
2. Start agent
3. Kill server
4. Restart server within 7 seconds
5. Verify agent reconnects

## Success Criteria

- [ ] Agent retries 3 times
- [ ] Backoff is exponential (1s, 2s, 4s)
- [ ] Agent reconnects if server returns
- [ ] Agent exits cleanly after max retries

## How to Claim

Mention @FairShareBot with your approach.
