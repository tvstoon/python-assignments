
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
line_offside = 13
enemy_player = 14
enemy_number = enemy_player
if enemy_number > line_offside:
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
health = 60
my_health = health
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
height = 175
age = 16
my_height = height
my_age = age
if my_height > 170 and my_age > 15:
    print("Can go to pool")
else:
    print("Cannot go to pool")

# 10
player_point = 25
my_point = player_point
if my_point > 10 and my_point < 50:
    print("Place is safe")
elif my_point > 0 and my_point < 10:
    print("Place is not safe")
else:
    print("Point is not in the ranges")