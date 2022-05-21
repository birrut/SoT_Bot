import requests
import json


def get_character_data():
    """Queries the swgoh.gg api to get character display name"""
    character_file = 'data/characters.json'
    url = 'https://swgoh.gg/api/characters'
    payload = {}
    headers = {"User-Agent": 'PostmanRuntime/7.29.0', "Accept": '*/*'}
    response = requests.request("GET", url, headers=headers, data=payload)
    character_list = response.json()
    with open(character_file, 'w') as out_file:
        out_file.write(json.dumps(character_list))




if __name__ =="__main__":
    get_character_data()
