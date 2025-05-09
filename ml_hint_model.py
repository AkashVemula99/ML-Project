import random

class MLHintModel:
    def __init__(self, digits, code_length, max_hints=5):
        self.digits = digits
        self.code_length = code_length
        self.max_hints = max_hints
        self.hints_used = 0

    def suggest(self, history):
        if self.hints_used >= self.max_hints:
            return None  # No hints left

        likely_digits = set()
        confirmed_wrong_digits = set()

        # Analyze feedback from history
        for guess, correct, misplaced in history:
            total_hits = correct + misplaced
            if total_hits == 0:
                confirmed_wrong_digits.update(guess)
            else:
                likely_digits.update(guess)

        remaining_digits = [d for d in self.digits if d not in confirmed_wrong_digits]

        # Build a smart guess using likely digits or remaining options
        suggestion = []
        for _ in range(self.code_length):
            if likely_digits:
                suggestion.append(random.choice(list(likely_digits)))
            else:
                suggestion.append(random.choice(remaining_digits or self.digits))

        self.hints_used += 1
        return ''.join(suggestion)
