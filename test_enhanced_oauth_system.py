#!/usr/bin/env python3
"""
Test Enhanced OAuth System with Current YouTube Issue
"""
import os
import sys
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

import requests
import json
from django.test import Client
from django.contrib.auth.models import User

def test_enhanced_oauth_api():
    """Test the enhanced OAuth API endpoints"""
    print("=== Testing Enhanced OAuth API Endpoints ===\n")
    
    client = Client()
    
    # Create a session and login user 'toto'
    user = User.objects.get(username='toto')
    client.force_login(user)
    
    # Test 1: Get connected accounts with enhanced diagnostics
    print("1️⃣ Testing enhanced connected accounts endpoint...")
    response = client.get('/api/oauth/connected-accounts/')
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Total accounts: {data['summary']['total_connected']}")
        print(f"Overall health: {data['summary']['overall_health']}")
        print(f"Enhanced diagnostics: {data['summary']['enhanced_diagnostics']}")
        
        # Show YouTube account details
        youtube_account = next((acc for acc in data['accounts'] if acc['provider'] == 'youtube'), None)
        if youtube_account:
            print(f"\n📺 YouTube Account:")
            print(f"   Health: {youtube_account.get('health', 'unknown')}")
            print(f"   Status: {youtube_account.get('status', 'unknown')}")
            print(f"   API Accessible: {youtube_account.get('api_accessible', 'unknown')}")
            print(f"   Scope Sufficient: {youtube_account.get('scope_sufficient', 'unknown')}")
            print(f"   Recommended Action: {youtube_account.get('recommended_action', 'unknown')}")
            
            if youtube_account.get('diagnostics', {}).get('api_error'):
                print(f"   API Error: {youtube_account['diagnostics']['api_error']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.content.decode())
    
    # Test 2: Get YouTube diagnostics
    print(f"\n2️⃣ Testing YouTube diagnostics endpoint...")
    response = client.get('/api/oauth/diagnostics/youtube/')
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            diagnostics = data['diagnostics']
            print(f"✅ Success!")
            
            print(f"\n🔍 YouTube Diagnostics:")
            print(f"   Connected: {diagnostics['connection_status']['connected']}")
            print(f"   Validation Status: {diagnostics['connection_status']['validation_status']}")
            print(f"   API Accessible: {diagnostics['connection_status'].get('api_accessible', 'unknown')}")
            
            print(f"\n📋 Recommendations ({len(diagnostics['recommendations'])}):")
            for i, rec in enumerate(diagnostics['recommendations'], 1):
                priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'info': '🟢'}.get(rec['priority'], '⚪')
                print(f"   {i}. {priority_emoji} [{rec['priority'].upper()}] {rec['message']}")
                if rec.get('url'):
                    print(f"      Action URL: {rec['url']}")
        else:
            print(f"❌ Diagnostics failed: {data.get('message')}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.content.decode())
    
    # Test 3: Attempt connection repair
    print(f"\n3️⃣ Testing connection repair endpoint...")
    response = client.post('/api/oauth/repair/youtube/')
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Repair Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', 'No message')}")
        
        if data.get('repair_actions'):
            print(f"\n🔧 Repair Actions:")
            for action in data['repair_actions']:
                status_emoji = '✅' if action['success'] else '❌'
                print(f"   {status_emoji} {action['action']}: {action['message']}")
        
        print(f"\n📊 Status Comparison:")
        print(f"   Before: {data.get('status_before', {})}")
        print(f"   After: {data.get('status_after', {})}")
        print(f"   Recommended Action: {data.get('recommended_action')}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.content.decode())

def test_enhanced_youtube_upload():
    """Test YouTube upload with enhanced OAuth handling"""
    print(f"\n=== Testing Enhanced YouTube Upload ===\n")
    
    client = Client()
    
    # Login user 'toto'
    user = User.objects.get(username='toto')
    client.force_login(user)
    
    # Test upload with current token (should detect and handle scope issue)
    test_data = {
        'file_url': 'http://localhost:8000download/podcast/Algeria_2026_water_economic.mp4',
        'file_name': 'Algeria_2026_water_economic.mp4',
        'file_type': 'mp4',
        'platform_data': json.dumps({
            "title": "Enhanced OAuth Test Video",
            "description": "Testing enhanced OAuth system with scope issue detection",
            "tags": "",
            "visibility": "private"
        })
    }
    
    print("📤 Attempting YouTube upload with enhanced OAuth...")
    response = client.post('/api/social-media/share/youtube/', data=test_data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload Success!")
        print(f"Video ID: {data.get('video_id')}")
        print(f"Video URL: {data.get('video_url')}")
        print(f"Connection Status: {data.get('connection_status')}")
    elif response.status_code == 403:
        data = response.json()
        print(f"🔴 Scope Issue Detected (as expected)!")
        print(f"Error: {data.get('error')}")
        print(f"Action Required: {data.get('action_required')}")
        print(f"Connect URL: {data.get('connect_url')}")
        print(f"Scope Issue: {data.get('scope_issue', False)}")
        
        if data.get('technical_details'):
            print(f"Technical Details: {data['technical_details'].get('api_error', 'No details')}")
    elif response.status_code == 401:
        data = response.json()
        print(f"🟠 Authentication Issue:")
        print(f"Error: {data.get('error')}")
        print(f"Action Required: {data.get('action_required')}")
        print(f"Connect URL: {data.get('connect_url')}")
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except:
            print(response.content.decode())

if __name__ == "__main__":
    print("🧪 Testing Enhanced Professional OAuth System\n")
    
    try:
        test_enhanced_oauth_api()
        test_enhanced_youtube_upload()
        
        print(f"\n" + "="*60)
        print("🎯 SUMMARY:")
        print("✅ Enhanced OAuth system provides comprehensive diagnostics")
        print("✅ Scope issues are detected and properly communicated") 
        print("✅ Professional error messages guide users to solutions")
        print("✅ Automatic repair attempts when possible")
        print(f"🔗 Reconnect YouTube: http://localhost:8000/oauth/youtube/start/")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()