from PySide6.QtWidgets import QApplication , QPushButton , QVBoxLayout , QHBoxLayout , QWidget , QLineEdit , QLabel  , QComboBox


app = QApplication()

button = QPushButton("pushbutton")

lineedit = QLineEdit()

wdg = QWidget()

label = QLabel("name")

combo = QComboBox()

combo.addItems(["labaniat" , "hobobat" , "gooshti"])

vb = QVBoxLayout()

hb = QHBoxLayout()


hb.addWidget(label)
hb.addWidget(lineedit)

vb.addLayout(hb)
vb.addWidget(button)
vb.addWidget(combo)


wdg.setLayout(vb)

wdg.show()

app.exec()


# # a = {"name" : "ali" , "age" : "12" , "country" : "iran" }

# # print(a["age"])



# # a = {"name" :"javad" , "age" :"14" , "country" :"iran"}


# # a.update({"city" : "arak"})

# # print(a)


# a = {"قد" :"170" , "وزن" : "50" , "سن" : "16"}

# b = a["وزن"]

# c = a["سن"]

# a.update({"کشور" : "ایران"} )

# print(a , b , c)