#!/usr/bin/env python3
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from oauth.utils import get_oauth_client

youtube_client = get_oauth_client('youtube')

print('✅ YouTube OAuth Configuration Updated:')
print(f'Scopes: {youtube_client.client_kwargs.get("scope", "None")}')
print('\n🔗 Now visit: http://localhost:8000/oauth/youtube/start/')
print('   This will use the corrected scope configuration')