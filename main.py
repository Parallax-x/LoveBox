from vk import search_user

if __name__ == "__main__":
    for i in search_user(name='Никифоров', age_from=20, age_to=40, sex=0, city='Москва'):
        print(i)