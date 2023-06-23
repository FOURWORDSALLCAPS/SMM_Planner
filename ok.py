import hashlib  
import json,requests
import requests
import hashlib
import time
import json


app_id = '512001977033' 
app_public_key = 'CKMLCDLGDIHBABABA'
app_secret_key = 'f77099cf490198c8c1a1576f944797ce' 
access_token = 'tkn1ovwGmnQGCFC80PkOR2Hm3brtjuEmI6HNHUI3me0hDAM4pmBxDikFDRjpbfMBYs4le'
group_id = '70000002836096' # ID группы, в которой вы хотите опубликовать сообщение
message = 'Hello, world!' # Сообщение, которое вы хотите опубликовать


params = {
    "application_key": app_public_key,
    "method": "photosV2.getUploadUrl",
    "format": "json",
    "gid": group_id,
    "count": 1  # Number of photos to be uploaded
}

#Signature
params_str = "".join(f"{k}={v}" for k, v in sorted(params.items()))
sig = hashlib.md5((params_str + app_secret_key).encode('utf-8')).hexdigest()

params["access_token"] = access_token
params["sig"] = sig

response = requests.post("https://api.ok.ru/fb.do", params=params)
data = response.json()

upload_url = data["upload_url"]

print("upload_url:", upload_url)


with open("test.png", "rb") as f:
    files = {"file": f}

    response = requests.post(upload_url, files=files)



data = response.json()

pprint.pprint(data)


photo_id_key = list(data["photos"].keys())[0]
photo_token = data["photos"][photo_id_key]["token"]

print("photo_id_key:", photo_id_key)
print("photo_token:", photo_token)



method = 'mediatopic.post'
timestamp = str(int(time.time()))


sign_str = f"application_key={app_public_key}group_id={group_id}method={method}type=GROUP_THEMEformat=jsonmethod={method}{timestamp}{access_token}{app_secret_key}"
sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()


url = f"https://api.ok.ru/fb.do?application_key={app_public_key}&method={method}&format=json&sig={sign}&access_token={access_token}"


attachment = {
  "media": [
    {
      "type": "photo",
      "list": [
        { "id": photo_id_key },
        { "photoId": photo_token }
      ]
    },
    {
      "type": "text",
      "text": "Text1"
    }
  ]
}


try:
    response = requests.post(url, data={'gid': group_id, 'type': 'GROUP_THEME', 'attachment': json.dumps(attachment)})
    response.raise_for_status()
except requests.exceptions.HTTPError as errh:
    print ("HTTP Error:",errh)
except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc)
except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
except requests.exceptions.RequestException as err:
    print ("Something went wrong with the request:",err)

#Проверка ответа
if response.status_code == 200:
    print('Post published successfully.')
else:
    pprint.pprint('Failed to publish post.', response.status_code, response.text)

pprint.pprint(response.json())
