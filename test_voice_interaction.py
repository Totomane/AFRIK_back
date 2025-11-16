#!/usr/bin/env python3
"""
Test script for the Interactive Voice System with DIA TTS
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_interactive_conversation():
    """Test the interactive conversation flow"""
    
    print("🧪 Testing Interactive Voice Conversation System")
    print("=" * 50)
    
    # Test 1: Start new conversation
    print("\n1️⃣ Starting new conversation...")
    response = requests.get(f"{BASE_URL}/voice/conversation/", params={
        "session_id": "test_session_123",
        "reset": "true"
    })
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Conversation started successfully")
        print(f"📝 AI Response: {data['ai_response_text'][:100]}...")
        print(f"🎵 Audio file: {data['ai_response_audio']}")
        print(f"📊 State: {data['conversation_state']}")
    else:
        print(f"❌ Failed to start conversation: {response.status_code}")
        return
    
    # Test 2: Check conversation status
    print("\n2️⃣ Checking conversation status...")
    response = requests.get(f"{BASE_URL}/voice/conversation/status/", params={
        "session_id": "test_session_123"
    })
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Status retrieved successfully")
        print(f"📊 Current step: {data['conversation_state']['step']}")
        print(f"👥 Active sessions: {data['total_active_sessions']}")
    else:
        print(f"❌ Failed to get status: {response.status_code}")
    
    # Test 3: Quick commands
    print("\n3️⃣ Testing quick commands...")
    commands = ["help", "countries", "risks", "demo"]
    
    for cmd in commands:
        print(f"\n   Testing command: '{cmd}'")
        response = requests.get(f"{BASE_URL}/voice/command/", params={
            "command": cmd
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Command '{cmd}' successful")
            print(f"   📝 Response: {data['response_text'][:80]}...")
        else:
            print(f"   ❌ Command '{cmd}' failed: {response.status_code}")
    
    # Test 4: Basic TTS
    print("\n4️⃣ Testing basic TTS...")
    response = requests.get(f"{BASE_URL}/voice/ask/", params={
        "text": "Hello! This is a test of the DIA TTS system. Can you hear me clearly?"
    })
    
    if response.status_code == 200:
        data = response.json()
        print("✅ TTS generation successful")
        print(f"📝 Text: {data['text']}")
        print(f"🎵 Audio file: {data['audio_file']}")
    else:
        print(f"❌ TTS generation failed: {response.status_code}")

def test_conversation_flow_simulation():
    """Simulate a complete conversation flow"""
    
    print("\n\n🎭 Simulating Complete Conversation Flow")
    print("=" * 50)
    
    session_id = "demo_session"
    
    # Simulate conversation steps
    conversation_steps = [
        {
            "step": "Start",
            "action": "GET",
            "url": f"{BASE_URL}/voice/conversation/",
            "params": {"session_id": session_id, "reset": "true"}
        },
        {
            "step": "User says country (simulated)",
            "expected_response": "Great! I'll analyze Nigeria. Now, what types of risks..."
        },
        {
            "step": "Check available endpoints",
            "action": "GET",
            "url": f"{BASE_URL}/voice/conversation/status/",
            "params": {"session_id": session_id}
        }
    ]
    
    for i, step in enumerate(conversation_steps, 1):
        print(f"\n{i}️⃣ {step['step']}")
        
        if step.get('action') == 'GET':
            response = requests.get(step['url'], params=step.get('params', {}))
            
            if response.status_code == 200:
                data = response.json()
                print("   ✅ Step completed successfully")
                if 'ai_response_text' in data:
                    print(f"   📝 AI: {data['ai_response_text'][:100]}...")
                if 'conversation_state' in data:
                    print(f"   📊 Step: {data['conversation_state']['step']}")
            else:
                print(f"   ❌ Step failed: {response.status_code}")
        else:
            print(f"   📝 Expected: {step.get('expected_response', 'N/A')[:100]}...")

if __name__ == "__main__":
    print("🎙️ Interactive Voice System Test Suite")
    print("🔊 Testing DIA TTS Integration")
    
    try:
        test_interactive_conversation()
        test_conversation_flow_simulation()
        
        print("\n\n✅ All tests completed!")
        print("\n📋 Available Endpoints:")
        print("   🎤 POST /voice/conversation/ - Interactive conversation")
        print("   📊 GET  /voice/conversation/status/ - Conversation status")
        print("   🗣️  GET  /voice/ask/ - Basic TTS generation")
        print("   ⚡ GET  /voice/command/ - Quick voice commands")
        print("   🎵 GET  /voice/audio/<file_path>/ - Serve audio files")
        
        print("\n🎯 Frontend Integration:")
        print("   1. Start conversation: GET /voice/conversation/")
        print("   2. Record user audio and POST to /voice/conversation/")
        print("   3. Play AI response audio from returned file path")
        print("   4. Repeat until conversation complete")
        
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")
        print("Make sure the Django server is running on localhost:8000")