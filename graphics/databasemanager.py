from pymongo import MongoClient
from bson.objectid import ObjectId
from ursina import  *
from datetime import  *
from bson import ObjectId, Binary
from datetime import datetime
from PIL import ImageGrab
class DatabaseManager:
    def __init__(self, db_name='drone_system', collection_name='missions', mongo_url='mongodb://localhost:27017/'):
        self.client = MongoClient(mongo_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_init_data(self, id_file='mission_id.txt'):
        try:
            # Читаем _id из файла
            with open(id_file, 'r') as file:
                mission_id = file.read().strip()

            # Преобразуем в ObjectId и ищем миссию
            mission = self.collection.find_one({"_id": ObjectId(mission_id)})

            if not mission:
                print("❌ Миссия не найдена.")
                return None

            num_drones = mission.get('num_drones')
            print(f"✅ Найдено: {num_drones} БПЛА для миссии {mission_id}")
            return num_drones

        except Exception as e:
            print(f"⚠️ Ошибка при получении данных из БД: {e}")
            return None

    def complete_mission(self, id_file: str = 'mission_id.txt'):
        try:
            # Получаем ID миссии из файла
            with open(id_file, 'r') as file:
                mission_id = file.read().strip()

            _id = ObjectId(mission_id)

            file = self.take_screenshot(mission_id = _id)

            # Ищем последнюю подходящую картинку по шаблону
            screenshot_dir = 'screenshots'
            files = sorted(
                [f for f in os.listdir(screenshot_dir) if f.startswith(f'mission_{mission_id}') and f.endswith('.png')],
                reverse=True
            )

            if not files:
                print("❌ Скриншот для миссии не найден.")
                return

            latest_image_path = os.path.join(screenshot_dir, files[0])

            # Чтение изображения как бинарного объекта
            with open(latest_image_path, 'rb') as img_file:
                img_binary = Binary(img_file.read())

            # Обновление документа
            result = self.collection.update_one(
                {"_id": _id},
                {
                    "$set": {
                        "status": "завершена",
                        "img_data": img_binary,
                        "completed_at": datetime.utcnow()
                    }
                }
            )

            if result.modified_count > 0:
                print(f"✅ Миссия {_id} успешно завершена и изображение сохранено в БД.")
            else:
                print(f"⚠️ Миссия {_id} не найдена или уже обновлена.")

        except Exception as e:
            print(f"❌ Ошибка при завершении миссии: {e}")

    def take_screenshot(self, mission_id):
        os.makedirs('screenshots', exist_ok=True)  # создаём папку, если её нет
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"screenshots/mission_{mission_id}_{timestamp}.png"
        ImageGrab.grab().save(filename)




        return filename