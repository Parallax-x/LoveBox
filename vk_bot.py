from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import os
import requests
import random
from db import User, MatchingUser, Photos, BlacklistedUser, Session

session = Session()


class VKinderBot:

    def __init__(self):
        self.token_bot = os.getenv('token_group')
        self.token_user = os.getenv('token_user')
        self.vk = vk_api.VkApi(token=self.token_bot)
        self.longpoll = VkLongPoll(self.vk)

    def get_vk(self, url, new_params, **kwargs):
        params = {
            'access_token': self.token_user,
            'v': '5.141'
        }
        params.update(new_params)
        response = requests.get(url, params=params, **kwargs)
        if response.status_code != requests.codes.ok:
            print(f'Ошибка при запросе к серверу: {response.text}')
            return None
        result = response.json()
        if 'error' in result:
            print(f'Ошибка в данных: {result["error"]}')
            return None
        return result['response']

    def write_msg(self, user_id, message, keyboard=None):
        post = {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)}
        if keyboard is not None:
            post['keyboard'] = keyboard.get_keyboard()
        else:
            post = post
        self.vk.method('messages.send', post)

    def start(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text.lower()
                if text in ['start', 'начать']:
                    keyboard = VkKeyboard(one_time=False)
                    keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
                    keyboard.add_button('Help', color=VkKeyboardColor.SECONDARY)
                    self.write_msg(event.user_id, f'Привет! \n'
                                                  f'Это LoveBox! \n'
                                                  f'Найти тебе пару?', keyboard=keyboard)
                    self.after_start()
                else:
                    if text not in ['start', 'начать']:
                        self.write_msg(event.user_id, 'Введите start или начать, чтобы запустить бота!')
                        self.start()

    def after_start(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text.lower()
                if text == 'да':
                    self.start_vkinder(event)
                elif text == 'нет':
                    self.write_msg(event.user_id, 'До свидания! Заходите еще!')
                    self.start()
                elif text == 'help':
                    self.write_msg(event.user_id, 'Приложение для поиска партнера, при вводе start \
                    или начать вы запустите бота. Последовательно заполните данные для поиска партнера.')
                    self.after_start()
                else:
                    self.write_msg(event.user_id, 'Не понял вашего сообщения!')
                    self.start()

    def start_vkinder(self, event):
        dating_id = event.user_id
        user = session.query(User).filter(User.dating_id == dating_id).all()

        if len(user) == 0:
            self.get_user(event)
            self.start_vkinder(event)
        else:
            self.update_user_data(event)
            # self.search_partner_command(event)

    def search_partner_command(self, event):
        dating_id = event.user_id
        user = session.query(User).filter(User.dating_id == dating_id).all()
        age_from = user[0].age_from
        age_to = user[0].age_to
        city = user[0].city
        partners_sex = user[0].partners_sex
        self.choose_partner(event, partners_sex, city, age_to, age_from)

    def choose_partner(self, event, partners_sex, city, age_to, age_from):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('❤', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('👎🏻', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('Понравившиеся', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Изменить параметры', color=VkKeyboardColor.PRIMARY)
        self.write_msg(event.user_id, 'Поехали', keyboard=keyboard)

        partners_get = self.search_partner(partners_sex, city, age_to, age_from)
        if len(partners_get) == 0:
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Да', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
            self.write_msg(event.user_id, 'Совпадений не найдено! Хотите изменить параметры?', keyboard=keyboard)
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                    text = event.text.lower()
                    if text == 'да':
                        self.update_user_data(event)
                    elif text == 'нет':
                        self.write_msg(event.user_id, 'До свидания! Заходите еще!')
                        self.start()
                    else:
                        self.write_msg(event.user_id, 'Не понял вас, попробуйте поменять параметры поиска!')
                        self.update_user_data(event)

        list_partners = []
        for partners in partners_get:
            if partners['is_closed'] is False:
                partner_id = (partners['first_name'], partners['last_name'], partners['id'])
                list_partners.append(partner_id)
        id_dater = event.user_id
        liked_users = session.query(MatchingUser).filter(MatchingUser.id_dater == id_dater).all()
        ignore_users = session.query(BlacklistedUser).filter(BlacklistedUser.id_dater == id_dater).all()

        bd_id = []
        for match_id in liked_users:
            us_id = match_id.matching_id
            bd_id.append(us_id)

        for ign_id in ignore_users:
            ig_id = ign_id.blacklisted_id
            bd_id.append(ig_id)

        for partner in list_partners:
            if partner[2] not in bd_id:
                photo_list = self.choose_photo(partner[2])
                photo_dict = {}
                # if photo_list['count'] >= 3:
                for photo in photo_list['items']:
                    photo_id = photo['id']
                    likes = photo['likes']['count']
                    photo_dict[likes] = f'photo{partner[2]}_{photo_id}'
                # else:
                #     pass
                # sorted_photo_dict = {}
                # for k in sorted(photo_dict.keys(), reverse=True):
                #     sorted_photo_dict[k] = photo_dict[k]

                if len(photo_dict) > 3:
                    photos = list(photo_dict.values())[:-4:-1]
                else:
                    photos = list(photo_dict.values())

                link_photo = []
                for photog in photo_list['items']:
                    if photog['likes']['count'] in list(photo_dict.keys())[:-4:-1]:
                        link_photo.append([photog['id'], photog['likes']['count'], photog['sizes'][-1]['url']])

                self.write_msg(event.user_id, partner[0] + ' ' + partner[1])

                link = 'https://vk.com/id' + str(partner[2])
                self.write_msg(event.user_id, link)
                for photo_send in photos:
                    self.send_photo(event.user_id, photo_send)
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                        text = event.text
                        if text == '❤':
                            self.add_liked_partner(link_photo, partner[2])
                            break
                        elif text == '👎🏻':
                            self.add_ignore(partner)
                            break
                        elif text == 'Понравившиеся':
                            self.show_liked(event)
                            break
                        elif text == 'Изменить параметры':
                            self.update_user_data(event)
                            break
                        else:
                            self.write_msg(event.user_id, 'Не понял вас, попробуйте еще.')
            elif partner[2] in bd_id:
                continue
        else:
            self.not_peoples(event)
            # self.write_msg(event.user_id, 'Новых совпадений не найдено! Хотите посмотреть понравившихся \n'
            #                               'или изменить параметры поиска?')
            # keyboard = VkKeyboard(one_time=False)
            # keyboard.add_button('Понравившиеся', color=VkKeyboardColor.PRIMARY)
            # keyboard.add_button('Изменить', color=VkKeyboardColor.NEGATIVE)
            # for event in self.longpoll.listen():
            #     if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            #         text = event.text.lower()
            #         if text == 'понравившиеся':
            #             self.show_liked(event)
            #             self.start()
            #         elif text == 'изменить':
            #             self.update_user_data(event)
            #         else:
            #             self.write_msg(event.user_id, 'Не понял вас, попробуйте еще.')
            #             self.start()

    def not_peoples(self, event):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Понравившиеся', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Изменить', color=VkKeyboardColor.NEGATIVE)
        self.write_msg(event.user_id, 'Новых совпадений не найдено! Хотите посмотреть понравившихся \n'
                                      'или изменить параметры поиска?', keyboard=keyboard)
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = event.text.lower()
                if text == 'понравившиеся':
                    self.show_liked(event)
                    self.start()
                elif text == 'изменить':
                    self.update_user_data(event)
                else:
                    self.write_msg(event.user_id, 'Не понял вас, попробуйте снова. Введите Начать или Start')
                    self.start()

    def get_user(self, event):
        info = self.get_vk('https://api.vk.com/method/users.get', {'user_ids': event.user_id})[0]
        first_name = info['first_name']
        last_name = info['last_name']
        city = self.get_city(event.user_id)
        sex = self.get_gender(event.user_id)
        age_to = self.get_age_to(event.user_id)
        age_from = self.get_age_from(event.user_id)
        user = User(dating_id=event.user_id, first_name=first_name, last_name=last_name, age_to=age_to,
                    age_from=age_from, city=city, partners_sex=sex)
        session.add(user)
        session.commit()

    def get_gender(self, user_id, gender=''):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Девушка', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Парень', color=VkKeyboardColor.SECONDARY)
        self.write_msg(user_id, 'Какого пола нужен партнер?', keyboard=keyboard)
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = event.text
                if text == 'Девушка':
                    gender = '1'
                elif text == 'Парень':
                    gender = '2'
                else:
                    self.write_msg(event.user_id, 'Выберите: девушка или парень.')
                    self.get_gender(event.user_id)
                return gender

    def get_city(self, user_id):
        self.write_msg(user_id, 'В каком городе искать партнера?')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                city_name = event.text.lower()
                city = self.get_vk(f'https://api.vk.com/method/database.getCities', {'country_id': '1',
                                                                                     'q': city_name,
                                                                                     'count': '1'})['items']
                if len(city) == 0:
                    self.write_msg(event.user_id, f'Не нашел города с названием {city_name}.')
                    self.get_city(event.user_id)
                else:
                    city = city_name
                return city

    def get_age_to(self, user_id):
        self.write_msg(user_id, 'Укажите максимальный возраст.')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                age_to = event.text.lower()
                return age_to

    def get_age_from(self, user_id):
        self.write_msg(user_id, 'Укажите минимальный возраст.')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                age_from = event.text.lower()
                return age_from

    def search_partner(self, partners_sex, city, age_to, age_from):
        partners6 = self.get_vk('https://api.vk.com/method/users.search', {'is_closed': 'False',
                                                                           'has_photo': '1',
                                                                           'sex': partners_sex,
                                                                           'status': '6', 'hometown': city,
                                                                           'age_from': age_from,
                                                                           'age_to': age_to, 'count': '1000'})['items']
        partners1 = self.get_vk('https://api.vk.com/method/users.search', {'is_closed': 'False',
                                                                           'has_photo': '1',
                                                                           'sex': partners_sex,
                                                                           'status': '1', 'hometown': city,
                                                                           'age_from': age_from,
                                                                           'age_to': age_to, 'count': '1000'})['items']
        partners = partners6 + partners1
        return partners

    def choose_photo(self, partner_id):
        photo_list = self.get_vk('https://api.vk.com/method/photos.get', {'owner_id': partner_id,
                                                                          'album_id': 'profile',
                                                                          'rev': 1,
                                                                          'extended': 1,
                                                                          'photo_sizes': 0})
        return photo_list

    def send_photo(self, user_id, photo_send):
        response = self.get_vk(f'https://api.vk.com/method/messages.send', {'access_token': self.token_bot,
                                                                            'user_id': user_id,
                                                                            'random_id': random.getrandbits(64),
                                                                            'attachment': photo_send,
                                                                            'v': 5.141})
        return response

    def add_liked_partner(self, link_photo, partner_id):
        user = session.query(User).all()
        id_dater = user[0].dating_id
        like_partner_info = self.get_vk('https://api.vk.com/method/users.get', {'user_ids': partner_id,
                                                                                'fields': 'sex'})[0]
        first_name = like_partner_info['first_name']
        last_name = like_partner_info['last_name']
        sex = like_partner_info['sex']
        like_partner = MatchingUser(matching_id=partner_id, first_name=first_name, last_name=last_name,
                                    id_dater=id_dater, sex=sex)
        session.add(like_partner)
        session.commit()

        for photo in link_photo:
            pic_link = photo[2]
            pic_likes = photo[1]
            photo = Photos(id_matcher=partner_id, photo_link=pic_link, likes_count=pic_likes)
            session.add(photo)
            session.commit()

    def add_ignore(self, partner):
        user = session.query(User).all()
        id_dater = user[0].dating_id
        blacklisted_id = partner[2]
        first_name = partner[0]
        last_name = partner[1]
        ignore_user = BlacklistedUser(blacklisted_id=blacklisted_id, first_name=first_name, last_name=last_name,
                                      id_dater=id_dater)
        session.add(ignore_user)
        session.commit()

    def show_liked(self, event):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Продолжить поиск', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Изменить параметры', color=VkKeyboardColor.SECONDARY)
        id_dater = event.user_id
        liked_users = session.query(MatchingUser).filter(MatchingUser.id_dater == id_dater).all()

        for liked_user in liked_users:
            first_name = liked_user.first_name
            last_name = liked_user.last_name
            us_id = liked_user.matching_id
            user_info = first_name + ' ' + last_name + ' ' + 'https://vk.com/id' + str(us_id)
            self.write_msg(event.user_id, user_info)

        self.write_msg(event.user_id, 'Продолжить поиск?', keyboard=keyboard)
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = event.text.lower()
                if text == 'продолжить поиск':
                    self.search_partner_command(event)
                elif text == 'изменить параметры':
                    self.update_user_data(event)
                else:
                    self.write_msg(event.user_id, 'Не понял вашего сообщения.')
                    self.start()

    def update_user_data(self, event):
        # user = session.query(User).all()[0]
        us_id = event.user_id
        city = self.get_city(us_id)
        sex = self.get_gender(us_id)
        age_to = self.get_age_to(us_id)
        age_from = self.get_age_from(us_id)
        session.query(User).filter(User.dating_id == us_id).update({'age_from': age_from,
                                                                    'age_to': age_to,
                                                                    'partners_sex': sex,
                                                                    'city': city})
        session.commit()
        self.search_partner_command(event)


bot = VKinderBot()
vk = vk_api.VkApi(token=os.getenv('token_group'))
longpoll = VkLongPoll(vk)
bot.start()
