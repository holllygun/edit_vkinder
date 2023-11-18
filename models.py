import sqlalchemy
import yaml
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import func

Base = declarative_base()

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)
password = config.get('DB_PASS', '')
DSN = f"postgresql://postgres:{password}@localhost:5432/vkinder_db"
engine = sqlalchemy.create_engine(DSN)


class Users(Base):
    __tablename__ = "users"

    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=False)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    gender = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=False)
    city = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=False)
    vk_id = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=False, unique=True)
    vk_link = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=False, unique=True)
    user_insert_time = sqlalchemy.Column(sqlalchemy.TIMESTAMP, server_default=func.now())

    photos = relationship("Photos", backref="user")
    favorite = relationship("Favorites", primaryjoin="Users.user_id == Favorites.user_id", uselist=False, backref="user")
    favorites = relationship("Favorites", primaryjoin="Users.user_id == Favorites.added_user_id", backref="added_by_user")

    def __str__(self):
        return f"User {self.user_id} : {self.name}, {self.surname}, {self.age}, {self.gender}, {self.city}, {self.vk_id}, {self.user_insert_time}"


class Photos(Base):
    __tablename__ = "photos"

    photo_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id"), nullable=False)
    url_photo = sqlalchemy.Column(sqlalchemy.String(length=255), nullable=False, unique=True)
    likes = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    photo_insert_time = sqlalchemy.Column(sqlalchemy.TIMESTAMP, server_default=func.now())

    def __str__(self):
        return f"Photo {self.photo_id} : {self.user_id}, {self.url_photo}, {self.likes}, {self.photo_insert_time}"


class Favorites(Base):
    __tablename__ = "favorites"

    favorite_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id"), nullable=False)
    added_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id"), nullable=False)
    favorite_creation_time = sqlalchemy.Column(sqlalchemy.TIMESTAMP, server_default=func.now())

    __table_args__ = (
        sqlalchemy.UniqueConstraint('user_id', 'added_user_id'),
    )


class UserActions(Base):
    __tablename__ = "user_actions"

    action_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id"), nullable=False)
    action_type = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=False)
    action_insert_time = sqlalchemy.Column(sqlalchemy.TIMESTAMP, server_default=func.now())


def create_tables():
    print("Идет создание таблиц")
    Base.metadata.create_all(engine)
    print("Таблицы созданы.")


def drop_tables():
    print("Идет удаление таблиц")
    Base.metadata.drop_all(engine)
    print("Таблицы удалены.")


def main():
    inspector = sqlalchemy.inspect(engine)

    if not inspector.get_table_names():
        print("Таблиц в Базе данных не существует. Создаем таблицы.")
        create_tables()
    else:
        print("Таблицы уже существуют в Базе данных")
        confirmation = input("Вы действительно хотите удалить таблицы? (Да/Нет): ")
        if confirmation.lower() == "да":
            drop_tables()
        else:
            print("Таблицы не удалены.")


# main()
