import os
import requests
import base64
import json

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_URL = os.getenv('AIRTABLE_URL')
SPOTIFY_TOKEN = os.getenv('SPOTIFY_TOKEN')
SPOTIFY_URL = os.getenv('SPOTIFY_URL')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def auth():
    headers = {}
    data = {}
    message = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    url = "https://accounts.spotify.com/api/token"
    headers['Authorization'] = f"Basic {base64_message}"
    data['grant_type'] = "client_credentials"
    r = requests.post(url, headers=headers, data=data)
    token = r.json()['access_token']
    return token

def cleanup_uri(uri):
    return uri.replace('spotify:playlist:', '')

def playlists():
    url = f"{AIRTABLE_URL}/Playlists"
    headers = {
      'Authorization': f'Bearer {AIRTABLE_API_KEY}',
      'Content-Type': 'application/json'
    }
    try:
        response = requests.request("GET", url, headers=headers)
        result = {}
        for r in response.json()['records']:
            result[r['id']] = cleanup_uri(r["fields"]['URI'])
            playlist_id = cleanup_uri(r["fields"]['URI'])
            followers = get_follower_amount(playlist_id)
            requests.request("PATCH", f"{AIRTABLE_URL}/Playlists/{r['id']}", headers=headers, data=json.dumps({
                "fields": {
                    "Followers": followers
                }
            }))
    except Exception as e:
        print(e)

def get_follower_amount(playlist):
    url = SPOTIFY_URL.replace('{PLAYLIST_ID}', playlist)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + auth()
    }
    try:
        response = requests.request("GET", url, headers=headers)
        if response.status_code != 200:
            print(response)
            return "Error"
        return response.json()["followers"]["total"]
    except Exception as e:
        print(e)

def lambda_handler(event, context):
    playlists()