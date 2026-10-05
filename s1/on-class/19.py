from PySide6.QtWidgets import QApplication, QPushButton, QLabel, QWidget, QHBoxLayout, QLineEdit


app = QApplication()

window = QWidget()

button = QPushButton("کلیک کن")
label = QLabel("نا کاربری  : ")

lineedit = QLineEdit()

box = QHBoxLayout()

box.addWidget(label)
box.addWidget(lineedit)
box.addWidget(button)

window.setLayout(box)

window.show()
app.exec()

# from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QComboBox

# app = QApplication()


# window = QWidget()

# combo = QComboBox()
# combo.addItems(["female", "male"])

# layout = QHBoxLayout()

# layout.addWidget(combo)

# window.setLayout(layout)

# window.show()
# app.exec()


# from PySide6.QtWidgets import QApplication, QComboBox, QWidget, QHBoxLayout, QLabel


# app = QApplication()


# combo = QComboBox()
# combo.addItems(["male", "female"])
# window = QWidget()

# label = QLabel("gender")

# box = QHBoxLayout()

# box.addWidget(label)
# box.addWidget(combo)

# window.setLayout(box)

# window.show()

# app.exec()


# from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
# app = QApplication()

# window = QWidget()

# label_hello = QLabel("hello")
# label_samyar = QLabel("samyar")

# label_shop = QLabel("Shop")
# label_clothes = QLabel("Clothes")

# box_1 = QVBoxLayout()
# box_2 = QVBoxLayout()

# box_3 = QHBoxLayout()

# box_1.addWidget(label_hello)
# box_1.addWidget(label_samyar)

# box_2.addWidget(label_shop)
# box_2.addWidget(label_clothes)

# box_3.addLayout(box_1)
# box_3.addLayout(box_2)

# window.setLayout(box_3)

# window.show()
# app.exec()


# from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
# app = QApplication()

# window = QWidget()

# label_hello = QLabel("hello")
# label_samyar = QLabel("samyar")

# label_shop = QLabel("Shop")
# label_clothes = QLabel("Clothes")

# box_1 = QVBoxLayout()
# box_2 = QVBoxLayout()

# box_1.addWidget(label_hello)
# box_1.addWidget(label_samyar)

# box_2.addWidget(label_shop)
# box_2.addWidget(label_clothes)


# box_3 = QHBoxLayout()


# box_3.addLayout(box_1)
# box_3.addLayout(box_2)

# window.setLayout(box_3)

# window.show()
# app.exec()
