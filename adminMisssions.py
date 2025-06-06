import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QTableView, QPushButton,
                             QStyledItemDelegate, QHeaderView, QAbstractItemView,
                             QMessageBox, QInputDialog, QLineEdit, QFormLayout,
                             QDialogButtonBox, QVBoxLayout, QLabel, QSpinBox)
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
        self._data.append([operator, model, str(count), status, "Просмотреть"])
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

        QMessageBox.information(self.parent(), "Информация о миссии",
                                f"Оператор: {operator}\n"
                                f"Модель БПЛА: {drone_model}\n"
                                f"Количество: {count}\n"
                                f"Статус: {status}")


class AddMissionDialog(QDialog):
    def __init__(self, parent=None):
        self.init__ = super().__init__(parent)
        self.setWindowTitle("Добавить новую миссию")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.operator_edit = QLineEdit()
        self.model_edit = QLineEdit()
        self.count_edit = QSpinBox()
        self.count_edit.setMinimum(1)
        self.count_edit.setMaximum(15)
        self.status_edit = QLineEdit()
        self.status_edit.setText("В процессе")

        form_layout.addRow("Оператор БПЛА:", self.operator_edit)
        form_layout.addRow("Модель БПЛА:", self.model_edit)
        form_layout.addRow("Количество БПЛА:", self.count_edit)
        form_layout.addRow("Статус миссии:", self.status_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_data(self):
        return {
            "operator": self.operator_edit.text(),
            "model": self.model_edit.text(),
            "count": self.count_edit.value(),
            "status": self.status_edit.text()
        }


class MissionDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Загрузка UI
        from PyQt5.uic import loadUi
        loadUi('ui/admin.ui', self)  # Замените 'your_ui_file.ui' на путь к вашему файлу

        # Настройка таблицы
        self.setup_table()

        # Добавляем тестовые записи
        self.add_test_missions()

        # Подключение кнопок
        self.add.clicked.connect(self.show_add_mission_dialog)
        self.back.clicked.connect(self.close)

    def setup_table(self):
        headers = ["Оператор БПЛА", "Модель БПЛА", "Число БПЛА", "Статус миссии", "Действие"]
        data = []

        self.model = MissionsTableModel(data, headers)
        self.missions.setModel(self.model)

        self.missions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.missions.verticalHeader().setVisible(False)
        self.missions.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.missions.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.missions.setItemDelegateForColumn(4, ButtonDelegate(self.missions))

    def add_test_missions(self):
        # Тестовые данные
        test_missions = [
            ["Иванов И.И.", "DJI Mavic 3", 2, "В процессе"],
            ["Петров П.П.", "DJI Phantom 4", 1, "Завершена"],
            ["Сидоров С.С.", "Autel EVO II", 3, "Планируется"]
        ]

        # Добавляем тестовые миссии в таблицу
        for mission in test_missions:
            self.model.add_mission(*mission)

    def show_add_mission_dialog(self):
        dialog = AddMissionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data["operator"] and data["model"]:
                self.model.add_mission(
                    data["operator"],
                    data["model"],
                    data["count"],
                    data["status"]
                )
            else:
                QMessageBox.warning(self, "Ошибка", "Поля 'Оператор' и 'Модель' обязательны для заполнения!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = MissionDialog()
    dialog.show()
    sys.exit(app.exec_())