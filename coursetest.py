import sys
import subprocess
from PyQt5.QtCore import QMutex, Qt
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMessageBox, QVBoxLayout, QLabel, QFormLayout
from PyQt5.QtGui import QPixmap
import os
from pymongo import MongoClient
from bson import ObjectId
import bcrypt


import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QTableView, QPushButton,
                             QStyledItemDelegate, QHeaderView, QAbstractItemView,
                             QMessageBox, QInputDialog, QLineEdit, QFormLayout,
                             QDialogButtonBox, QVBoxLayout, QLabel, QSpinBox)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant

from datetime import datetime
from pymongo.errors import DuplicateKeyError
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtWidgets import QStyledItemDelegate, QPushButton, QHeaderView, QAbstractItemView, QMessageBox
# Инициализация MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['drone_control_system']


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("ui/welcomescreen.ui", self)
        self.login_UAV.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)
        self.toplayout.addWidget(self.login_admin, alignment=QtCore.Qt.AlignCenter)
        self.toplayout.addWidget(self.login_UAV, alignment=QtCore.Qt.AlignCenter)
        self.botlayout.addWidget(self.exit, alignment=QtCore.Qt.AlignCenter)
        self.botlayout.addWidget(self.create, alignment=QtCore.Qt.AlignCenter)
        self.exit.clicked.connect(self.gotoexit)
        self.login_admin.clicked.connect(self.gotologinadm)
        self.testLayout.addWidget(self.test, alignment=QtCore.Qt.AlignCenter)
        self.test.clicked.connect(self.gototest)

    def gototest(self):
        subprocess.Popen(
            [sys.executable, "main.py"],
            cwd="C:/Users/MSI/PycharmProjects/PPS/SwarmDrone/graphics"
        )

    def gotologin(self):
        login = LoginScreen(main_win=self)
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotocreate(self):
        create = CreateAccScreen(main_win=self)
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoexit(self):
        client.close()
        os._exit(0)

    def gotologinadm(self):
        login = LoginScreen(mode="admin", main_win=self)
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class LoginScreen(QDialog):
    def __init__(self, main_win: QDialog, mode="operator"):
        super(LoginScreen, self).__init__()
        self.mode = mode
        self.main = main_win
        loadUi("ui/login.ui", self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
        self.back.clicked.connect(self.goback)

    def goback(self):
        self.close()
        self.main.show()

    def loginfunction(self):
        user = self.loginfield.text()
        password = self.passwordfield.text()

        if len(user) == 0 or len(password) == 0:
            self.error.setText("Please input all fields.")
            return

        try:
            if self.mode == 'operator':
                collection = db.operators
            else:
                collection = db.admins

            user_data = collection.find_one({'login': user})

            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password']):
                if self.mode == 'operator':
                    oper = OperScreen(operator_id= user_data['_id'], main_win= self.main)
                    widget.addWidget(oper)
                else:
                    admin = AdminScreen(admin_id= user_data['_id'], main_win= self.main)
                    widget.addWidget(admin)
                widget.setCurrentIndex(widget.currentIndex() + 1)
            else:
                self.error.setText("Invalid username or password")

        except Exception as e:
            self.error.setText(f"Error: {str(e)}")


class CreateAccScreen(QDialog):
    def __init__(self, main_win: QDialog):
        super(CreateAccScreen, self).__init__()
        loadUi("ui/createacc.ui", self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)
        self.main_win = main_win

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def signupfunction(self):
        user = self.loginfield.text()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()
        type_acc = str(self.type.currentText())

        if len(user) == 0 or len(password) == 0 or len(confirmpassword) == 0:
            self.error.setText("Пожалуйста, заполните все поля")
            return

        if password != confirmpassword:
            self.error.setText("Пароли не совпадают")
            return

        try:
            if type_acc == "Оператор":
                collection = db.operators
                user_data = {
                    'login': user,
                    'password': self.hash_password(password),
                    'full_name': "",
                    'avatar_url': "",
                    'created_at': datetime.now()
                }
            else:
                collection = db.admins
                user_data = {
                    'login': user,
                    'password': self.hash_password(password),
                    'full_name': "",
                    'avatar_url': "",
                    'created_at': datetime.now()
                }

            collection.insert_one(user_data)
            QMessageBox.information(self, "Успех", "Аккаунт успешно создан!")
            self.close()
            self.main_win.show()

        except DuplicateKeyError:
            self.error.setText("Этот логин уже используется")
        except Exception as e:
            self.error.setText(f"Ошибка: {str(e)}")


class OperScreen(QDialog):
    def __init__(self, operator_id, main_win: QDialog):
        super(OperScreen, self).__init__()
        loadUi("ui/oper.ui", self)
        self.operator_id = operator_id
        self.main = main_win
        # Настройка интерфейса
        self.top.addWidget(self.missions, alignment=QtCore.Qt.AlignCenter)
        self.bot.addWidget(self.back, alignment=QtCore.Qt.AlignCenter)
        self.bot.addWidget(self.run_mission, alignment=QtCore.Qt.AlignCenter)

        # Инициализация таблицы миссий
        self.setup_missions_table()

        # Загрузка миссий оператора
        self.load_operator_missions()

        # Подключение кнопок
        self.run_mission.clicked.connect(self.execute_mission)
        self.back.clicked.connect(self.goback)
    def goback(self):
        self.close()
        self.main.show()
    def setup_missions_table(self):
        """Настройка таблицы миссий"""
        headers = ["ФИО","Модель БПЛА", "Число БПЛА", "Статус миссии", "Действие"]
        self.missions_model = MissionsTableModel([], headers)
        self.missions.setModel(self.missions_model)

        # Настройка внешнего вида
        self.missions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.missions.verticalHeader().setVisible(False)
        self.missions.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.missions.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Делегат для кнопки "Просмотреть"
        self.missions.setItemDelegateForColumn(4, ButtonDelegate(self.missions))

    def load_operator_missions(self):
        """Загрузка миссий текущего оператора из базы данных"""
        try:
            # Получаем данные оператора
            operator = db.operators.find_one({'_id': ObjectId(self.operator_id)})
            if not operator:
                QMessageBox.warning(self, "Ошибка", "Оператор не найден")
                return

            # Получаем миссии оператора
            missions = list(db.missions.find({'operator_id': ObjectId(self.operator_id)}))

            # Добавляем миссии в таблицу
            for mission in missions:
                self.missions_model.add_mission(
                    operator['full_name'],
                    mission['drone_model'],
                    mission['drone_count'],
                    mission['status']
                )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить миссии: {str(e)}")

    def execute_mission(self):

        subprocess.Popen(
            [sys.executable, "main.py"],
            cwd="C:/Users/MSI/PycharmProjects/PPS/SwarmDrone/graphics"
        )


    def get_mission(self,  folder='graphics', filename='mission_id.txt'):
        mission = db.missions.find_one({'status': 'В процессе'})
        if mission:
            folderf = os.path.join(os.getcwd(), 'graphics')
            os.makedirs(os.getcwd(), exist_ok=True)
            filepath = os.path.join(folderf, filename)
            with open(filepath, 'w') as file:
                file.write(str(mission['_id']))
            print(f"✅ Миссия {mission['_id']} сохранена в {filepath}")
            return mission
        else:
            print("❌ Нет миссий со статусом 'в процессе'")
            return None

class MissionsTableModel(QAbstractTableModel):
    def __init__(self, data, headers, parent=None):
        super(MissionsTableModel, self).__init__(parent)
        self._data = data
        self._headers = headers

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        elif role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return QVariant()

    def add_mission(self, operator, model, count, status):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._data.append([operator, model, count, status, "Просмотреть"])
        self.endInsertRows()


class ButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            button = QPushButton(self.parent())
            button.setText("Просмотреть")
            button.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    background-color: rgb(200, 200, 200);
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: rgb(180, 180, 180);
                }
            """)
            button.clicked.connect(lambda: self.button_clicked(index))
            self.parent().setIndexWidget(index, button)

    def button_clicked(self, index):
        model = index.model()
        row = index.row()

        operator = model.data(model.index(row, 0))
        drone_model = model.data(model.index(row, 1))
        count = model.data(model.index(row, 2))
        status = model.data(model.index(row, 3))

        # Создаем диалог с подробной информацией
        detail_dialog = QDialog()
        detail_dialog.setWindowTitle("Детали миссии")
        layout = QVBoxLayout()

        info = QLabel(
            f"<b>Оператор:</b> {operator}<br>"
            f"<b>Модель БПЛА:</b> {drone_model}<br>"
            f"<b>Количество:</b> {count}<br>"
            f"<b>Статус:</b> {status}"
        )

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(detail_dialog.close)

        layout.addWidget(info)
        layout.addWidget(close_btn)
        detail_dialog.setLayout(layout)
        detail_dialog.exec_()

class AddMissionDialog(QDialog):
    def __init__(self, admin_id,  parent=None) :
        super().__init__(parent)
        self.setWindowTitle("Добавить новую миссию")
        self.setFixedSize(400, 300)
        self.admin_id = admin_id

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.operator_edit = QLineEdit()
        self.model_edit = QLineEdit()
        self.count_edit = QSpinBox()
        self.count_edit.setMinimum(1)
        self.count_edit.setMaximum(15)
        self.status_edit = QLineEdit()
        self.status_edit.setText("В процессе")
        self.status_edit.setReadOnly(True)

        form_layout.addRow("Оператор БПЛА:", self.operator_edit)
        form_layout.addRow("Модель БПЛА:", self.model_edit)
        form_layout.addRow("Количество БПЛА:", self.count_edit)
        form_layout.addRow("Статус миссии:", self.status_edit)


       # admin = db.operators.find_one({'login': self.operator_edit.text()})





        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_mission_data(self):
            """Возвращает данные миссии после успешного сохранения"""
            return {
                'operator': self.operator_edit.text(),
                'model': self.model_edit.text(),
                'count': self.count_edit.value(),
                'status': self.status_edit.text()
            }
class AdminScreen(QDialog):
    def __init__(self, main_win: QDialog, admin_id):
        super(AdminScreen, self).__init__()
        self.admin_id = admin_id  # Инициализируем сначала admin_id
        loadUi("ui/admin.ui", self)
        self.setup_ui()

        # Настройка таблицы миссий
        self.setup_missions_table()
        self.main = main_win
        # Загрузка данных
        self.load_all_missions()

        # Подключение сигналов
        self.connect_signals()

    def goback(self):
        self.close()
        self.main.show()
    def setup_ui(self):
        """Настройка элементов интерфейса"""
        self.bot.addWidget(self.back, alignment=QtCore.Qt.AlignCenter)
        self.bot.addWidget(self.add, alignment=QtCore.Qt.AlignCenter)

    def setup_missions_table(self):
        """Настройка таблицы миссий"""
        headers = ["Оператор БПЛА", "Модель БПЛА", "Число БПЛА", "Статус миссии", "Действие"]
        self.missions_model = MissionsTableModel([], headers)
        self.missions.setModel(self.missions_model)

        # Настройка внешнего вида
        self.missions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.missions.verticalHeader().setVisible(False)
        self.missions.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.missions.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Делегат для кнопки "Просмотреть"
        self.missions.setItemDelegateForColumn(4, ButtonDelegate(self.missions))

    def connect_signals(self):
        """Подключение сигналов кнопок"""
        self.add.clicked.connect(self.show_add_mission_dialog)
        self.back.clicked.connect(self.goback)

    def load_all_missions(self):
        """Загрузка всех миссий из базы данных"""
        try:
            # Очищаем текущие данные
            self.missions_model = MissionsTableModel([], self.missions_model._headers)
            self.missions.setModel(self.missions_model)

            # Получаем все миссии с информацией об операторах
            pipeline = [
                {
                    '$lookup': {
                        'from': 'operators',
                        'localField': 'operator_id',
                        'foreignField': '_id',
                        'as': 'operator'
                    }
                },
                {'$unwind': '$operator'},
                {'$sort': {'created_at': -1}}
            ]

            missions = list(db.missions.aggregate(pipeline))

            # Добавляем миссии в таблицу
            for mission in missions:
                self.missions_model.add_mission(
                    mission['operator']['full_name'],
                    mission['drone_model'],
                    mission['drone_count'],
                    mission['status']
                )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить миссии: {str(e)}")

    def show_add_mission_dialog(self):
        """Показ диалога добавления миссии"""
        dialog = AddMissionDialog(self.admin_id)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_mission_data()

            if not data["operator"] or not data["model"]:
                QMessageBox.warning(self, "Ошибка", "Поля 'Оператор' и 'Модель' обязательны!")
                return

            try:
                # Находим оператора по ФИО
                operator = db.operators.find_one({'login': data["operator"]})

                if not operator:
                    QMessageBox.warning(self, "Ошибка", "Оператор не найден!")
                    return
                # Создаем новую миссию
                user_data = {
                    'operator_id': operator['_id'],
                    'admin': self.admin_id,
                    'drone_model': data["model"],
                    'drone_count': data["count"],
                    'status': data["status"],
                    'created_at': datetime.now(),
                    'report': ''
                }

                db.missions.insert_one(user_data)

                # Сохраняем в базу


                # Добавляем в таблицу
                self.missions_model.add_mission(
                    data["operator"],
                    data["model"],
                    data["count"],
                    data["status"]
                )

                QMessageBox.information(self, "Успех", "Миссия успешно добавлена!")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")


    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        client.close()
        event.accept()


# main
app = QApplication(sys.argv)
welcome = WelcomeScreen()

widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()

try:
    sys.exit(app.exec_())
except Exception as e:
    print(f"Exiting: {str(e)}")
finally:
    client.close()
