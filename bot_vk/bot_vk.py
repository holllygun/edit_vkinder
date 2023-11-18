from random import randrange

import vk_api

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import yaml
from vk_info import VK
from db_injections import Methods
from pick_data_from_db import Db_data

# Чтение значений из файла конфигурации config.yaml
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

GROUP_TOKEN = config.get('GROUP_TOKEN', '')
ACCESS_TOKEN = config.get('ACCESS_TOKEN', '')

vk_session = vk_api.VkApi(token=GROUP_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

methods = Methods()
db_picker = Db_data()


class Bot:
    def __init__(self):
        pass

    def bot_typing(self, id):
        vk.messages.setActivity(user_id=id, group_id=223098125, peer_id=id, type='typing')
    def sender(self, id, text, photo: None, **kwargs):  # функция для отправки сообщений
        vk.messages.send(user_id=id, message=text, attachment=photo, random_id=randrange(10 ** 7), **kwargs)

    def user_name(self, user_id):  # достать имя пользователя
        user_get = vk.users.get(user_ids=user_id)
        user_get = user_get[0]['first_name']
        return user_get

    def favorites_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        buttons = ['Вернуться', 'Закончить']
        buttons_colors = [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]
        for btn, btn_color in zip(buttons, buttons_colors):
            keyboard.add_button(btn, btn_color)
        keyboard.add_line()
        keyboard.add_button('Избранное', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()

    def yes_no_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        buttons = ['Да!', 'Я передумал']
        buttons_colors = [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]
        for btn, btn_color in zip(buttons, buttons_colors):
            keyboard.add_button(btn, btn_color)
        return keyboard.get_keyboard()

    def standart_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        buttons = ['Дальше', 'Добавить', 'Закончить']
        buttons_colors = [VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]
        for btn, btn_color in zip(buttons, buttons_colors):
            keyboard.add_button(btn, btn_color)
        keyboard.add_line()
        keyboard.add_button('Избранное', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()

    def user_for_db(self, id, lst: list):
        if id in lst:
            print('Пользователь был добавлен ранее.')
        else:
            vk_api = VK(ACCESS_TOKEN, id)
            user_list = vk_api.create_user()
            param = vk_api.users_params()
            print('VK PARAMS:', param)
            methods.create_user(user_list)
            lst.append(id)
            lst.append({'param': param, 'vk_api': vk_api})


    def hello(self, param, vk_api, id):
        methods.add_actions('hello', id)
        self.sender(id, f'Привет, {self.user_name(id)}! Начнем?💞 Сбор информации может занять несколько минут:)',
                    None, keyboard=self.yes_no_keyboard())
        self.bot_typing(id)
        counter = db_picker.last_user(id)
        if db_picker.user_exist(id):
            matches = db_picker.get_matches_list(param)
        else:
            for user in vk_api.users_list():
                methods.create_user(user)
                methods.add_photo(user)
            matches = db_picker.get_matches_list(param)
        return{'counter': counter, 'matches': matches}

    def yes(self, counter, matches, id):
        methods.add_actions('start', id)
        counter += 1
        if counter < len(matches):
            user_id = matches[counter]['user_id']
            self.sender(id, f'Выберите действие{db_picker.print_users(matches[counter])}',
                        db_picker.three_photos(user_id), keyboard=self.standart_keyboard())
        else:
            self.sender(id, 'Пользователи закончились:( Начать сначала?', None, keyboard=self.yes_no_keyboard())
            counter = -1
        return counter

    def next_or_back(self, counter, matches, id):
        methods.add_actions('next', id)
        counter += 1
        if counter < len(matches):
            user_id = matches[counter]['user_id']
            self.sender(id, f"Следующий пользователь: {db_picker.print_users(matches[counter])}",
                        db_picker.three_photos(user_id), keyboard=self.standart_keyboard())
        else:
            self.sender(id, 'Пользователи закончились:( Начать сначала?', None, keyboard=self.yes_no_keyboard())
            counter = -1
        return counter

    def add(self, counter, matches, id):
        methods.add_actions('add_user', id)
        user_id = matches[counter]['user_id']
        action = methods.add_to_favorites(id, user_id)
        if action == "Пользователь с таким ID уже существует":
            self.sender(id, f'Пользователь был добавлен в избранное ранее', None, keyboard=self.favorites_keyboard())
        else:
            self.sender(id, f'Добавили в избранное👌', None, keyboard=self.favorites_keyboard())

    def finish(self, counter, id):
        methods.add_actions(f'break, {int(counter)}', id)
        self.sender(id, 'Пока:( Чтобы снова начать поиск, напиши "Привет":)', None)

    def show_favorites(self, id):
        methods.add_actions('show_favorites', id)
        self.sender(id, f'Избранные профили 📃:\n {db_picker.show_favorites(id)}', None,
                    keyboard=self.favorites_keyboard())


    def process (self, event, lst, counter, matches):
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                msg = event.text.lower()
                id = event.user_id
                self.user_for_db(id, lst)
                info = lst[1]
                vk_api, param = info['vk_api'], info['param']
                if msg == 'привет' or msg == 'начать':
                    res = self.hello(param, vk_api, id)
                    counter, matches = res['counter'], res['matches']
                elif msg == 'да!':
                    print('YES', counter)
                    counter = self.yes(counter, matches, id)
                    counter = self.next_or_back(counter, matches, id)
                elif msg == 'добавить':
                    self.add(counter, matches, id)
                elif msg == 'закончить' or msg == 'я передумал':
                    self.finish(counter, id)
                elif msg == 'избранное':
                    self.show_favorites(id)
                else:
                    self.sender(id, 'Я вас не понимаю:(', None)
            return counter

    def longpoll_event(self):  # отправить ответ и создать клавиатуру
        counter = -1
        lst = []
        matches = []
        for event in longpoll.listen():
            # не работает
            # new_counter = self.process(event, lst, counter, matches)
            # counter = new_counter
            # print('COUNTER', new_counter)

            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg = event.text.lower()
                    id = event.user_id
                    self.user_for_db(id, lst)
                    info = lst[1]
                    vk_api, param = info['vk_api'], info['param']
                    if msg == 'привет' or msg == 'начать':
                        res = self.hello(param, vk_api, id)
                        counter, matches = res['counter'], res['matches']
                    elif msg == 'да!':
                        counter = self.yes(counter, matches, id)
                    elif msg == 'дальше' or msg == 'вернуться':
                        counter = self.next_or_back(counter, matches, id)
                    elif msg == 'добавить':
                        self.add(counter, matches, id)
                    elif msg == 'закончить' or msg == 'я передумал':
                        self.finish(counter, id)
                    elif msg == 'избранное':
                        self.show_favorites(id)
                    else:
                        self.sender(id, 'Я вас не понимаю:(', None)
