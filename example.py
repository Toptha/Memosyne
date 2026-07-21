import sys
from PyQt6.QtWidgets import *

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("calc")
window.resize(400,300)
label = QLabel("Enter Number",window)
label.resize(100,20)
text = QLineEdit(window)
text.resize(200,20)
text.move(120,0)
plusbutton = QPushButton("+",window)
plusbutton.resize(20,20)
plusbutton.move(120,40)
minusbutton = QPushButton("-",window)
minusbutton.resize(20,20)
minusbutton.move(140,40)
multiplybutton = QPushButton("*",window)
multiplybutton.resize(20,20)
multiplybutton.move(160,40)
dividebutton = QPushButton("/",window)
dividebutton.resize(20,20)
dividebutton.move(180,40)

var1=0
var2=0
operation=''

def plus():
    var1 = int(text.text())
    operation = '+'
    text.clear()
    return var1,operation
def minus():
    var1 = int(text.text())
    operation = '-'
    text.clear()
    return var1,operation
def multiply():
    var1 = int(text.text())
    operation = '*'
    text.clear()
    return var1,operation
def divide():
    var1 = int(text.text())
    operation = '/'
    text.clear()
    return var1,operation

calculate = QPushButton("calculate",window)
calculate.resize(100,20)
calculate.move(150,90)
label2=QLabel(window)
label2.resize(100,20)
label2.move(120,80)
label2.hide()
def display():
    var2 = int(text.text())
    if operation == '+':
        label2.setText(str(int(var1) + int(var2)))
    elif operation == '-':
        label2.setText(str(int(var1) - int(var2)))
    elif operation == '*':
        label2.setText(str(int(var1) * int(var2)))
    elif operation == '/':
        label2.setText(str(int(var1) / int(var2)))
    label2.show()
calculate.clicked.connect(display)
plusbutton.clicked.connect(plus)
minusbutton.clicked.connect(minus)
multiplybutton.clicked.connect(multiply)
dividebutton.clicked.connect(divide)
window.show()
sys.exit(app.exec())


# import requests
# import requests

# url = "https://jsonplaceholder.typicode.com/users"
# response = requests.get(url)
# print(response.status_code)
# print(response.json())

# data = {
#     "id": 3,
#     "name":"pree"
# }

# response = requests.post(url,json=data)
# print(response.status_code)
# print(response.json())

# response = requests.put(url,json=data)
# print(response.status_code)
# print(response.json())

# response = requests.delete(url)
# print(response.status_code)
# print(response.json())

