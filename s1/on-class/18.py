# from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QHBoxLayout, QLineEdit
# app = QApplication()

# widget = QWidget()
# button_1 = QPushButton("click")
# button_2 = QPushButton("Button 2")
# button_3 = QPushButton("button 3")
# label_1 = QLabel("user name : ")
# lineedit_1 = QLineEdit()
# button_1.move(10, 10)

# h_layout = QHBoxLayout()

# h_layout.addWidget(label_1)
# h_layout.addWidget(lineedit_1)
# h_layout.addWidget(button_1)
# h_layout.addWidget(button_2)
# h_layout.addWidget(button_3)

# widget.setLayout(h_layout)

# widget.show()
# app.exec()


from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QApplication, QHBoxLayoutc v

app = QApplication()
Widget = QWidget()
label = QLabel("user name : ")
lineEdit = QLineEdit()

layout = QHBoxLayout()

layout.addWidget(label)
layout.addWidget(lineEdit)
Widget.setLayout(layout)

Widget.show()
app.exec()
