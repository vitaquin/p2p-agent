#!/usr/bin/env python3
"""
P2P Agent Relay Server
======================
A simple WebSocket relay server that enables agents to discover
and communicate with each other.

Run: python server.py
"""

import asyncio
import json
import websockets
from datetime import datetime

# Connected agents
agents = {}

# Message log for graph construction
message_log = []


async def handler(websocket, path):
    """Handle incoming WebSocket connections."""
    agent_id = None
    
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "register":
                # Agent registration
                agent_id = data.get("agent_id")
                agents[agent_id] = {
                    "websocket": websocket,
                    "capabilities": data.get("capabilities", []),
                    "joined_at": datetime.utcnow().isoformat()
                }
                print(f"[+] Agent joined: {agent_id}")
                
                # Notify all agents of new member
                await broadcast({
                    "type": "agent_joined",
                    "agent_id": agent_id,
                    "capabilities": data.get("capabilities", [])
                })
                
                # Send current agent list to new agent
                agent_list = [
                    {"agent_id": aid, "capabilities": info["capabilities"]}
                    for aid, info in agents.items()
                ]
                await websocket.send(json.dumps({
                    "type": "agent_list",
                    "agents": agent_list
                }))
            
            elif msg_type == "message":
                # Direct message to another agent
                to_agent = data.get("to")
                from_agent = data.get("from", agent_id)
                content = data.get("content", "")
                
                # Log for graph construction
                message_log.append({
                    "from": from_agent,
                    "to": to_agent,
                    "content": content,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Forward message
                if to_agent in agents:
                    await agents[to_agent]["websocket"].send(json.dumps({
                        "type": "message",
                        "from": from_agent,
                        "content": content
                    }))
                    print(f"[@] {from_agent} -> {to_agent}")
            
            elif msg_type == "broadcast":
                # Broadcast to all agents
                from_agent = data.get("from", agent_id)
                content = data.get("content", "")
                
                await broadcast({
                    "type": "broadcast",
                    "from": from_agent,
                    "content": content
                }, exclude=agent_id)
                print(f"[*] {from_agent} broadcast: {content[:50]}...")
            
            elif msg_type == "get_graph":
                # Return message log for graph construction
                await websocket.send(json.dumps({
                    "type": "graph_data",
                    "messages": message_log
                }))
    
    except websockets.exceptions.ConnectionClosed:
        pass
    
    finally:
        if agent_id and agent_id in agents:
            del agents[agent_id]
            print(f"[-] Agent left: {agent_id}")
            await broadcast({
                "type": "agent_left",
                "agent_id": agent_id
            })


async def broadcast(message, exclude=None):
    """Broadcast message to all connected agents."""
    msg_str = json.dumps(message)
    for aid, info in agents.items():
        if aid != exclude:
            try:
                await info["websocket"].send(msg_str)
            except:
                pass


async def main():
    """Start the relay server."""
    port = 8765
    print(f"P2P Agent Relay Server")
    print(f"======================")
    print(f"Listening on ws://localhost:{port}")
    print(f"Waiting for agents...")
    print()
    
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
