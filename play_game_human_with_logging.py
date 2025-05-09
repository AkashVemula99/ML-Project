from CodeCrackGame import CodeCrackGame
import time
import csv
import os

def play_game():
    print("🎮 Welcome to CodeCrack!")
    print("Try to guess the secret code. You’ll get feedback after each guess.")
    
    # Initialize game
    game = CodeCrackGame(code_length=4, max_guesses=10, allow_duplicates=True, digit_range=(1, 6))
    print(f"Digits range: {game.digits[0]} to {game.digits[-1]}")
    print(f"You have {game.max_guesses} guesses. Good luck!\n")
    
    start_time = time.time()

    # Prepare CSV logging
    csv_file = "game_stats.csv"
    if not os.path.exists(csv_file):
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["guess", "correct", "misplaced", "time_elapsed", "hints_used", "code_length", "duplicates_allowed"])
    
    while game.guesses_remaining > 0:
        guess_str = input(f"Enter your guess ({game.code_length} digits): ").strip()
        is_valid, error = game._validate_guess(guess_str)
        
        if not is_valid:
            print(f"❌ {error}\n")
            continue
        
        guess = list(guess_str)
        correct, misplaced = game._get_feedback(guess)
        game.history.append((guess, correct, misplaced))
        game.guesses_remaining -= 1

        # Log attempt to CSV
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                guess_str,
                correct,
                misplaced,
                round(time.time() - start_time, 2),
                0,  # hints_used is static here
                game.code_length,
                game.allow_duplicates
            ])

        print(f"✅ Correct: {correct}, 🔁 Misplaced: {misplaced}, 🕐 Guesses left: {game.guesses_remaining}\n")

        if correct == game.code_length:
            print("🎉 Congratulations! You cracked the code!")
            game.won = True
            break
    
    if not game.won:
        print(f"❌ Game over. The secret code was: {''.join(game.secret_code)}")

if __name__ == "__main__":
    play_game()
