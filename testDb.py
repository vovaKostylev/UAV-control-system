from pymongo import MongoClient
from bson import ObjectId
import bcrypt
from datetime import datetime


def initialize_database():
    # Подключение к MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['drone_control_system']

    # Коллекции
    operators = db['operators']
    admins = db['admins']
    missions = db['missions']

    # Хеширование паролей
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # 1. Добавляем админов (если их нет)
    if admins.count_documents({}) == 0:
        admin_data = [
            {
                'login': 'admin',
                'password': hash_password('admin123'),
                'full_name': 'Главный Администратор',
                'avatar_url': '',  # Пустая ссылка на изображение
                'created_at': datetime.now()
            },
            {
                'login': 'supervisor',
                'password': hash_password('super123'),
                'full_name': 'Супервайзер Системы',
                'avatar_url': '',  # Пустая ссылка на изображение
                'created_at': datetime.now()
            }
        ]
        admins.insert_many(admin_data)
        print("Добавлены тестовые администраторы")

    # 2. Добавляем операторов (если их нет)
    if operators.count_documents({}) == 0:
        operator_data = [
            {
                'login': 'ivanov',
                'password': hash_password('operator1'),
                'full_name': 'Иванов Иван Иванович',
                'created_at': datetime.now()
            },
            {
                'login': 'petrov',
                'password': hash_password('operator2'),
                'full_name': 'Петров Петр Петрович',
                'created_at': datetime.now()
            },
            {
                'login': 'sidorova',
                'password': hash_password('operator3'),
                'full_name': 'Сидорова Анна Михайловна',
                'created_at': datetime.now()
            }
        ]
        operators.insert_many(operator_data)
        print("Добавлены тестовые операторы")

    # 3. Добавляем миссии (если их нет)
    if missions.count_documents({}) == 0:
        # Получаем ID операторов
        ops = list(operators.find({}, {'_id': 1}))

        if ops:
            mission_data = [
                {
                    'operator_id': ops[0]['_id'],
                    'drone_model': 'DJI Mavic 3',
                    'drone_count': 2,
                    'status': 'В процессе',
                    'description': 'Мониторинг строительной площадки',
                    'photo_url': '',  # Пустая ссылка на изображение
                    'start_time': datetime(2023, 6, 15, 9, 0),
                    'created_at': datetime.now()
                },
                {
                    'operator_id': ops[1]['_id'],
                    'drone_model': 'Autel EVO II',
                    'drone_count': 1,
                    'status': 'Завершена',
                    'description': 'Аэрофотосъемка парковой зоны',
                    'photo_url': '',  # Пустая ссылка на изображение
                    'start_time': datetime(2023, 6, 10, 14, 30),
                    'end_time': datetime(2023, 6, 10, 16, 45),
                    'created_at': datetime.now()
                },
                {
                    'operator_id': ops[2]['_id'],
                    'drone_model': 'DJI Phantom 4',
                    'drone_count': 1,
                    'status': 'Планируется',
                    'description': 'Инспекция ЛЭП',
                    'photo_url': '',  # Пустая ссылка на изображение
                    'planned_time': datetime(2023, 6, 20, 11, 0),
                    'created_at': datetime.now()
                }
            ]
            missions.insert_many(mission_data)
            print("Добавлены тестовые миссии")

    client.close()
    print("Инициализация базы данных завершена")


if __name__ == "__main__":
    initialize_database()