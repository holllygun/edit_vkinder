import requests
from pprint import pprint
from datetime import date
import time
from heapq import nlargest


class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version

    def common_params(self):
        return{
            'access_token': self.token,
            'v': self.version
        }

    def get_info_user(self):
        params = self.common_params()
        params.update({"user_id": self.id, "fields": "city, bdate, sex, domain"})
        response = requests.get('https://api.vk.com/method/users.get', params=params).json()
        return response["response"][0]

    def get_profile_photo(self, user_id):  # Получение фото
        params = self.common_params()
        params.update(
            {"owner_id": user_id, "count": 1000, "album_id": "profile", "photo_sizes": "0", "extended": "1", "rev": 1})
        response = requests.get('https://api.vk.com/method/photos.get', params=params).json()
        time.sleep(0.1)
        response = response['response']
        arr = [item['likes']['count']for item in response['items']]
        res = nlargest(3, arr)
        photos_list = []
        for item in response['items']:
            owner_id = item['owner_id']
            photo_id = item['id']
            if item['likes']['count'] in res:
                photos_list.append({f'photo{owner_id}_{photo_id}_{self.token}': item['likes']['count']})
        print(f"user photos: {photos_list}")
        return photos_list

    def search_people(self, city, age, sex):#change to 1000
        params = self.common_params()
        params.update(
            {"user_id": self.id, "count": 100, "city": city, "age_from": age - 2, "age_to": age + 5, "sex": sex,
             "fields": "id, domain, city, bdate, sex"}
        )
        response = requests.get('https://api.vk.com/method/users.search', params=params).json()
        return response['response']

    def calculate_age(self, b_date):
        today = date.today()
        day, month, year = b_date.split('.')
        day, month, year = int(day), int(month), int(year)
        age = today.year - year - ((today.month, today.day) < (month, day))
        return age

    def users_params(self):
        try:
            user = self.get_info_user()
            city = user['city']['id']
            gender = user['sex']
            if gender == 1:
                match_gender = 2
            else:
                match_gender = 1
            age = self.calculate_age(user['bdate'])
            info_param_user = {"city": city, "sex": match_gender, "age": age}
        except KeyError:
            return 'Недостаточно информации для добавления в список'
        return info_param_user

    def get_matches(self):
        current_user = self.get_info_user()
        try:
            city = current_user['city']['id']
            sex = current_user['sex']
            if sex == 1:
                match_gender = 2
            else:
                match_gender = 1
            age = self.calculate_age(current_user['bdate'])
            matches_for_user = self.search_people(city, age, match_gender)
        except KeyError:
            return 'Недостаточно информации для поиска. Пожалуйста, добавьте в личные данные ваш возраст и/или город.'
        print('MATCHES', matches_for_user)
        return matches_for_user['items']

    def users_list(self):
        matches_file = self.get_matches()
        print(f'matches_from_vk:{matches_file}')
        matches_list = []
        for match in matches_file:
            try:
                if match['is_closed'] is True:  # исключаем закрытые профили
                    continue
                else:
                    matches_list.append(self.user_info_for_db(match))
            except KeyError:
                continue
        pprint(matches_list)
        return matches_list

    def user_info_for_db(self, user_dict):
        name = user_dict['first_name']
        last_name = user_dict['last_name']
        sex = user_dict['sex']
        age = self.calculate_age(user_dict['bdate'])
        city = user_dict['city']['id']
        vk_id = user_dict['id']
        vk_link = f"https://vk.com/{user_dict['domain']}"
        users_photos = self.get_profile_photo(vk_id)
        user = [name, last_name, age, sex, city, vk_id, users_photos, vk_link]
        return user

    def create_user(self):
        user = self.get_info_user()
        user_list = self.user_info_for_db(user)
        return user_list
