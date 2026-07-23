player_hp = 100
attack =  'مشت'

# print(attack != 'مشت')

# -----------------------------
player_hp = 100
action = "ضریه قوی"

"مشت"
"تفنگ"
"ضربه قوی"

if action == "مشت" :
    player_hp = player_hp - 20
elif action == "ضریه قوی" :
    player_hp = player_hp - 40
elif action == "تفنگ" :
    player_hp = player_hp - 80
else :
    player_hp = player_hp - 10



print (player_hp)


if player_hp > 80 :
    print ("ok")
elif player_hp > 50 :
    print ("not bad")
elif player_hp > 20 :
    print ("need bandage")
elif player_hp == 0 :
    print ("dead")

# -----------------------------------------------

print(type(43543))  #--> Integer
print(type("ahmadreza")) #-->String

# ----------------------------------------------
player_hp = 60
# AND OR 
print(player_hp >50 and player_hp<80)

if player_hp >50 and player_hp<80:
    pass
    