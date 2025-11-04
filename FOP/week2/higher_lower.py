import random

print("Welcome to Higher & Lower"
      ", a game where you have 5 attempts to guess the correct number.")


print("When you forgot your previous attempts you can guess"
      "-1 which does not count as a guess but will print your previous guesses!")

print("Choose the guessing range starting from 1 to:")
max_number = int(input())
secret_number = random.randint(1, max_number)

guess_list = []
counter = 0

while True:

    point_list = [10, 8, 5, 2, 1]
    print(f"Guess a number between 1 and {max_number}: ")
    guess = int(input())
    if guess == -1:
        if guess_list:
            print(f"Your previous guess(es) are: {','.join(str(i) for i in guess_list)}")  # Print list of guesses
        continue  # Skip and iterate other

    guess_list.append(guess)
    counter += 1

    if guess < secret_number:  # Guess if lower
        print(f"{guess} is incorrect, the number is higher.")
        if counter == 5:
            print(f"You have tried to following numbers: {' '.join(str(i) for i in guess_list)}"
                  f" to guess the secret number {secret_number}!")
            print("You lost :(")
            points = 0
            break
    elif guess > secret_number:  # Guess if higher
        print(f"{guess} is incorrect, the number is lower.")
        if counter == 5:
            print(f"You have tried to following numbers: {' '.join(str(i) for i in guess_list)}"
                  f" to guess the secret number {secret_number}!")
            print("You lost :(")
            points = 0
            break
    elif guess == secret_number:  # Correct guess
        print(f"You have tried to following numbers: {' '.join(str(i) for i in guess_list)}"
              f" to guess the secret number {secret_number}!")
        if counter <= 5:
            points = point_list[counter - 1]  # Index starts at 0 so use counter - 1
        else:
            points = 0  # if attempts exceed 5
        print(f"You won and are awarded {points} points!")
        break
