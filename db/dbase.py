from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
from datetime import datetime


class DatabaseMongo:
    def __init__(self, db_name='drone_control_system'):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[db_name]
        self.operators = self.db.operators
        self.admins = self.db.admins
        self.missions = self.db.missions
        # Создаем индексы для быстрого поиска
        self.operators.create_index('login', unique=True)
        self.admins.create_index('login', unique=True)

        # Инициализация тестовых данных
        self.initialize_test_data()

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, hashed_password, user_password):
        return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

    def initialize_test_data(self):
        # Добавляем тестового админа, если его нет
        if self.admins.count_documents({}) == 0:
            self.add_admin('admin', 'admin123', 'Администратор')

        # Добавляем тестовых операторов, если их нет
        if self.operators.count_documents({}) == 0:
            self.add_operator('ivanov', 'ivanov123', 'Иванов Иван Иванович')
            self.add_operator('petrov', 'petrov123', 'Петров Петр Петрович')

        # Добавляем тестовые миссии, если их нет
        if self.missions.count_documents({}) == 0:
            operators = list(self.operators.find({}, {'_id': 1}))
            if operators:
                self.add_mission(
                    operator_id=operators[0]['_id'],
                    drone_model='DJI Mavic 3',
                    drone_count=2,
                    status='В процессе',
                    description='Разведка местности'
                )
                self.add_mission(
                    operator_id=operators[1]['_id'],
                    drone_model='DJI Phantom 4',
                    drone_count=1,
                    status='Завершена',
                    description='Фотосъемка объекта'
                )

    # Операторы
    def add_operator(self, login, password, full_name):
        hashed_password = self.hash_password(password)
        operator = {
            'login': login,
            'password': hashed_password,
            'full_name': full_name,
            'created_at': datetime.now()
        }
        try:
            return self.operators.insert_one(operator).inserted_id
        except:
            return None

    def authenticate_operator(self, login, password):
        operator = self.operators.find_one({'login': login})
        if operator and self.check_password(operator['password'], password):
            return operator
        return None

    def get_operator(self, operator_id):
        return self.operators.find_one({'_id': ObjectId(operator_id)})

    # Админы
    def add_admin(self, login, password, full_name):
        hashed_password = self.hash_password(password)
        admin = {
            'login': login,
            'password': hashed_password,
            'full_name': full_name,
            'created_at': datetime.now()
        }
        try:
            return self.admins.insert_one(admin).inserted_id
        except:
            return None

    def authenticate_admin(self, login, password):
        admin = self.admins.find_one({'login': login})
        if admin and self.check_password(admin['password'], password):
            return admin
        return None

    # Миссии
    def add_mission(self, operator_id, drone_model, drone_count, status, description=''):
        mission = {
            'operator_id': ObjectId(operator_id),
            'drone_model': drone_model,
            'drone_count': drone_count,
            'status': status,
            'description': description,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        return self.missions.insert_one(mission).inserted_id

    def get_all_missions(self):
        return list(self.missions.aggregate([
            {
                '$lookup': {
                    'from': 'operators',
                    'localField': 'operator_id',
                    'foreignField': '_id',
                    'as': 'operator'
                }
            },
            {
                '$unwind': '$operator'
            },
            {
                '$project': {
                    '_id': 1,
                    'operator_full_name': '$operator.full_name',
                    'drone_model': 1,
                    'drone_count': 1,
                    'status': 1,
                    'description': 1,
                    'created_at': 1
                }
            }
        ]))

    def get_mission(self, mission_id):
        return self.missions.find_one({'_id': ObjectId(mission_id)})

    def update_mission_status(self, mission_id, new_status):
        return self.missions.update_one(
            {'_id': ObjectId(mission_id)},
            {'$set': {'status': new_status, 'updated_at': datetime.now()}}
        )

    def delete_mission(self, mission_id):
        return self.missions.delete_one({'_id': ObjectId(mission_id)})

    def close(self):
        self.client.close()