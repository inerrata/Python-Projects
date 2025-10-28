import random

given_number = random.randint(256, 1024)

print("Given number: ", given_number)

mynum = float(input("Input your number: "))


if mynum == given_number:
    print("The input is the same as the given number is True")
else:
    print("The input is the same as the given number is False")

if mynum < given_number:
    print("The input is smaller compared to the given number is True")
else:
    print("The input is smaller compared to the given number is False")

if mynum != 0 and given_number != 0:
    print("The input and the given number are both not zero True")
else:
    print("The input and the given number are both not zero False")

if id(mynum) == id(given_number):
    print("The input is the same memory object as the given number is True")
else:
    print("The input is the same memory object as the given number is False")
