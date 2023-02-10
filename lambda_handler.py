import os
import requests
import json

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_URL = os.getenv('AIRTABLE_URL')
SPOTIFY_TOKEN = os.getenv('SPOTIFY_TOKEN')
SPOTIFY_URL = os.getenv('SPOTIFY_URL')

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
        'Authorization': f'Bearer {SPOTIFY_TOKEN}'
    }
    try: 
        response = requests.request("GET", url, headers=headers)
        if response.status_code != 200:
            print(response)
            return 0
        return response.json()["followers"]["total"]
    except Exception as e:
        print(e)
    
def handler(event, context):
    playlists()

# for local testing
# if __name__ == '__main__':
#     get_playlist_ids()

