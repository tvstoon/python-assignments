name = "samyar"
health = 100
power = 25
level = 1
#____________________________________________________________________________________________________


player_name = "Samyar"
money = 500
health = 100
is_alive = True



car_name = "tara"
speed = 180
fuel = 50
is_locked = False

print("car_name =", type(car_name))
print("speed =", type(speed))
print("fuel =", type(fuel))
print("is_locked =", type(is_locked))

items = ["Gun", 30, "Food"]

print(type(items))

#_____________________________________________________________________________________________________________


money = 8000
armor_price = 2500
gun_price = 1800
food_price = 500

total_price = armor_price + gun_price + food_price
remaining_money = money - total_price

print(total_price)
print(remaining_money)



reward = 2400
players = 4

share = reward / players

print(share)



bullets = 53
box_capacity = 10

remaining_bullets = bullets % box_capacity

print(remaining_bullets)



magic_power = 3

final_power = magic_power ** 4

print(final_power)



player_health = 75
enemy_health = 90

print(player_health > enemy_health)
print(enemy_health > player_health)
print(player_health == enemy_health)
print(player_health != enemy_health)