import asyncio
import json
from typing import Dict, Set

# In-memory subscribers mapping: session_id -> set of asyncio.Queue
_subscribers: Dict[int, Set[asyncio.Queue]] = {}


def _get_subscribers(session_id: int):
    return _subscribers.setdefault(int(session_id), set())


async def event_stream(session_id: int):
    """Async generator that yields Server-Sent Events for a session.

    Usage: return StreamingResponse(event_stream(session_id), media_type='text/event-stream')
    """
    q = asyncio.Queue()
    subs = _get_subscribers(session_id)
    subs.add(q)

    try:
        # Immediately yield a comment to establish the SSE connection
        yield "\n"
        while True:
            data = await q.get()
            try:
                payload = json.dumps(data)
            except Exception:
                payload = json.dumps({"type": "raw", "data": str(data)})
            yield f"data: {payload}\n\n"
    finally:
        # Clean up subscriber queue
        subs.discard(q)


def publish_event(session_id: int, event: dict):
    """Publish an event dict to all subscribers for the session.

    This is synchronous and will attempt to put_nowait to each queue.
    """
    subs = list(_get_subscribers(session_id))
    if not subs:
        return
    for q in subs:
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            # drop if subscriber is slow
            continue
