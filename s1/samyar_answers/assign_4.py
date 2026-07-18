health = 40
if health < 50:
    print("Health is low")
else:
    print("Health is good")

player_level = 12
if player_level >= 10:
    print("You can enter")
else:
    print("Level is low")

offside_line = 13
player_position = 14
if player_position > offside_line:
    print("آفساید")
else:
    print("آفساید نیست")

finish_point = 40
player_position = 41
if player_position > finish_point:
    print("پلیر برنده شده")

name = "Player1"
level = 5
color_of_skin = "آبی"
print(type(name))
print(type(level))
print(type(color_of_skin))
if color_of_skin == "آبی":
    print("اون دشمن هست")

health = 60
if health > 80:
    print("سالمه")
elif health > 50:
    print("نیاز به دارو")
elif health > 10:
    print("وضعیت بد")
elif health == 0:
    print("مرده ")