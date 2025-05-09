import random
import csv
from CodeCrackGame import CodeCrackGame

def generate_game_data(num_games=5000, output_file="codecrack_data.csv"):
    data = []
    for _ in range(num_games):
        game = CodeCrackGame()
        while game.guesses_remaining > 0 and not game.won:
            guess = ''.join(random.choices(game.digits, k=game.code_length))
            is_valid, _ = game._validate_guess(guess)
            if not is_valid:
                continue
            guess_list = list(guess)
            correct, misplaced = game._get_feedback(guess_list)
            game.history.append((guess_list, correct, misplaced))
            game.guesses_remaining -= 1
            if correct == game.code_length:
                game.won = True
                break
        for guess, c, m in game.history:
            data.append([guess, c, m, ''.join(game.secret_code), game.won, len(game.history)])

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Guess", "Correct", "Misplaced", "SecretCode", "Win", "NumGuesses"])
        writer.writerows(data)

if __name__ == "__main__":
    generate_game_data()
