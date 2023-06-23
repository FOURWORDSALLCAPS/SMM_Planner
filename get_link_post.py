def get_link_post_vk(group_id, post_id):
    post_url = f'https://vk.com/wall-{group_id}_{post_id}'
    return post_url


def get_link_post_tg(group_id, post_id):
    post_url = f'https://t.me/{group_id[1:]}/{post_id}'
    return post_url