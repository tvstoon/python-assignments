# Arithmatic Operators
a = 5
b = 9

c = a+b
f = a*b
l = a**b
m = a/b
p = a % b

print('-----------------------Arithmatic Operators-----------------------')
print('The value of c is :', c)
print('The value of f is :', f)
print('The subtract of f and c is : ', f-c)
print('------------------------------------------------------------------')

# Comparison Operators
var_a = 10
var_b = 20
var_c = 20

print('-----------------------Comparison Operators-----------------------')
print("var_a > var_b :", var_a > var_b)
print("var_a < var_b :", var_a < var_b)
print("var_a <= var_b :", var_a <= var_b)
print("var_c <= var_b :", var_c <= var_b)
print("var_c < var_b :", var_c < var_b)
print("var_c >= var_b :", var_c >= var_b)
print("var_a == var_b :", var_a == var_b)
print("var_b == var_c :", var_b == var_c)
print("var_b != var_c :", var_b != var_c)
print('------------------------------------------------------------------')

# Assignment Operators
Number_1 = 2
Number_2 = 5
# Number_1 = Number_1+1
Number_1 += 1
Number_2 -= 10


print('-----------------------Assignment Operators-----------------------')
print(Number_1)
print(Number_2)
print('------------------------------------------------------------------')


# Ligical Operators
# and , &
# or , |


print('-----------------------Example-----------------------')
# Example

# Arithmetic Operators
player_money = 5000
car_price = 3000
gun_price = 1200

total_cost = car_price + gun_price
remaining_money = player_money - total_cost
double_reward = 500 * 2
power = 2 ** 3
team_share = 1000 / 4
remaining_bullets = 17 % 5

print("هزینه کل:", total_cost)
print("پول باقی‌مانده:", remaining_money)
print("جایزه دو برابر:", double_reward)
print("قدرت بازیکن:", power)
print("سهم هر بازیکن:", team_share)
print("گلوله باقی‌مانده:", remaining_bullets)

# Comparison Operators
player_health = 80
enemy_health = 50
required_level = 10
player_level = 10

print("بازیکن قوی‌تر است:", player_health > enemy_health)
print("دشمن قوی‌تر است:", enemy_health > player_health)
print("بازیکن اجازه ورود دارد:", player_level >= required_level)
print("سطح بازیکن دقیقاً 10 است:", player_level == 10)
print("جان بازیکن صفر نیست:", player_health != 0)
