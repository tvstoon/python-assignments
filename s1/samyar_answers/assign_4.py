
# # -----------------------------------------
# # 1
# health = 40
# check_number = 50
# my_health = health
# if my_health < check_number:
#     print("Health is low")
# else:
#     print("Health is good")

# # 2
# player_level = 12
# min_level = 10
# my_level = player_level
# if my_level >= min_level:
#     print("You can enter")
# else:
#     print("Level is low")

# # 3
# line_offside = 17
# enemy_position = 10
# if enemy_position > line_offside:
#     print("Offside")
# else:
#     print("Not Offside")

# # 4
# finish_point = 40
# player_position = 45
# my_position = player_position
# if my_position > finish_point:
#     print("Player won")
# else:
#     print("Player did not win")

# # 5
# name = "Amir"
# level = 5
# color_of_skin = "Blue"
# print(type(name))
# print(type(level))
# print(type(color_of_skin))
# my_color = color_of_skin
# if my_color == "Blue":
#     print("That is enemy")
# else:
#     print("That is not enemy")

# # 6
# my_health = 60
# if my_health > 80:
#     print("Healthy")
# elif my_health > 50:
#     print("Need medicine")
# elif my_health > 10:
#     print("Critical")
# elif my_health == 0:
#     print("Dead")
# else:
#     print("Unknown status")

# # 7
# action = "Kick"
# health = 100
# if action == "Punch":
#     health = health - 10
#     print("Punched, health decreased")
#     print("Health now:", health)
# elif action == "Kick":
#     health = health - 25
#     print("Kicked, health decreased")
#     print("Health now:", health)
# elif action == "Gun":
#     health = 0
#     print("Shot by gun, died instantly!")
#     print("Health now:", health)
# else:
#     print("I don't know this action")

# # 8
# money = 100
# price_game = 10
# price_ai = 20
# price_gamepass = 25
# total_cost = price_game + price_ai + price_gamepass
# if total_cost <= money:
#     print("Money is enough, you can buy all")
# else:
#     print("Money is not enough")

# # 9
# my_height = 175
# my_age = 11
# if my_height > 170 and my_age > 15:
#     print("Can go to pool")
# else:
#     print("Cannot go to pool")

# # 10
# my_point = 25
# if my_point > 10 and my_point < 50:
#     print("Place is safe")
# elif my_point > 0 and my_point < 10:
#     print("Place is not safe")
# else:
#     print("Point is not in the ranges")


# # ---------------------
# # تمکرین 13:

# # age = 20
# # has_card = True

# # اگر سن سن فرد بیشتر از 19 باشد و همینطور کارت داشته باشد پرینت کنه ورود مجاز است
# age = 20
# has_card = False

# if age > 19 and has_card :
#     print ("ok")
# else:
#     print ("not ok")

# # ---------------------
# # تمکرین 14:
# # power = 50
# # item = "sword"
# # shield

# # اگر آیتم برابر با شمشیر بود بیاد به مقدار قدرتمون 30 تا اضافه کنه و بعدش پرینت کنه  ⚔️ شمشیر گرفتی!
# # اگر آیتم برابر با سپر بود بیاد به مقدار قدرتمون 15 تا اضافه کنه و بعدش پرینت کنه  🛡️ سپر گرفتی!!
# # در غیر اینصورت 10 تا از قدرت کم کنه و پرینت کنه  💀 آیتم خراب بود!

# # بعد از بلاک کاندیشن پرینت کنه قدرت نهایییمون

# power = 50
# item = ""

# if item == "sword" :
#     power = power + 30
#     print("get sword")
# elif item == "shield":
#     power = power + 15
#     print("get shield")
# else:
#     power = power - 10
#     print("item is broken")
# print(power)
# #___________________________________________________________________________________________________________________________
# #تمرین جدید
# game_items = ['sword', 'bow', 'shield']

# power = 0

# if game_items[0] == 'sword':
#     power = power + 20
#     print("Sword is in hand")

# if game_items[1] == 'shield':
#     power = power + 10
#     print("Can protect")

# if game_items[2] == 'bow':
#     power = power + 15
#     print("Can attack from far")

# print("Power is:", power)


# numbers = [5, 23, 17, 30, 12]

# for i in numbers:
#     if i > 18:
#         print("You can enter")
#     else:
#         print("You can not enter")

# #2
# numbers = [5, 23, 17, 30, 12]

# for i in numbers:
#     if i > 18:
#         print("You can enter")
#     else:
#         print("You can not enter")

#         #3


#         numbers = [20, 18, 15, 9, 12]

# for i in numbers:

#     if i >= 18 and i <= 20:
#         print("Excellent")

#     elif i >= 15 and i < 18:
#         print("Medium")

#     elif i >= 10 and i < 15:
#         print("Not good")

#     else:
#         print("Fail")

#         #4
#         far_items = []

# game_items = [
#     'sword',
#     'bow',
#     'shield',
#     'axe',
#     'crossbow'
# ]

# if game_items[0] == 'bow' or game_items[0] == 'crossbow':
#     far_items.append(game_items[0])
# else:
#     pass

# if game_items[1] == 'bow' or game_items[1] == 'crossbow':
#     far_items.append(game_items[1])
# else:
#     pass

# if game_items[2] == 'bow' or game_items[2] == 'crossbow':
#     far_items.append(game_items[2])
# else:
#     pass

# if game_items[3] == 'bow' or game_items[3] == 'crossbow':
#     far_items.append(game_items[3])
# else:
#     pass

# if game_items[4] == 'bow' or game_items[4] == 'crossbow':
#     far_items.append(game_items[4])
# else:
#     pass

# print(far_items)
# #--------------------------------------------------------------------------
# #تکالیف جذیذ

# names = [
#     "علی", "سامیار", "محمد", "حسین", "مهدی",
#     "امیر", "سارا", "مریم", "نگار", "نرگس",
#     "زهرا", "فاطمه", "آرمان", "پارسا", "کیان",
#     "یاسین", "رها", "نازنین", "پریسا", "مهسا"
# ]

# # for name in names:
# #     print(name)


# #----------------------------------
# #2
# a = [1, 34, 7, 8, 34, 2, 1, 4, 345, 12, 234]

# for number in a:
#     print(number / 2)


# #__________________________________
# #3
# a = [1, 34, 7, 8, 34, 2, 1, 4, 345, 12, 234]

# for number in a:
#     if number > 10:
#         print(number)
#         #_________________________________________________________________________
# game_items = ['sword', 'bow', 'shield']

# power = 0

# for item in game_items:
#     if item == 'sword':
#         power = power + 20
#         print("Sword is in hand")

#     elif item == 'shield':
#         power = power + 10
#         print("Can protect")

#     elif item == 'bow':
#         power = power + 15
#         print("Can attack from far")

# print("Power:", power)
# #
# # _______________________________________________________
# numbers = [5, 27, 14, 19, 8]

# for num in numbers:
#     if num > 18:
#         print(num, "You can enter")
#     else:
#         print(num, "You cannot enter")
# #_________________________________________________________
# numbers = [20, 17, 15, 9, 12]

# for num in numbers:

#     if num >= 18 and num <= 20:
#         print(num, "Excellent")

#     elif num >= 15 and num < 18:
#         print(num, "Average")

#     elif num >= 10 and num < 15:
#         print(num, "Not good")

#     else:
#         print(num, "Fail")
# #________________________________________________________
# new_list = []

# game_items = [
#     'sword',
#     'bow',
#     'shield',
#     'axe',
#     'crossbow'
# ]


# for item in game_items:

#     if item == 'bow' or item == 'crossbow':
#         new_list.append(item)


# print(new_list)
# #______________________________________
# #1
# names = [
#     "علی", "رضا", "محمد", "حسین", "مهدی",
#     "امیر", "سارا", "مریم", "نگار", "نرگس",
#     "زهرا", "فاطمه", "آرمان", "پارسا", "کیان",
#     "یاسین", "رها", "نازنین", "پریسا", "مهسا"
# ]

# for name in names:
#     print(name)

#     #_______________________________________________

#     #2


# a = [1, 34, 7, 8, 34, 2, 1, 4, 345, 12, 234]

# for number in a:
#     print(number / 2)


#     #_________________________________________
#     #3

# a = [1, 34, 7, 8, 34, 2, 1, 4, 345, 12, 234]

# for number in a:
#     if number > 10:
#         print(number)

# #______________________________________________________________________________________________________________________________
# #تمرین اول
# name = input("enter your name: ")

# print(type(name))
# print(name)


# #تمرین دوم
# number = input("enter a number: ")

# print(type(number))

# if type(number) == str:
#     number = int(number)

# print(type(number))

# #تمرین سوم
# number = input("enter a number: ")

# number = int(number)

# if number > 10:
#     print("your number is more than 10")
# else:
#     print("your number is less than 10")
# #تمرین چهارم
# names = [
#     "علی", "محمد", "رضا", "حسین", "مهدی",
#     "امیر", "سینا", "آرمان", "سامان", "پویان",
#     "فاطمه", "زهرا", "مریم", "سارا", "نگار",
#     "نرگس", "الهام", "نازنین", "هانیه", "ریحانه",
#     "کیان", "پارسا", "بردیا", "یاسین", "شایان",
#     "ترانه", "مهسا", "رها", "نیلوفر", "بهار"
# ]

# for name in names:
#     print(name)

# #تمرین گنجم

# c = [12, 23, 454, 23, 12, 1, 23, 4, 45, 6, 7, 8, 45, 2, 12]

# new_list = []

# for number in c:
#     if number < 10:
#         new_list.append(number)

# print(new_list)

# #تمرین شیشم
def tamrin_3():
    my_number = 7

    number = input("enter a number: ")

    number = int(number)

    if number == my_number:
        print("your number is correct")
    else:
        print("your number is wrong")


tamrin_3()

# #_______________________________________________________________________________________________________________________
# #تکلیف جدید

# # یک متغیر داریم به اسم score
# # مقدار آن برابر 0 است
# #score = 0

# # یک متغیر دیگر داریم به اسم correct_number
# # یعنی عدد درست
# #correct_number = 10

# # از یوزر با input یک عدد بگیر
# # و آن را بررسی کن که عدد درست است یا نه

# # اگر عدد درست را وارد کرد:
# # یک امتیاز به score اضافه کن

# # در غیر این صورت:
# # یک امتیاز از score کم کن

# # در نهایت خارج از بلاک:
# # score را print کن


def tamrin_3():
    score = 0
    correct_number = 10

    number = int(input("Enter number: "))

    if number == correct_number:
        score = score + 1
    else:
        score = score - 1

    print(score)

# ________________________________________________________________________________________________________________________________________________
# تمرین جدید

# از یوزر سنش رو بگیر
# مجدد از یوزر اسمش هم بگیر
# و پرینت کن تایپاشون رو و همینطور خودشون رو
# سن رو بعدش تبدیل کن به int و مجدد پرینتش کن


def tamrin_4():
    age = input("Enter your age: ")
    name = input("Enter your name: ")

    print(age)
    print(type(age))

    print(name)
    print(type(name))

    age = int(age)

    print(age)
    print(type(age))


# #________________________________________________________________________
# #تمرین جدید
def tamrin_5():
    age = int(input("سن خود را وارد کنید: "))

    if age < 10:
        print(" javan hast")
    elif age <= 20:
        print("nojavan")
    else:
        print("pir")


# #_________________________________________________________________________________________________________________________________________
# #تمرین جدید
def tamrin_6():
    list_a = [1, 23, 3, 2, 12, 4, 5, 34, 1, 1, 5, 445, 56, 7, 64, 2, 3, 4]

    greater_than_10 = []
    less_than_10 = []

    for x in list_a:
        if x > 10:
            greater_than_10.append(x)

        if x < 10:
            less_than_10.append(x)

    print(greater_than_10)
    print(less_than_10)


# ۲
# از لیست زبر مقادیری که بزرگ تر از ۱۰ هست رو به یک لیست جدید اضافه کن
def tamrrin_7():
    a = [34, 2, 5, 34, 78, 6, 5, 13, 15, 19, 67, 5, 9]

    users_age = [12, 23, 43]
    users_name = ['maryam', 'morteza', 'mirza']

    name = input("اسم را وارد کنید: ")
    age = int(input("سن را وارد کنید: "))

    users_name.append(name)
    users_age.append(age)

    print(users_name)
    print(users_age)

# #________________________________________________________________________________________________________________________


def tamrin_8():
    a = [34, 2, 5, 34, 78, 6, 5, 13, 15, 19, 67, 5, 9]

    new_list = []

    for i in a:
        if i > 10:
            new_list.append(i)

    print(new_list)


def tamrin_9():
    a = [34, 2, 5, 34, 78, 6, 5, 13, 15, 19, 67, 5, 9]
    b = []
    for ooo in a:
        if ooo > 10:
            b.append(ooo)
    print(b)


def tamrin_10():
    a = None
    ooo = input("adad ra vard kon : ")
    ooo = int(ooo)
    if ooo < 10:
        a = "kodak"
    elif ooo > 10:
        a = "pir"
    print(a)


def tamrin_akhar():
    b = [12, 1, 2, 23, 3, 2, 1, 23, 4, 3, 2, 34, 32, 234, 234]

    ccc = int(input("meghdar 1 : "))

    ooo = int(input("meghdar 2 : "))

    fff = ooo + ccc

    if fff > 10:
        b.append(fff)

# ________________________________________________________________________________________________________________________________________


def jam_adad(a, b, c):
    jam = a + b + c
    print(jam)


jam_adad(2, 3, 4)
jam_adad(10, 5, 2)
jam_adad(1, 1, 8)

a = int(input("سنتو بده : "))
print(a)


def sen():
    a = int(input("سنتو بده : "))
    print(a)


sen()

# __________________________________________________________________________________________________________________________
# 1


def jam_adad(a, b, c):
    print(a + b + c)


jam_adad(2, 3, 4)
jam_adad(5, 5, 5)
jam_adad(10, 20, 30)


# 2
def sen():
    a = int(input("سنتو بده : "))
    print(a)


sen()


# 3
a = 100

x = int(input("عدد اول: "))
y = int(input("عدد دوم: "))
z = int(input("عدد سوم: "))

jam = x + y + z

if jam > a:
    print("ok")
else:
    print("no")


# 4
multiplied = [4, 6, 8, 7, 6]

x = int(input("یک عدد بده: "))
x = x * 2

multiplied.append(x)

print(multiplied)
