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


def max_light_level(player):
    player_json = search_player(player)
    player_id = json.loads(player_json)['Response'][0]['membershipId']
    platform = json.loads(player_json)['Response'][0]['membershipType']
    profile_url = f'{API_BASE}Destiny2/{platform}/Profile/{player_id}/?components=100'
    player_characters = json.loads(requests.get(profile_url, headers=headers).content)['Response']['profile']['data']['characterIds']
    levels = []
    for character_id in player_characters:
        character_url = profile_url[0:-15] + f'Character/{character_id}/?components=200'
        character_json = json.loads(requests.get(character_url, headers=headers).content)
        levels.append(character_json['Response']['character']['data']['light'])
    return max(levels)


if __name__ == '__main__':
    # print(search_player('Nethermaker'))
    # api_url = f'{API_BASE}Destiny2/3/Profile/4611686018467392692/Character/2305843009300120719/?components=200'
    # response = requests.get(api_url, headers=headers)
    # d = json.loads(response.content)
    # print(d['Response']['character']['data']['light'])
    # print(json.dumps(response.json(), sort_keys=True, indent=4))
    max_light_level('Nethermaker')

