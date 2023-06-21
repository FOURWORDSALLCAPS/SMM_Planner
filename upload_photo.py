import requests

from vkbottle import API, VKAPIError


async def upload_photo_to_album(token, group_id, album_id, file_path):
    try:
        api = API(token)
        upload_url = await api.photos.get_upload_server(group_id=group_id, album_id=album_id)
        response = requests.post(upload_url.upload_url, files={'photo': open(file_path, 'rb')})
        response.raise_for_status()
        if not response.ok:
            return None
        result_upload = response.json()
        photos_list = result_upload['photos_list']
        server = result_upload['server']
        hash_value = result_upload['hash']
        photo_info = await api.photos.save(album_id=album_id,
                                           group_id=group_id,
                                           server=server,
                                           hash=hash_value,
                                           photos_list=photos_list)
        attachment = f"photo{photo_info[0].owner_id}_{photo_info[0].id}"
        return attachment
    except VKAPIError as e:
        print(f"VK API error occurred: {e}")
        return None
