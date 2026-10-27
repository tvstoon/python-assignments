# from PySide6.QtWidgets import (QApplication, QWidget, QLineEdit, QLabel, QPushButton, QLayout, QHBoxLayout, QVBoxLayout)

# app = QApplication()

# widget = QWidget()

# label_1 = QLabel("username")
# label_2 = QLabel("password")
# label_3 = QLabel("age")

# lineedit_1 = QLineEdit()
# lineedit_2 = QLineEdit()
# lineedit_3 = QLineEdit()

# pushbutton_1 = QPushButton("cancel")
# pushbutton_2 = QPushButton("create")

# layout_box_username = QHBoxLayout()
# layout_box_password = QHBoxLayout()
# layout_box_age = QHBoxLayout()
# layout_box_button = QHBoxLayout()

# main_layout = QVBoxLayout()

# layout_box_username.addWidget(label_1)
# layout_box_username.addWidget(lineedit_1)

# layout_box_password.addWidget(label_2)
# layout_box_password.addWidget(lineedit_2)

# layout_box_age.addWidget(label_3)
# layout_box_age.addWidget(lineedit_3)

# layout_box_button.addWidget(pushbutton_1)
# layout_box_button.addWidget(pushbutton_2)

# main_layout.addLayout(layout_box_username)
# main_layout.addLayout(layout_box_password)
# main_layout.addLayout(layout_box_age)
# main_layout.addLayout(layout_box_button)

# widget.setLayout(main_layout)
# widget.show()

# app.exec()

from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QCheckBox, QWidget, QRadioButton, QTextEdit


app = QApplication()
wgt = QWidget()

checkbox = QCheckBox("active")
radio_1 = QRadioButton("پذیرش قوانین")
radio_2 = QRadioButton("خرید")
radio_3 = QRadioButton("لغو")
text_edit = QTextEdit()
v_box = QVBoxLayout()

v_box.addWidget(checkbox)
v_box.addWidget(radio_1)
v_box.addWidget(radio_2)
v_box.addWidget(radio_3)
v_box.addWidget(text_edit)
wgt.setLayout(v_box)
wgt.show()
app.exec()
