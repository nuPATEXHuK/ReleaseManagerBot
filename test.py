import requests

url = 'https://shikimori.one/api/animes/40028'
headers = {'user-agent': 'my-app/0.0.1'}

res = requests.get(url, headers=headers)
json = res.json()
print(json)