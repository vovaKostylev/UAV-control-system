import sys
import subprocess
from PyQt5.QtCore import QMutex
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5.QtGui import QPixmap
import os
import sqlite3
from operatorMission import  *
from adminMisssions import  *

class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("ui/welcomescreen.ui",self)
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
        login = LoginScreen(main_win= self)
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

        
        

    def gotocreate(self):
        create = CreateAccScreen(main_win= self)
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoexit(self):
        os._exit(0)



    def gotologinadm(self):
        login = LoginScreen(mode = "admin",main_win = self)
        
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

class LoginScreen(QDialog):
    def __init__(self,main_win: QDialog,mode="operator" ):
        super(LoginScreen, self).__init__()
        self.mode = mode 
        self.main = main_win
        loadUi("ui/login.ui",self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
        self.back.clicked.connect(self.goback)
        
    def goback(self):
        self.close()
        self.main.show()

    def loginfunction(self):
        user = self.loginfield.text()
        password = self.passwordfield.text()

        if len(user)==0 or len(password)==0:
            self.error.setText("Please input all fields.")

        else:
            conn = sqlite3.connect("login.db")
            cur = conn.cursor()
            query = 'SELECT password FROM users WHERE login =\''+user+"\'"
            result_pass = cur.execute(query).fetchone()[0]
            if result_pass == str(password):
                if(self.mode== 'operator'):
                    oper = OperScreen()
                    widget.addWidget(oper)
                    widget.setCurrentIndex(widget.currentIndex() + 1)
                else:
                    admin = AdminScreen()
                    widget.addWidget(admin)
                    widget.setCurrentIndex(widget.currentIndex() + 1)

                print("suceesfull")
            else:
                self.error.setText("Invalid username or password")

class CreateAccScreen(QDialog):
    def __init__(self, main_win: QDialog):
        super(CreateAccScreen, self).__init__()
        loadUi("ui/createacc.ui",self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)
        self.main_win = main_win



    def signupfunction(self):
        user = self.loginfield.text()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()
        type_acc = str(self.type.currentText())

        if len(user)==0 or len(password)==0 or len(confirmpassword)==0:
            self.error.setText("Пожалуйста, заполните все поля")

        elif password!=confirmpassword:
            self.error.setText("Пароли не совпадают")
        else:


            try:
                conn = sqlite3.connect("login.db")
                cur = conn.cursor()

                user_info = [user, password, type_acc]
                cur.execute('INSERT INTO users (login, password, type) VALUES (?,?,?)', user_info)
                conn.commit()

            except Exception as e:
                self.error.setText("Этот логин уже используется ")
            finally:
                conn.close()
                self.close()
                self.main_win.show()

class OperScreen(QDialog):
    def __init__(self):
        super(OperScreen, self).__init__()
        loadUi("ui/oper.ui",self)
        self.top.addWidget(self.missions, alignment=QtCore.Qt.AlignCenter)
        self.bot.addWidget(self.back, alignment=QtCore.Qt.AlignCenter)
        self.bot.addWidget(self.run_mission, alignment=QtCore.Qt.AlignCenter)


class AdminScreen(QDialog):
    def __init__(self):
        super(AdminScreen, self).__init__()
        loadUi("ui/admin.ui",self)
        self.bot.addWidget(self.back, alignment=QtCore.Qt.AlignCenter)
        self.bot.addWidget(self.add, alignment=QtCore.Qt.AlignCenter)


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
except:
    print("Exiting")