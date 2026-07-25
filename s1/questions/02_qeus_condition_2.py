player_hp = 100
attack = 'مشت'

# print(attack != 'مشت')

# -----------------------------
player_hp = 100
action = "ضریه قوی"

"مشت"
"تفنگ"
"ضربه قوی"

if action == "مشت":
    player_hp = player_hp - 20
elif action == "ضریه قوی":
    player_hp = player_hp - 40
elif action == "تفنگ":
    player_hp = player_hp - 80
else:
    player_hp = player_hp - 10


print(player_hp)


if player_hp > 80:
    print("ok")
elif player_hp > 50:
    print("not bad")
elif player_hp > 20:
    print("need bandage")
elif player_hp == 0:
    print("dead")

# -----------------------------------------------

print(type(43543))  # --> Integer
print(type("ahmadreza"))  # -->String

# ----------------------------------------------
player_hp = 60
# AND OR
print(player_hp > 50 and player_hp < 80)

if player_hp > 50 and player_hp < 80:
    pass


# -------------------------------------------------------------
# ep3
player_hp = 40
print(player_hp > 30 and player_hp < 60)
if player_hp > 30 and player_hp < 60:
    pass

weapon = "sword"

# If the weapon is a sword, print that it can fight at close range.
# If the weapon is a bow, print that it can fight from a distance.
# If it is neither, fight with fists.

if weapon == "sword":
    print("It can fight at close range.")


if weapon == "bow":
    print("It can fight from a distance.")
else:
    print("It fights with fists.")

# ------------------------------------
# سن بیشتر از 18
# معدلم بالای 19
# پرینت کنه میتونم برم خارح

age = 19
grade = 20
if age > 18 and grade > 19:
    a = 10
    b = 10
    c = a + b
    print("میتونی بری خارج")
else:
    print("نمیتونی بری خارج")

# ----------------------------------
has_car = False
can_swim = True

if can_swim:
    print("گرنده میماند")
else:
    print("غرق می شود")

if has_car:
    print('کیلومتر را نشان بده')
    print('نمیا ماشی نرا نمایش بده')
