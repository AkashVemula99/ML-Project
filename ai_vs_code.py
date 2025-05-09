from CodeCrackGame import CodeCrackGame
from itertools import product

class CodeCrackSolver:
    def __init__(self, digits, code_length=4, allow_duplicates=True):
        self.digits = digits
        self.code_length = code_length
        self.allow_duplicates = allow_duplicates
        self.history = []
        self.all_codes = self._generate_all_possible_codes()

    def _generate_all_possible_codes(self):
        if self.allow_duplicates:
            return [''.join(p) for p in product(self.digits, repeat=self.code_length)]
        else:
            from itertools import permutations
            return [''.join(p) for p in permutations(self.digits, r=self.code_length)]

    def _feedback(self, guess, code):
        correct = sum(g == c for g, c in zip(guess, code))
        misplaced = sum(min(guess.count(d), code.count(d)) for d in set(guess)) - correct
        return correct, misplaced

    def filter_possible_codes(self, guess, correct, misplaced):
        self.all_codes = [code for code in self.all_codes if self._feedback(guess, code) == (correct, misplaced)]

    def next_guess(self):
        return self.all_codes[0] if self.all_codes else None

def play_vs_ai(code_length=4, max_guesses=10, allow_duplicates=True, digit_range=(1, 6)):
    game = CodeCrackGame(code_length=code_length, max_guesses=max_guesses,
                         allow_duplicates=allow_duplicates, digit_range=digit_range)
    ai = CodeCrackSolver(digits=game.digits, code_length=code_length, allow_duplicates=allow_duplicates)

    print(f"[AI] Trying to crack a {code_length}-digit code. Digits: {game.digits[0]}-{game.digits[-1]}")
    print(f"Secret Code (hidden): {'*' * code_length}\n")

    while game.guesses_remaining > 0:
        guess = ai.next_guess()
        if guess is None:
            print("AI has no valid guesses left. Aborting.")
            break

        correct, misplaced = game._get_feedback(list(guess))
        game.history.append((list(guess), correct, misplaced))
        game.guesses_remaining -= 1
        ai.filter_possible_codes(guess, correct, misplaced)

        print(f"AI Guess: {guess} | Correct: {correct} | Misplaced: {misplaced} | Guesses Left: {game.guesses_remaining}")

        if correct == code_length:
            print("\n🎉 AI cracked the code!")
            break

    if game.guesses_remaining == 0 and not game.won:
        print(f"\n❌ AI failed to crack the code. Secret was: {''.join(game.secret_code)}")

def select_difficulty():
    print("Select Difficulty Level:")
    print("1. Easy (4 digits, duplicates allowed)")
    print("2. Medium (5 digits, no duplicates)")
    print("3. Hard (6 digits, no duplicates)")

    choice = input("Enter choice (1/2/3): ").strip()
    if choice == '1':
        return 4, 10, True
    elif choice == '2':
        return 5, 10, False
    elif choice == '3':
        return 6, 10, False
    else:
        print("Invalid choice. Defaulting to Medium.")
        return 5, 10, False

if __name__ == "__main__":
    code_length, max_guesses, allow_duplicates = select_difficulty()
    play_vs_ai(code_length=code_length, max_guesses=max_guesses, allow_duplicates=allow_duplicates, digit_range=(1, 6))
