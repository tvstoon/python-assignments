from PySide6.QtWidgets import QPushButton, QApplication, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout


# app = QApplication()

# button_1 = QPushButton("home")
# button_2 = QPushButton("contact")
# button_3 = QPushButton("about")
# button_4 = QPushButton("exit")
# button_5 = QPushButton("log in")


# v_box = QVBoxLayout()
# h_box = QHBoxLayout()

# wgt = QWidget()

# v_box.addWidget(button_1)
# v_box.addWidget(button_2)
# v_box.addWidget(button_3)

# h_box.addWidget(button_4)
# h_box.addWidget(button_5)

# v_box.addLayout(h_box)
# wgt.setLayout(v_box)

# wgt.show()
# app.exec()


# for loop with Qt
# b = [1, 28, 37, 14, 5, 6, 12, 23, 12, 234, 34]
# for d in b:
#     if d > 10:
#         print(d)


# from PySide6.QtWidgets import QApplication, QGridLayout, QPushButton, QWidget

# c = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 12, 23, 34, 45, 56, 67, 78, 89]

# app = QApplication([])
# wgt = QWidget()
# layout = QGridLayout(wgt)

# for index, number in enumerate(c):
#     row, column = divmod(index, 3)
#     layout.addWidget(QPushButton(str(number)), row, column)

# wgt.show()
# app.exec()


from PySide6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget
a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
app = QApplication()
wdg = QWidget()
vl = QVBoxLayout()

for b in a:
    button = QPushButton(str(b))

    vl.addWidget(button)
wdg.setLayout(vl)
wdg.show()
app.exec()
