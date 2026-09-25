import math
def ooo(a , b):

    eee = math.pow(a , b)
    return eee

lll = ooo(15 , 25)
lll = ooo(2 , 3)
print(lll)
import random

ooo = range(100)
e = []
for a in ooo :
    c = random.randint(0 , 100)
    e.append(c)

print(e)






# from random import randint
# from math import pow
# b = pow(2, 4)
# print(b)
# a = randint(1 , 1000)
# print(a)




from PySide6.QtWidgets import QApplication , QPushButton

app = QApplication()

button = QPushButton('click kon')

button.show()
app.exec()