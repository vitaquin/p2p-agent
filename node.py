#!/usr/bin/env python3
"""
P2P Agent Node
==============
An agent node that connects to the relay server and can
communicate with other agents.

Run: python node.py --id AgentName
"""

import asyncio
import json
import argparse
import websockets


class AgentNode:
    """A P2P agent node."""
    
    def __init__(self, agent_id, capabilities=None, server_url="ws://localhost:8765"):
        self.agent_id = agent_id
        self.capabilities = capabilities or []
        self.server_url = server_url
        self.websocket = None
        self.known_agents = {}
        self.message_handlers = []
    
    def on_message(self, handler):
        """Register a message handler."""
        self.message_handlers.append(handler)
    
    async def connect(self):
        """Connect to the relay server."""
        self.websocket = await websockets.connect(self.server_url)
        
        # Register with server
        await self.websocket.send(json.dumps({
            "type": "register",
            "agent_id": self.agent_id,
            "capabilities": self.capabilities
        }))
        
        print(f"[{self.agent_id}] Connected to server")
    
    async def send_message(self, to_agent, content):
        """Send a direct message to another agent."""
        await self.websocket.send(json.dumps({
            "type": "message",
            "from": self.agent_id,
            "to": to_agent,
            "content": content
        }))
    
    async def mention(self, agent_id, message):
        """
        Mention another agent (creates graph edge).
        Format: @agent_id message
        """
        content = f"@{agent_id} {message}"
        await self.send_message(agent_id, content)
        print(f"[{self.agent_id}] Mentioned @{agent_id}")
    
    async def broadcast(self, content):
        """Broadcast a message to all agents."""
        await self.websocket.send(json.dumps({
            "type": "broadcast",
            "from": self.agent_id,
            "content": content
        }))
    
    async def get_graph_data(self):
        """Request graph data from server."""
        await self.websocket.send(json.dumps({
            "type": "get_graph"
        }))
    
    async def listen(self):
        """Listen for incoming messages."""
        async for message in self.websocket:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "agent_list":
                # Update known agents
                for agent in data.get("agents", []):
                    self.known_agents[agent["agent_id"]] = agent
                print(f"[{self.agent_id}] Known agents: {list(self.known_agents.keys())}")
            
            elif msg_type == "agent_joined":
                agent_id = data.get("agent_id")
                self.known_agents[agent_id] = {
                    "agent_id": agent_id,
                    "capabilities": data.get("capabilities", [])
                }
                print(f"[{self.agent_id}] Agent joined: {agent_id}")
            
            elif msg_type == "agent_left":
                agent_id = data.get("agent_id")
                if agent_id in self.known_agents:
                    del self.known_agents[agent_id]
                print(f"[{self.agent_id}] Agent left: {agent_id}")
            
            elif msg_type == "message":
                from_agent = data.get("from")
                content = data.get("content")
                print(f"[{self.agent_id}] Message from {from_agent}: {content}")
                
                # Call registered handlers
                for handler in self.message_handlers:
                    await handler(from_agent, content)
            
            elif msg_type == "broadcast":
                from_agent = data.get("from")
                content = data.get("content")
                print(f"[{self.agent_id}] Broadcast from {from_agent}: {content}")
            
            elif msg_type == "graph_data":
                messages = data.get("messages", [])
                print(f"[{self.agent_id}] Graph data: {len(messages)} messages")
                return messages
    
    async def run(self):
        """Main run loop."""
        await self.connect()
        await self.listen()


async def interactive_mode(node):
    """Run agent in interactive mode."""
    await node.connect()
    
    # Start listener in background
    listener_task = asyncio.create_task(node.listen())
    
    print()
    print("Commands:")
    print("  /list          - Show known agents")
    print("  /msg <id> <m>  - Send message to agent")
    print("  /mention <id> <m> - Mention agent (creates edge)")
    print("  /broadcast <m> - Broadcast to all")
    print("  /graph         - Request graph data")
    print("  /quit          - Exit")
    print()
    
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(
                None, input, f"[{node.agent_id}]> "
            )
            
            if line.startswith("/list"):
                print(f"Known agents: {list(node.known_agents.keys())}")
            
            elif line.startswith("/msg "):
                parts = line[5:].split(" ", 1)
                if len(parts) == 2:
                    await node.send_message(parts[0], parts[1])
            
            elif line.startswith("/mention "):
                parts = line[9:].split(" ", 1)
                if len(parts) == 2:
                    await node.mention(parts[0], parts[1])
            
            elif line.startswith("/broadcast "):
                await node.broadcast(line[11:])
            
            elif line.startswith("/graph"):
                await node.get_graph_data()
            
            elif line.startswith("/quit"):
                break
            
            else:
                print("Unknown command. Type /list, /msg, /mention, /broadcast, /graph, or /quit")
        
        except EOFError:
            break
    
    listener_task.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P2P Agent Node")
    parser.add_argument("--id", required=True, help="Agent ID")
    parser.add_argument("--capabilities", nargs="*", default=[], help="Agent capabilities")
    parser.add_argument("--server", default="ws://localhost:8765", help="Server URL")
    args = parser.parse_args()
    
    node = AgentNode(
        agent_id=args.id,
        capabilities=args.capabilities,
        server_url=args.server
    )
    
    asyncio.run(interactive_mode(node))
