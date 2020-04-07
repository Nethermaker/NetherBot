import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('BUNGIE_API_KEY')
API_BASE = 'https://www.bungie.net/Platform/'

headers = {'Content-Type': 'application/json',
           'X-API-KEY': API_KEY}


def search_player(player):
    api_url = f'{API_BASE}Destiny2/SearchDestinyPlayer/-1/{player}/'
    response = requests.get(api_url, headers=headers)
    return json.dumps(response.json(), sort_keys=True, indent=4)


if __name__ == '__main__':
    print(search_player('Nethermaker'))