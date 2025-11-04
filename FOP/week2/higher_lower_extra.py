import random

print("Welcome to Higher & Lower"
      ", a game where you have 5 attempts to guess the correct number .")

print("When you forgot your previous attempts you can guess"
      "-1 which does not count as a guess but will print your previous guesses !")
point_list = [10, 8, 5, 2, 1]
round_counter = 0
round_scores = []

max_number = int(input("Choose the guessing range starting from 1 to: "))


while True:  # Outer loop for multiple rounds
    secret_number = random.randint(1, max_number)

    guess_list = []  # Reset guesses for this round
    counter = 0  # Reset attempt counter for this round

    while True:  # Inner loop for guesses in the current round
        guess = int(input(f"\nGuess a number between 1 and {max_number}: "))

        if guess == -1:
            if guess_list:
                print(f"Your previous guess(es) are: {' '.join(str(i) for i in guess_list)}")
            continue

        guess_list.append(guess)
        counter += 1

        if guess < secret_number:  # Guess if lower
            print(f"\n{guess} is incorrect, the number is higher.")
            if counter == 5:
                print(f"You have tried to following numbers: {' '.join(str(i) for i in guess_list)}"
                      f" to guess the secret number {secret_number}!")
                print("You lost :(")
                points = 0
                round_scores.append(points)
                break
        elif guess > secret_number:  # Guess if higher
            print(f"\n{guess} is incorrect, the number is lower.")
            if counter == 5:
                print(f"You have tried to following numbers: {' '.join(str(i) for i in guess_list)}"
                      f" to guess the secret number {secret_number}!")
                print("You lost :(")
                points = 0
                round_scores.append(points)
                break
        else:  # Correct guess
            print(f"\nYou have tried to following numbers: {' '.join(str(i) for i in guess_list)}"
                  f" to guess the secret number {secret_number}!")
            points = point_list[counter - 1] if counter <= 5 else 0  # if counter exceeds 5 then 0 points
            print(f"You won and are awarded {points} points!")
            round_scores.append(points)
            break

    round_counter += 1

    # Ask if player wants to play again
    play_again = str(input("Do you want to play again ? ( y/n ) ")).strip().lower()
    if play_again not in ["yes", "y"]:
        total_points = sum(round_scores)
        max_points = round_counter * point_list[0]
        print(f"\nYou played {round_counter} rounds, where you recieved {total_points}/{max_points} points")
        print(f"You scored per round: {round_scores}")
        break
