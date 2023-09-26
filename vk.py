from typing import Dict, Any, List

import vk_api


def search_user(name: str, age_from: int, age_to: int, sex: int, city: str):
    with open('token.txt', 'r') as file_object:
        token = file_object.readline().strip()

    version: str = '5.154'

    params = {
        'v': version,
        'count': 1000,
        'is_closed': False,
        'fields': 'city, bdate',
        'q': name,
        'age_from': age_from,
        'age_to': age_to,
        'sex': sex,
        'has_photo': 1,
        'online': 1,
        'sort': 0
            }
    session = vk_api.VkApi(token=token)
    result = session.method('users.search', params)['items']
    for item in result:
        dic_user = {}
        if item['is_closed'] or 'city' not in item:
            continue
        if item['city']['title'] != city:
            continue
        params_photo = {
            'owner_id': item['id'],
            'album_id': 'profile',
            'v': version,
            'extended': 1
        }
        photo_user = session.method('photos.get', params_photo)['items']
        sort_photo = sorted(photo_user, key=lambda x: x['likes']['count'], reverse=True)
        dic_user['id'] = item['id']
        dic_user['first_name'] = item['first_name']
        dic_user['last_name'] = item['last_name']
        dic_user['city'] = city
        if item['bdate']:
            dic_user['date_birth'] = item['bdate']
        else:
            dic_user['date_birth'] = None
        list_url = []
        for sized in sort_photo:
            sort_photo_url = sorted(sized['sizes'], key = lambda d: d['height'])
            list_url.append(sort_photo_url[0])
            if len(list_url) == 3:
                break
        dic_user['photo_url'] = list_url
        yield dic_user

