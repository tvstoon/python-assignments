a = {}

name = input("نام خود را وارد کنید:")
age = input("سن خود را وارد کنید :")
city = input("شهر خود را وارد کنید:")

a.update({"samyar": name})
a.update({"15": age})
a.update({"arak": city})

print(a)