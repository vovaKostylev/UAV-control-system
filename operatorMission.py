import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QTableView, QPushButton,
                             QStyledItemDelegate, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
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


class MissionDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Загрузка UI
        from PyQt5.uic import loadUi
        loadUi('ui/oper.ui', self)  # Замените 'your_ui_file.ui' на путь к вашему файлу

        # Настройка таблицы
        self.setup_table()
        self.add_test_missions()

        # Подключение кнопок
        self.run_mission.clicked.connect(self.add_new_mission)
        self.back.clicked.connect(self.close)

    def setup_table(self):
        # Заголовки столбцов
        headers = ["Оператор БПЛА", "Модель БПЛА", "Число БПЛА", "Статус миссии", "Действие"]

        # Начальные данные (можно оставить пустым)
        data = []

        # Создаем модель
        self.model = MissionsTableModel(data, headers)
        self.missions.setModel(self.model)

        # Настройка внешнего вида таблицы
        self.missions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.missions.verticalHeader().setVisible(False)
        self.missions.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.missions.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Устанавливаем делегат для кнопки в последнем столбце
        self.missions.setItemDelegateForColumn(4, ButtonDelegate(self.missions))

    def add_new_mission(self):
        # Пример добавления новой миссии
        operator = "Оператор 1"
        model = "Модель X"
        count = 3
        status = "Выполнение"

        self.model.add_mission(operator, model, count, status)

    def add_test_missions(self):
        # Тестовые данные
        test_missions = [
            ["Иванов И.И.", "DJI Mavic 3", 2, "В процессе"],
            ["Петров П.П.", "DJI Phantom 4", 1, "Завершена"],
            ["Сидоров С.С.", "Autel EVO II", 3, "Планируется"],
            ["Кузнецов К.К.", "Parrot Anafi", 1, "Отменена"]
        ]

        # Добавляем тестовые миссии в таблицу
        for mission in test_missions:
            self.model.add_mission(*mission)


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
        # Получаем данные строки
        model = index.model()
        row = index.row()

        operator = model.data(model.index(row, 0))
        drone_model = model.data(model.index(row, 1))
        count = model.data(model.index(row, 2))
        status = model.data(model.index(row, 3))

        print(f"Просмотр миссии: {operator}, {drone_model}, {count} БПЛА, статус: {status}")
        # Здесь можно открыть диалог с подробной информацией о миссии


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = MissionDialog()
    dialog.show()
    sys.exit(app.exec_())