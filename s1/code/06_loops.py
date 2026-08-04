# for loop
list_a = [10, 20, 30, 1, 2, 4, 5, 6]

for i in list_a:
    if i % 2 == 0:
        print(i, 'is divisible by 2')
    else:
        print(i, 'is not divisible by 2')

# while loop
a = 1
while a < 20:
    print(a)
    a = a+1

# For loop with range and break
list_range = range(1, 100)
for b in list_range:
    print(b)
    if b % 9 == 0:
        break

# continue
list_range = range(1, 100)
for b in list_range:
    if b % 9 == 0:
        continue

    print(b)
