import requests
import json

from vkbottle import API


async def upload_photo_to_album(vk_token, group_id, file_path):
    api = API(vk_token)
    upload_url = await api.photos.get_upload_server(album_id=group_id, group_id=group_id)
    with open(file_path, 'rb') as f:
        photo_data = {'photo': (file_path, f, 'jpeg')}
        response = requests.post(upload_url.upload_url, files=photo_data)
        upload_result = json.loads(response.text)
    photo_info = await api.photos.save(album_id=group_id, group_id=group_id, server=upload_result['server'],
                                       photos_list=upload_result['photos_list'], hash=upload_result['hash'])
    attachment = f"photo-{photo_info[0].owner_id}_{photo_info[0].id}"
    return attachment
