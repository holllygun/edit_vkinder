from sqlalchemy.orm import sessionmaker
from models import engine

from models import Users, Photos, Favorites, UserActions


class Db_data:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def get_matches_list(self, params): #get users by parameters from db
        print('PARAMS:', params)
        city = params["city"]
        print(city)
        new_sex = params['sex']
        print(new_sex)
        age = params['age']
        print(age)
        matches_lst = []
        db_info = self.session.query(Users).filter(Users.city == str(city), Users.gender == str(new_sex), Users.age.between((age-2), (age+5))).all()
        for item in db_info:
            user = {
                'age': item.age,
                'name': item.name,
                'surname': item.surname,
                'link': item.vk_link,
                'user_id': item.user_id
            }
            matches_lst.append(user)
        return matches_lst

    def print_users(self, user: dict):
        age = user['age']
        name = user['name']
        surname = user['surname']
        link = user['link']
        if age % 10 == 1:
            sentence = 'год'
        elif 1 < age % 10 < 5:
            sentence = 'года'
        else:
                sentence = 'лет'
        return (f'\n- {name} {surname}\n'
                    f'- {age} {sentence}\n'
                    f'- {link}\n')

    def three_photos(self, user_id):
        answer = self.session.query(Photos.url_photo).filter(Photos.user_id == user_id).all()
        an = []
        for a in answer:
            an.append(a.url_photo)
        return an

    def show_favorites(self, id):
        user_id = self.session.query(Users.user_id).filter(Users.vk_id.like(str(id))).all()
        user_id = user_id[0][0]
        db_info = self.session.query(Favorites.added_user_id).filter(Favorites.user_id== user_id).all()
        res_list = []
        for item in db_info:
            added_user_id = item[0]
            user_info = self.session.query(Users.name, Users.surname, Users.vk_link).filter(Users.user_id == added_user_id)
            res_list.append(user_info[0])
        message = ''
        for item in res_list:
            message +=  (f'\n- {item[0]} {item[1]}\n'
                    f'{item[2]}\n')
        return message

    def user_exist(self, id):
        user_id = self.session.query(Users.user_id).filter(Users.vk_id.like(str(id))).all()
        user_id = int(user_id[0][0])
        answer = self.session.query(UserActions.action_type).filter(UserActions.user_id == user_id).filter(UserActions.action_type.like('start')).all()
        return answer

    def last_user(self, id):
        user_id = self.session.query(Users.user_id).filter(Users.vk_id.like(str(id))).all()
        user_id = int(user_id[0][0])
        res = self.session.query(UserActions.action_type).filter(UserActions.action_type.like(str('%break%'))).filter(UserActions.user_id==user_id).all()
        count = -1
        if res:
            res = res[-1]
            for item in res:
                count = item.split(',')[1]
        return int(count)

