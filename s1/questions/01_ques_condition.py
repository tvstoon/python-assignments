# position   مخاصلا
# ِdragon     ازدها
# condition  شرط
# block      بلاک ، وقتی دو نقطه هست

mario_pos = 6
dragon_pos = 8

if dragon_pos >= mario_pos:
    print("mario dead")

else:
    print("mario is life")


print('----------------------------------------------')

player_pos = 10
min_safe = 3
max_safe = 8

if player_pos > min_safe and player_pos < max_safe:
    pass
