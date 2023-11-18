from sqlalchemy.orm import sessionmaker
from models import engine
from sqlalchemy import exc

from models import Users, Photos, Favorites, UserActions


class Methods:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def clear_tables(self):
        self.session.query(Photos).delete()
        self.session.query(Favorites).delete()
        self.session.query(UserActions).delete()
        self.session.query(Users).delete()
        self.session.commit()
        print("Таблицы очищены")

    def create_user(self, info_user: list):
        try:
            self.name = info_user[0]
            self.surname = info_user[1]
            self.age = info_user[2]
            self.sex = info_user[3]
            self.city = info_user[4]
            self.vk_id = info_user[5]
            self.link = info_user[7]
            user = Users(name=self.name, surname = self.surname, age = self.age, gender=self.sex, city=self.city, vk_id=self.vk_id, vk_link=self.link)
            self.session.add(user)
            self.session.commit()
            print(f"Пользователь добавлен: ID {user.user_id}, {user.name}, {user.surname}, {user.age}, {user.gender}, {user.city}")
        except exc.IntegrityError:
            self.session.rollback()
            print("Пользователь с таким ID уже существует")

    def add_photo(self, info_user: list):
        photography = info_user[6]
        try:
            user = self.session.query(Users).filter(Users.vk_id.like(str(info_user[5]))).all()
            for u in user:
                user_id = u.user_id
            # Проверяем количество фотографий у пользователя
            photo_count = self.session.query(Photos).filter(Photos.user_id == user_id).count()

            if photo_count < 3:
                if isinstance(photography, list):
                    for i in photography:
                        for k, j in i.items():
                            url_photo = k
                            likes = j

                            # Проверяем, существует ли фотография с таким URL в базе
                            existing_photo = self.session.query(Photos).filter(Photos.url_photo == url_photo).first()

                            if not existing_photo:
                                # Фотографии с таким URL еще нет, добавляем ее
                                photo = Photos(user_id=user_id, url_photo=url_photo, likes=likes)
                                self.session.add(photo)
                                self.session.commit()
                                print(f"Фотография добавлена: ID {photo.photo_id}, Пользователь ID {photo.user_id}, URL {photo.url_photo}, Лайки {photo.likes}")
                            else:
                                print(f"Фотография с URL {url_photo} уже существует и не будет добавлена.")

            else:
                print("У пользователя уже есть 3 фотографии, новые фотографии не добавлены.")

        except exc.IntegrityError:
            self.session.rollback()
            print("Произошла ошибка при добавлении фотографии.")

    def add_to_favorites(self, id, user):
        user_id = self.session.query(Users.user_id).filter(Users.vk_id.like(str(id))).all()
        user_id = user_id[0][0]
        try:
            added_user_id = user
            favorite = Favorites(added_user_id=added_user_id, user_id=user_id)
            self.session.add(favorite)
            self.session.commit()
            print(f"Пользователь добавлен.")
        except exc.IntegrityError:
            self.session.rollback()
            print("Пользователь с таким ID уже существует")
            return "Пользователь с таким ID уже существует"

    def add_actions(self, msg, u_id):
        user_id = self.session.query(Users.user_id).filter(Users.vk_id.like(str(u_id))).all()
        user_id = user_id[0][0]
        user_action = UserActions(user_id=user_id, action_type=msg)
        self.session.add(user_action)
        self.session.commit()



