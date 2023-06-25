import requests
import hashlib
import time
import json


def create_sign(ok_public_key, ok_group_id, method, ok_access_token, ok_secret_key): 
    timestamp = str(time.time())
    sign_str = f"application_key={ok_public_key}ok_group_id={ok_group_id}method={method}type=GROUP_THEMEformat=jsonmethod={method}{timestamp}{ok_access_token}{ok_secret_key}"
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    return sign


def create_url(ok_public_key, method, sign, ok_access_token):
    url = f"https://api.ok.ru/fb.do?application_key={ok_public_key}&method={method}&format=json&sig={sign}&ok_access_token={ok_access_token}"
    return url


def create_post_ok(ok_public_key, ok_group_id, ok_access_token, ok_secret_key, text_publication):
    method = 'mediatopic.post'
    attachment = {
        'media': [
            {
            'type': 'text',
            'text': text_publication
            }
        ]
    }

    sign = create_sign(ok_public_key, ok_group_id, method, ok_access_token, ok_secret_key)    
    url = create_url(ok_public_key, method, sign, ok_access_token)
    
    response = requests.post(url, data={'gid': ok_group_id, 'type': 'GROUP_THEME', 'attachment': json.dumps(attachment)})
    
    try:
        response = requests.post(url, data={'gid': ok_group_id, 'type': 'GROUP_THEME', 'attachment': json.dumps(attachment)})
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print ("HTTP Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("Something went wrong with the request:",err)
    
    if response.status_code == 200:
        print('Post published successfully.')
    else:
        print('Failed to publish post.', response.status_code, response.text)

    return ok_post_id


def delete_post_ok(ok_public_key, ok_group_id, ok_access_token, ok_secret_key, ok_post_id):
    method = 'mediatopic.deleteTopic'
    
    sign = create_sign(ok_public_key, ok_group_id, method, ok_access_token, ok_secret_key)
    url = create_url(ok_public_key, method, sign, ok_access_token)
    
    response = requests.post(url, data={'gid': ok_group_id, 'topic_id': ok_post_id, 'access_token': ok_access_token})


    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print ("HTTP Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("Something went wrong with the request:",err)
    
    if response.status_code == 200:
        print('Post deleted successfully.')
    else:
        print('Failed to delete post.', response.status_code, response.text)
