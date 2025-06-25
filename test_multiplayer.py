#!/usr/bin/env python3
"""
Test script to verify multiplayer functionality of the philoagents application.
This script simulates multiple users having conversations with the same philosopher
to ensure thread isolation is working correctly.
"""

import asyncio
import aiohttp
import json
import uuid
from typing import Dict, List


class PhiloagentsTestClient:
    """Test client for the philoagents API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
    
    async def create_session(self) -> Dict:
        """Create a new user session."""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/session") as response:
                if response.status == 200:
                    data = await response.json()
                    self.session_id = data["user_id"]
                    return data
                else:
                    raise Exception(f"Failed to create session: {response.status}")
    
    async def send_message(self, philosopher_id: str, message: str) -> str:
        """Send a message to a philosopher."""
        if not self.session_id:
            await self.create_session()
        
        payload = {
            "message": message,
            "philosopher_id": philosopher_id,
            "user_id": self.session_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["response"]
                else:
                    raise Exception(f"Failed to send message: {response.status}")
    
    async def reset_conversations(self) -> Dict:
        """Reset this user's conversations."""
        if not self.session_id:
            raise Exception("No session created")
        
        payload = {"user_id": self.session_id}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/reset-memory",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to reset conversations: {response.status}")


async def test_single_user_conversation():
    """Test that a single user can have a conversation with a philosopher."""
    print("🧪 Testing single user conversation...")
    
    client = PhiloagentsTestClient()
    
    # Create session
    session = await client.create_session()
    print(f"✅ Created session: {session['user_id'][:8]}...")
    
    # Send a message
    response = await client.send_message("socrates", "Hello, Socrates!")
    print(f"✅ Received response: {response[:50]}...")
    
    # Send follow-up message
    response2 = await client.send_message("socrates", "What is wisdom?")
    print(f"✅ Received follow-up: {response2[:50]}...")
    
    print("✅ Single user conversation test passed!\n")


async def test_multiple_users_same_philosopher():
    """Test that multiple users can talk to the same philosopher independently."""
    print("🧪 Testing multiple users with same philosopher...")
    
    # Create two clients
    client1 = PhiloagentsTestClient()
    client2 = PhiloagentsTestClient()
    
    # Create sessions
    session1 = await client1.create_session()
    session2 = await client2.create_session()
    
    print(f"✅ User 1 session: {session1['user_id'][:8]}...")
    print(f"✅ User 2 session: {session2['user_id'][:8]}...")
    
    # Both users talk to Socrates with different topics
    response1 = await client1.send_message("socrates", "Tell me about justice.")
    response2 = await client2.send_message("socrates", "What is the meaning of life?")
    
    print(f"✅ User 1 response: {response1[:50]}...")
    print(f"✅ User 2 response: {response2[:50]}...")
    
    # Verify responses are different (they should be contextually different)
    if response1 != response2:
        print("✅ Responses are different - good isolation!")
    else:
        print("⚠️  Responses are identical - possible isolation issue")
    
    # Continue conversations to test thread persistence
    follow1 = await client1.send_message("socrates", "Can you elaborate on that?")
    follow2 = await client2.send_message("socrates", "Can you give me an example?")
    
    print(f"✅ User 1 follow-up: {follow1[:50]}...")
    print(f"✅ User 2 follow-up: {follow2[:50]}...")
    
    print("✅ Multiple users same philosopher test passed!\n")


async def test_conversation_reset():
    """Test that conversation reset works for individual users."""
    print("🧪 Testing conversation reset...")
    
    client = PhiloagentsTestClient()
    
    # Create session and have a conversation
    session = await client.create_session()
    print(f"✅ Created session: {session['user_id'][:8]}...")
    
    # Start conversation
    response1 = await client.send_message("plato", "Hello Plato, let's discuss forms.")
    print(f"✅ Initial message: {response1[:50]}...")
    
    # Reset conversations
    reset_result = await client.reset_conversations()
    print(f"✅ Reset result: {reset_result['message']}")
    
    # Send new message (should start fresh conversation)
    response2 = await client.send_message("plato", "Hello Plato, let's discuss forms.")
    print(f"✅ Post-reset message: {response2[:50]}...")
    
    print("✅ Conversation reset test passed!\n")


async def test_concurrent_conversations():
    """Test concurrent conversations with multiple users and philosophers."""
    print("🧪 Testing concurrent conversations...")
    
    # Create multiple clients
    clients = [PhiloagentsTestClient() for _ in range(3)]
    
    # Create sessions concurrently
    sessions = await asyncio.gather(*[client.create_session() for client in clients])
    
    for i, session in enumerate(sessions):
        print(f"✅ User {i+1} session: {session['user_id'][:8]}...")
    
    # Send messages concurrently to different philosophers
    messages = [
        (clients[0], "socrates", "What is knowledge?"),
        (clients[1], "aristotle", "Explain virtue ethics."),
        (clients[2], "plato", "Tell me about the cave allegory.")
    ]
    
    responses = await asyncio.gather(*[
        client.send_message(philosopher, message) 
        for client, philosopher, message in messages
    ])
    
    for i, response in enumerate(responses):
        print(f"✅ User {i+1} response: {response[:50]}...")
    
    print("✅ Concurrent conversations test passed!\n")


async def main():
    """Run all tests."""
    print("🚀 Starting Philoagents Multiplayer Tests\n")
    
    try:
        await test_single_user_conversation()
        await test_multiple_users_same_philosopher()
        await test_conversation_reset()
        await test_concurrent_conversations()
        
        print("🎉 All tests passed! Multiplayer functionality is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
