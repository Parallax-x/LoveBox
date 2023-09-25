import vk_api


with open('token.txt', 'r') as file_object:
    token = file_object.readline().strip()

version: str = '5.131'

session = vk_api.VkApi(token=token)
