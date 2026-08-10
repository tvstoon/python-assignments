
# -----------------------------------------
# 1
health = 40
check_number = 50
my_health = health
if my_health < check_number:
    print("Health is low")
else:
    print("Health is good")

# 2
player_level = 12
min_level = 10
my_level = player_level
if my_level >= min_level:
    print("You can enter")
else:
    print("Level is low")

# 3
line_offside = 17
enemy_position = 10
if enemy_position > line_offside:
    print("Offside")
else:
    print("Not Offside")

# 4
finish_point = 40
player_position = 45
my_position = player_position
if my_position > finish_point:
    print("Player won")
else:
    print("Player did not win")

# 5
name = "Amir"
level = 5
color_of_skin = "Blue"
print(type(name))
print(type(level))
print(type(color_of_skin))
my_color = color_of_skin
if my_color == "Blue":
    print("That is enemy")
else:
    print("That is not enemy")

# 6
my_health = 60
if my_health > 80:
    print("Healthy")
elif my_health > 50:
    print("Need medicine")
elif my_health > 10:
    print("Critical")
elif my_health == 0:
    print("Dead")
else:
    print("Unknown status")

# 7
action = "Kick"
health = 100
if action == "Punch":
    health = health - 10
    print("Punched, health decreased")
    print("Health now:", health)
elif action == "Kick":
    health = health - 25
    print("Kicked, health decreased")
    print("Health now:", health)
elif action == "Gun":
    health = 0
    print("Shot by gun, died instantly!")
    print("Health now:", health)
else:
    print("I don't know this action")

# 8
money = 100
price_game = 10
price_ai = 20
price_gamepass = 25
total_cost = price_game + price_ai + price_gamepass
if total_cost <= money:
    print("Money is enough, you can buy all")
else:
    print("Money is not enough")

# 9
my_height = 175
my_age = 11
if my_height > 170 and my_age > 15:
    print("Can go to pool")
else:
    print("Cannot go to pool")

# 10
my_point = 25
if my_point > 10 and my_point < 50:
    print("Place is safe")
elif my_point > 0 and my_point < 10:
    print("Place is not safe")
else:
    print("Point is not in the ranges")


# ---------------------
# تمکرین 13:

# age = 20
# has_card = True

# اگر سن سن فرد بیشتر از 19 باشد و همینطور کارت داشته باشد پرینت کنه ورود مجاز است
age = 20
has_card = False

if age > 19 and has_card :
    print ("ok")
else:
    print ("not ok")

# ---------------------
# تمکرین 14:
# power = 50
# item = "sword"
# shield

# اگر آیتم برابر با شمشیر بود بیاد به مقدار قدرتمون 30 تا اضافه کنه و بعدش پرینت کنه  ⚔️ شمشیر گرفتی!
# اگر آیتم برابر با سپر بود بیاد به مقدار قدرتمون 15 تا اضافه کنه و بعدش پرینت کنه  🛡️ سپر گرفتی!!
# در غیر اینصورت 10 تا از قدرت کم کنه و پرینت کنه  💀 آیتم خراب بود!

# بعد از بلاک کاندیشن پرینت کنه قدرت نهایییمون

power = 50
item = ""

if item == "sword" :
    power = power + 30
    print("get sword")
elif item == "shield":
    power = power + 15
    print("get shield")
else:
    power = power - 10
    print("item is broken")   
print(power)
#___________________________________________________________________________________________________________________________
#تمرین جدید
game_items = ['sword', 'bow', 'shield']

power = 0

if game_items[0] == 'sword':
    power = power + 20
    print("Sword is in hand")

if game_items[1] == 'shield':
    power = power + 10
    print("Can protect")

if game_items[2] == 'bow':
    power = power + 15
    print("Can attack from far")

print("Power is:", power)

 
numbers = [5, 23, 17, 30, 12]

for i in numbers:
    if i > 18:
        print("You can enter")
    else:
        print("You can not enter")

#2
numbers = [5, 23, 17, 30, 12]

for i in numbers:
    if i > 18:
        print("You can enter")
    else:
        print("You can not enter")

        #3


        numbers = [20, 18, 15, 9, 12]

for i in numbers:

    if i >= 18 and i <= 20:
        print("Excellent")

    elif i >= 15 and i < 18:
        print("Medium")

    elif i >= 10 and i < 15:
        print("Not good")

    else:
        print("Fail")

        #4
        far_items = []

game_items = [
    'sword',
    'bow',
    'shield',
    'axe',
    'crossbow'
]

if game_items[0] == 'bow' or game_items[0] == 'crossbow':
    far_items.append(game_items[0])
else:
    pass

if game_items[1] == 'bow' or game_items[1] == 'crossbow':
    far_items.append(game_items[1])
else:
    pass

if game_items[2] == 'bow' or game_items[2] == 'crossbow':
    far_items.append(game_items[2])
else:
    pass

if game_items[3] == 'bow' or game_items[3] == 'crossbow':
    far_items.append(game_items[3])
else:
    pass

if game_items[4] == 'bow' or game_items[4] == 'crossbow':
    far_items.append(game_items[4])
else:
    pass

print(far_items)
#--------------------------------------------------------------------------
#تکالیف جذیذ

names = [
    "علی", "سامیار", "محمد", "حسین", "مهدی",
    "امیر", "سارا", "مریم", "نگار", "نرگس",
    "زهرا", "فاطمه", "آرمان", "پارسا", "کیان",
    "یاسین", "رها", "نازنین", "پریسا", "مهسا"
]

# for name in names:
#     print(name)


#----------------------------------
#2
a = [1, 34, 7, 8, 34, 2, 1, 4, 345, 12, 234]

for number in a:
    print(number / 2)


#__________________________________
#3
a = [1, 34, 7, 8, 34, 2, 1, 4, 345, 12, 234]

for number in a:
    if number > 10:
        print(number)
        #_________________________________________________________________________
game_items = ['sword', 'bow', 'shield']

power = 0

for item in game_items:
    if item == 'sword':
        power = power + 20
        print("Sword is in hand")

    elif item == 'shield':
        power = power + 10
        print("Can protect")

    elif item == 'bow':
        power = power + 15
        print("Can attack from far")

print("Power:", power)
#
# _______________________________________________________
numbers = [5, 27, 14, 19, 8]

for num in numbers:
    if num > 18:
        print(num, "You can enter")
    else:
        print(num, "You cannot enter")
#_________________________________________________________
numbers = [20, 17, 15, 9, 12]

for num in numbers:

    if num >= 18 and num <= 20:
        print(num, "Excellent")

    elif num >= 15 and num < 18:
        print(num, "Average")

    elif num >= 10 and num < 15:
        print(num, "Not good")

    else:
        print(num, "Fail")
#________________________________________________________
new_list = []

game_items = [
    'sword',
    'bow',
    'shield',
    'axe',
    'crossbow'
]


for item in game_items:

    if item == 'bow' or item == 'crossbow':
        new_list.append(item)


print(new_list)
#______________________________________
#1
names = [
    "علی", "رضا", "محمد", "حسین", "مهدی",
    "امیر", "سارا", "مریم", "نگار", "نرگس",
    "زهرا", "فاطمه", "آرمان", "پارسا", "کیان",
    "یاسین", "رها", "نازنین", "پریسا", "مهسا"
]

for name in names:
    print(name)

    #_______________________________________________

    #2


a = [1, 34, 7, 8, 34, 2, 1, 4, 345, 12, 234]

for number in a:
    print(number / 2)


    #_________________________________________
    #3

a = [1, 34, 7, 8, 34, 2, 1, 4, 345, 12, 234]

for number in a:
    if number > 10:
        print(number)