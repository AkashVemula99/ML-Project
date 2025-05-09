import random

class CodeCrackGame:
    """
    The logic engine for CodeCrack game (similar to Mastermind).
    Generates a secret code and evaluates user guesses.
    """

    def __init__(self, code_length=4, max_guesses=10, allow_duplicates=True, digit_range=(1, 6)):
        """
        Initializes game settings and secret code.

        Args:
            code_length (int): Number of digits in the code.
            max_guesses (int): Maximum number of guesses allowed.
            allow_duplicates (bool): Whether duplicate digits are allowed.
            digit_range (tuple): The digit range (min, max) inclusive.
        """
        if not (isinstance(code_length, int) and code_length > 0):
            raise ValueError("Code length must be a positive integer.")
        if not (isinstance(max_guesses, int) and max_guesses > 0):
            raise ValueError("Max guesses must be a positive integer.")
        if not (isinstance(digit_range, tuple) and len(digit_range) == 2 and all(isinstance(i, int) for i in digit_range)):
            raise ValueError("Digit range must be a tuple of two integers.")

        self.code_length = code_length
        self.max_guesses = max_guesses
        self.allow_duplicates = allow_duplicates
        self.digits = [str(i) for i in range(digit_range[0], digit_range[1] + 1)]
        self.secret_code = self._generate_secret_code()
        self.guesses_remaining = max_guesses
        self.history = []  # (guess_list, correct, misplaced)
        self.won = False

    def _generate_secret_code(self):
        """Generates a secret code based on rules."""
        if self.allow_duplicates:
            return random.choices(self.digits, k=self.code_length)
        else:
            return random.sample(self.digits, k=self.code_length)

    def _validate_guess(self, guess_str):
        """
        Validates a guess string.

        Returns:
            (bool, str): Tuple of (is_valid, error_message)
        """
        if len(guess_str) != self.code_length:
            return False, f"Guess must be {self.code_length} digits long."

        if not all(c in self.digits for c in guess_str):
            return False, f"Digits must be between {self.digits[0]} and {self.digits[-1]}."

        if not self.allow_duplicates and len(set(guess_str)) != self.code_length:
            return False, "Duplicate digits are not allowed."

        return True, ""

    def _get_feedback(self, guess):
        """
        Compares the guess to the secret code.

        Returns:
            (int, int): Tuple of (correct_position, correct_digit_wrong_position)
        """
        correct = sum(g == s for g, s in zip(guess, self.secret_code))
        misplaced = sum(min(guess.count(d), self.secret_code.count(d)) for d in set(guess)) - correct
        return correct, misplaced
