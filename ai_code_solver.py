import tkinter as tk
from tkinter import messagebox, ttk
from itertools import product, permutations
import random
import time
import csv
import joblib
import os
import hashlib
from datetime import datetime, timedelta
from ml_hint_model import MLHintModel
from sklearn.preprocessing import LabelEncoder
from PIL import Image, ImageTk

# Game Logic
class CodeCrackGame:
    def __init__(self, code_length=4, max_guesses=10, allow_duplicates=True, digit_range=(1, 6)):
        self.code_length = code_length
        self.max_guesses = max_guesses
        self.allow_duplicates = allow_duplicates
        self.digits = [str(i) for i in range(digit_range[0], digit_range[1] + 1)]
        self.secret_code = self._generate_secret_code()
        self.guesses_remaining = max_guesses
        self.history = []
        self.won = False

    def _generate_secret_code(self):
        if self.allow_duplicates:
            return random.choices(self.digits, k=self.code_length)
        else:
            return random.sample(self.digits, k=self.code_length)
        
    def _generate_daily_code(self):
        today = datetime.now().strftime("%Y-%m-%d")
        seed = int(hashlib.sha256(today.encode()).hexdigest(), 16) % (10 ** 8)
        rng = random.Random(seed)
        if self.allow_duplicates:
            return [rng.choice(self.digits) for _ in range(self.code_length)]
        else:
            return rng.sample(self.digits, k=self.code_length)

    def _validate_guess(self, guess_str):
        if len(guess_str) != self.code_length:
            return False, f"Guess must be {self.code_length} digits."
        if not all(c in self.digits for c in guess_str):
            return False, f"Digits must be between {self.digits[0]} and {self.digits[-1]}."
        if not self.allow_duplicates and len(set(guess_str)) != self.code_length:
            return False, "Duplicates not allowed."
        return True, ""

    def _get_feedback(self, guess):
        correct = sum(g == s for g, s in zip(guess, self.secret_code))
        misplaced = sum(min(guess.count(d), self.secret_code.count(d)) for d in set(guess)) - correct
        return correct, misplaced

# AI Solver Logic (Rule-based)
class CodeCrackSolver:
    def __init__(self, code_length=4, digits='123456', allow_duplicates=True):
        self.code_length = code_length
        self.digits = digits
        self.allow_duplicates = allow_duplicates
        self.history = []
        self.all_possible = self._generate_all_codes()

    def _generate_all_codes(self):
        if self.allow_duplicates:
            return [''.join(p) for p in product(self.digits, repeat=self.code_length)]
        else:
            return [''.join(p) for p in permutations(self.digits, r=self.code_length)]

    def _feedback(self, guess, secret):
        correct = sum(g == s for g, s in zip(guess, secret))
        misplaced = sum(min(guess.count(d), secret.count(d)) for d in set(guess)) - correct
        return correct, misplaced

    def filter(self, guess, correct, misplaced):
        self.history.append((guess, correct, misplaced))
        self.all_possible = [code for code in self.all_possible
                             if self._feedback(code, guess) == (correct, misplaced)]

    def next_guess(self):
        return self.all_possible[0] if self.all_possible else None

# GUI with AI and Hints
class CodeCrackGUI:
    def __init__(self, master):
        self.daily_result_summary = None
        self.master = master
        self.master.title("CodeCrack Game with AI Solver")
        self.master.geometry("500x650")
        self.creator_mode = False  # Set to False for public version
        self.daily_result_summary = None
        self.current_streak = 0
        self.longest_streak = 0
        self.load_streaks()
        self.theme = "Light"  # Default

        self.difficulty_settings = {
            "Easy": {"code_length": 4, "max_guesses": 10, "allow_duplicates": False},
            "Medium": {"code_length": 5, "max_guesses": 10, "allow_duplicates": True},
            "Hard": {"code_length": 6, "max_guesses": 10, "allow_duplicates": True}
        }

        self.create_start_menu()
    def load_streaks(self):
        if os.path.exists("streaks.txt"):
            with open("streaks.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    self.current_streak = int(lines[0].strip())
                    self.longest_streak = int(lines[1].strip())
                else:
                    self.current_streak = 0
                    self.longest_streak = 0
        else:
            self.current_streak = 0
            self.longest_streak = 0
    
    def save_streaks(self):
        with open("streaks.txt", "w") as f:
            f.write(f"{self.current_streak}\n{self.longest_streak}\n")

    def create_start_menu(self):
        self.clear_window()

        top_frame = tk.Frame(self.master)
        top_frame.pack(fill="x", pady=(10, 0))

        # First row: Title
        self.title_label = tk.Label(
            top_frame,
            text="🎯 CodeCrack Challenge",
            font=("Helvetica", 22, "bold"),
            fg="#ED7117",  # carrot
            bg=self.master["bg"]
        )
        self.title_label.pack(anchor="center", pady=(10, 5))

        # Second row: Theme Selector (to the right)
        # Second row: Theme Selector (right) + Info (left)
        theme_frame = tk.Frame(top_frame)
        theme_frame.pack(fill="x", pady=(0, 10), padx=10)

        # ❔ Info Button (left-most)
        info_btn = tk.Button(theme_frame, text="❔", font=("Helvetica", 10), command=self.show_rules)
        info_btn.pack(side="left", padx=(0, 10))

        # 📊 Stats Button
        self.stats_btn = tk.Button(theme_frame, text="View My Stats", command=self.show_stats)
        self.stats_btn.pack(side="left")

        # 🎨 Theme Label and Dropdown
        self.theme_var = tk.StringVar(value="Light")
        self.theme_dropdown = ttk.Combobox(theme_frame, textvariable=self.theme_var, state="readonly", width=7)
        self.theme_dropdown['values'] = ["Light", "Dark"]
        self.theme_dropdown.current(0)
        self.theme_dropdown.pack(side="right", padx=(0, 10))
        self.theme_dropdown.bind("<<ComboboxSelected>>", lambda e: self.apply_theme_from_dropdown())

        self.theme_label = tk.Label(theme_frame, text="Select Theme:", font=("Helvetica", 10))
        self.theme_label.pack(side="right", padx=(0, 5))

        self.level_label = tk.Label(self.master, text="Select Difficulty:", font=("Helvetica", 12))
        self.level_label.pack(pady=10)

        self.difficulty_var = tk.StringVar()
        self.difficulty_dropdown = ttk.Combobox(self.master, textvariable=self.difficulty_var, state="readonly")
        self.difficulty_dropdown['values'] = ["Easy", "Medium", "Hard"]
        self.difficulty_dropdown.current(0)
        self.difficulty_dropdown.pack(pady=10)

        self.start_btn = tk.Button(self.master, text="Start Game", command=self.start_game)
        self.start_btn.pack(pady=20)
        self.daily_btn = tk.Button(self.master, text="Daily Puzzle", command=self.start_daily_game)
        self.daily_btn.pack(pady=5)

        # Show Daily Puzzle Summary if available
        if self.daily_result_summary:
            result, code = self.daily_result_summary
            if result == "win":
                result_text = f"🎉 You cracked today's code!\nThe correct code was: {code}"
            else:
                result_text = f"❌ You failed to crack today's code!\nThe correct code was: {code}"
            self.daily_result_label = tk.Label(self.master, text=result_text, font=("Helvetica", 10, "italic"))
            self.daily_result_label.pack(pady=2)

        # 🔥 Show Streak Info
        streak_text = f"🔥 Current Streak: {self.current_streak} days   🏆 Longest Streak: {self.longest_streak} days"
        self.streak_label = tk.Label(self.master, text=streak_text, font=("Helvetica", 10, "italic"))
        self.streak_label.pack(pady=2)

        # Countdown Timer
        self.reset_timer_label = tk.Label(self.master, text="", font=("Helvetica", 10, "italic"))
        self.reset_timer_label.pack(pady=2)
        self.update_countdown_timer()
    
    def apply_theme_from_dropdown(self):
        self.theme = self.theme_var.get()
        self.apply_theme()

    def start_game(self):
        settings = self.difficulty_settings[self.difficulty_var.get()]
        self.game = CodeCrackGame(**settings)
        self.current_level = self.difficulty_var.get()
        self.solver = CodeCrackSolver(code_length=self.game.code_length,
                                       digits=''.join(self.game.digits),
                                       allow_duplicates=self.game.allow_duplicates)
        self.ml_model = MLHintModel(self.game.digits, self.game.code_length, max_hints=5)
        self.start_time = time.time()
        self.daily_mode = False

        self.clear_window()
        self.create_widgets()
        self.update_board()
        self.theme = self.theme_var.get()
        self.apply_theme()

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def apply_theme(self):
        if self.theme == "Light":
            bg_color = "white"
            fg_color = "black"
        else:  # Dark
            bg_color = "#333333"
            fg_color = "white"

        self.master.configure(bg=bg_color)

        # Update ALL labels/buttons dynamically
        for widget in self.master.winfo_children():
            if isinstance(widget, (tk.Label, tk.Button, tk.Entry, ttk.Combobox)):
                try:
                    widget.configure(bg=bg_color, fg=fg_color)
                except:
                    pass  # For combobox, sometimes ignore if fails

    def create_widgets(self):
        self.title_label = tk.Label(self.master, text="CodeCrack", font=("Helvetica", 20, "bold"))
        self.title_label.pack(pady=10)

        # 🟧 Top-right Difficulty Display
        self.level_display = tk.Label(self.master, text=f"🧠 Level: {self.current_level}", font=("Helvetica", 10, "italic"))
        self.level_display.place(x=10, y=10)

        # Info Button (ℹ️) at top-right
        info_btn = tk.Button(self.master, text="❔", font=("Helvetica", 10), command=self.show_rules)
        info_btn.place(x=460, y=10, width=30, height=30)

        self.instructions_label = tk.Label(self.master, text=f"Guess the {self.game.code_length}-digit code.\n Select the numbers between 1 - 6 \n No duplicate digits (Easy), duplicates allowed (Medium/Hard)", font=("Helvetica", 10))
        self.instructions_label.pack(pady=5)

        self.guess_entry = tk.Entry(self.master, font=("Helvetica", 14), width=10, justify="center")
        self.guess_entry.pack(pady=10)
        self.guess_entry.bind("<Return>", lambda e: self.submit_guess())

        self.submit_btn = tk.Button(self.master, text="Submit Guess", command=self.submit_guess)
        self.submit_btn.pack(pady=5)

        self.hint_btn = tk.Button(self.master, text="Get AI Hint", command=self.get_hint)
        self.hint_btn.pack(pady=5)

        self.hints_left_label = tk.Label(self.master, text=f"Hints left: {self.ml_model.max_hints - self.ml_model.hints_used}", font=("Helvetica", 10, "italic"))
        self.hints_left_label.pack(pady=2)

        self.board_frame = tk.Frame(self.master)
        self.board_frame.pack(pady=10)

        self.control_frame = tk.Frame(self.master)
        self.control_frame.pack(pady=20)

        self.restart_btn = tk.Button(self.control_frame, text="Restart", command=self.create_start_menu)
        self.restart_btn.pack(side="left", padx=10)

        self.quit_btn = tk.Button(self.control_frame, text="Quit", command=self.master.quit)
        self.quit_btn.pack(side="right", padx=10)

        self.win_chance_label = tk.Label(self.master, text="Win Chance: --", font=("Helvetica", 10, "italic"))
        self.win_chance_label.pack(pady=2)
        self.load_model()

    def load_model(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        if os.path.exists("win_predictor.pkl"):
            self.model = joblib.load("win_predictor.pkl")
            self.label_encoder.fit(["Easy", "Medium", "Hard"])

    def update_win_prediction(self):
        if self.model is None:
            self.win_chance_label.config(text="Win Chance: --")
            return

        difficulty_encoded = self.label_encoder.transform([self.difficulty_var.get()])[0]
        time_taken = time.time() - self.start_time
        hints_used = self.ml_model.hints_used
        guesses_used = len(self.game.history)

        features = [[
            difficulty_encoded, time_taken, guesses_used, hints_used,
            self.game.code_length, int(self.game.allow_duplicates)
        ]]

        prob = self.model.predict_proba(features)[0][1]
        self.win_chance_label.config(text=f"Win Chance: {int(prob * 100)}%")       

    def update_board(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        header = tk.Label(self.board_frame, text="Guess   |  Correct  |  Misplaced", font=("Helvetica", 12, "bold"))
        header.pack()

        for guess, correct, misplaced in self.game.history:
            guess_str = ''.join(guess)
            emoji = f"{'✔️' * correct}{'↔️' * misplaced}{'✖️' * (self.game.code_length - correct - misplaced)}"
            row_text = f"{guess_str:^8} | {correct:^8} | {misplaced:^8}  {emoji}"

            bg_color = "lightgreen" if correct == self.game.code_length else ("lightyellow" if correct > 0 or misplaced > 0 else "lightgrey")
            row_label = tk.Label(self.board_frame, text=row_text, font=("Courier", 12), bg=bg_color)
            row_label.pack(fill='x', pady=1)

        for _ in range(self.game.max_guesses - len(self.game.history)):
            row_label = tk.Label(self.board_frame, text=f"{'?' * self.game.code_length:^8} | {'?':^8} | {'?':^8}", font=("Courier", 12))
            row_label.pack()

        self.hints_left_label.config(text=f"Hints left: {self.ml_model.max_hints - self.ml_model.hints_used}")

    def show_stats_popup(self, result):
        time_taken = time.time() - self.start_time
        total_guesses = len(self.game.history)
        hints_used = self.ml_model.hints_used
        secret_code = ''.join(self.game.secret_code)

        message = (
            f"Result: {'✅ You Won!' if result == 'win' else '❌ You Lost'}\n"
            f"Secret Code: {secret_code}\n"
            f"Time Taken: {time_taken:.1f} seconds\n"
            f"Guesses Used: {total_guesses}/{self.game.max_guesses}\n"
            f"Hints Used: {hints_used}/{self.ml_model.max_hints}"
        )
        messagebox.showinfo("Game Stats", message)
        if "Daily Puzzle" in self.title_label.cget("text"):
    
            file_exists = os.path.exists("daily_scores.csv")
            with open("daily_scores.csv", "a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Date", "Result", "Guesses Used", "Time Taken"])
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d"),
                    result,
                    len(self.game.history),
                    round(time.time() - self.start_time, 1)
                ])

    def submit_guess(self):
        guess = self.guess_entry.get().strip()

        # Validate guess
        is_valid, msg = self.game._validate_guess(guess)
        if not is_valid:
            messagebox.showwarning("Invalid Guess", msg)
            return

        guess_list = list(guess)
        correct, misplaced = self.game._get_feedback(guess_list)
        self.game.history.append((guess_list, correct, misplaced))
        self.solver.filter(guess, correct, misplaced)
        self.game.guesses_remaining -= 1
        self.guess_entry.delete(0, tk.END)

        self.update_board()
        self.update_win_prediction()

        if correct == self.game.code_length:
            self.disable_game()
            if getattr(self, 'daily_mode', False):
                self.daily_result_summary = ("win", ''.join(self.game.secret_code))  # ✅ Save result
                self.current_streak += 1
                if self.current_streak > self.longest_streak:
                   self.longest_streak = self.current_streak
                self.save_streaks()
                self.show_stats_popup("win")
                self.create_start_menu()
            else:
                self.show_stats_popup("win")
                self.create_start_menu()

        elif self.game.guesses_remaining == 0:
            self.disable_game()
            if getattr(self, 'daily_mode', False):
                self.daily_result_summary = ("loss", ''.join(self.game.secret_code))  # ✅ Save result
                self.current_streak = 0
                self.save_streaks()
                self.show_stats_popup("loss")
                self.create_start_menu()
            else:
                self.show_stats_popup("loss")
                self.create_start_menu()

        else:
            self.update_board()
            self.update_win_prediction()

    def get_hint(self):
        suggestion = self.ml_model.suggest(self.game.history)
        if suggestion:
            self.guess_entry.delete(0, tk.END)
            self.guess_entry.insert(0, suggestion)
        else:
            messagebox.showinfo("No Hints Left", "You have used all your hints!")
        self.hints_left_label.config(text=f"Hints left: {self.ml_model.max_hints - self.ml_model.hints_used}")

    def disable_game(self):
        self.submit_btn.config(state="disabled")
        self.guess_entry.config(state="disabled")
        self.hint_btn.config(state="disabled")

    def start_daily_game(self):
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if today's puzzle was already played
        if not getattr(self, 'creator_mode', False):  # Only enforce if not creator mode
            if os.path.exists("daily_played.txt"):
                with open("daily_played.txt") as f:
                    if today in f.read():
                        messagebox.showinfo("Daily Puzzle", "You've already played today's puzzle!")
                        return

        with open("daily_played.txt", "w") as f:
           f.write(today)

        # Setup Daily Game
        # Randomly choose a level each day using date-based seed for consistency
        today = datetime.now().strftime("%Y-%m-%d")
        seed = int(hashlib.sha256(today.encode()).hexdigest(), 16) % (10 ** 8)
        rng = random.Random(seed)
        level = rng.choice(["Easy", "Medium", "Hard"])
        settings = self.difficulty_settings[level]
        self.current_level = level  # ✅ So level display works in create_widgets
        self.game = CodeCrackGame(**settings)
        self.game.secret_code = self.game._generate_daily_code()
        self.solver = CodeCrackSolver(code_length=self.game.code_length,
                                       digits=''.join(self.game.digits),
                                       allow_duplicates=self.game.allow_duplicates)
        self.ml_model = MLHintModel(self.game.digits, self.game.code_length, max_hints=5)
        self.start_time = time.time()
        self.daily_mode = True

        self.theme = self.theme_var.get()
        self.apply_theme()

        self.clear_window()
        self.create_widgets()
        self.update_board()

        # Update title
        self.title_label.config(text="CodeCrack \n Daily Puzzle")

        # Show today's date
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_label = tk.Label(self.master, text=f"🗓️ Daily Puzzle for: {today}", font=("Helvetica", 10, "italic"))
        self.date_label.pack()

        # Create daily result and countdown labels
        self.daily_result_label = tk.Label(self.master, text="", font=("Helvetica", 10, "italic"))
        self.daily_result_label.pack(pady=2)
        self.reset_timer_label = tk.Label(self.master, text="", font=("Helvetica", 10, "italic"))
        self.reset_timer_label.pack(pady=2)

        self.update_countdown_timer()
    
    def show_daily_result_message(self, result):
        if result == "win":
            msg = "🎉 You cracked today's code!"
        else:
            msg = "❌ You failed to crack today's code!"
        self.daily_result_label.config(text=f"{msg}\nThe correct code was: {''.join(self.game.secret_code)}")
        self.update_countdown_timer()
    
    def update_countdown_timer(self):
        now = datetime.now()
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_left = int((midnight - now).total_seconds())
        hours, remainder = divmod(seconds_left, 3600)
        minutes, seconds = divmod(remainder, 60)
    
        # Safe check: only update if label still exists
        if hasattr(self, 'reset_timer_label') and self.reset_timer_label.winfo_exists():
            self.reset_timer_label.config(text=f"The Puzzle will reset in {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.master.after(1000, self.update_countdown_timer)

    def show_stats(self):
        total_games = 0
        wins = 0
        guess_distribution = {}

        if os.path.exists("daily_scores.csv"):
            with open("daily_scores.csv", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_games += 1
                    if row['Result'].lower() == 'win':  # <- Capital "R"
                        wins += 1
                    guesses_used = int(row['Guesses Used'])
                    guess_distribution[guesses_used] = guess_distribution.get(guesses_used, 0) + 1

        win_percentage = (wins / total_games) * 100 if total_games > 0 else 0

        # Create popup
        stats_window = tk.Toplevel(self.master)
        stats_window.title("My Stats")
        stats_window.geometry("400x400")

        stats_label = tk.Label(stats_window, text="📊 Statistics", font=("Helvetica", 16, "bold"))
        stats_label.pack(pady=10)

        summary = f"""
    Games Played: {total_games}
    Win %: {win_percentage:.2f}
    Current Streak: {self.current_streak}
    Max Streak: {self.longest_streak}
        """
        summary_label = tk.Label(stats_window, text=summary, font=("Helvetica", 12), justify="left")
        summary_label.pack(pady=10)

        guess_label = tk.Label(stats_window, text="Guess Distribution:", font=("Helvetica", 12, "bold"))
        guess_label.pack(pady=5)

        for guess_count in sorted(guess_distribution.keys()):
            bar = "█" * guess_distribution[guess_count]
            row_text = f"{guess_count}: {bar} ({guess_distribution[guess_count]})"
            row_label = tk.Label(stats_window, text=row_text, font=("Courier", 10))
            row_label.pack(anchor="w", padx=20)

    def show_rules(self):
        rules = (
            "🎯 CodeCrack Game Rules:\n\n"
            "• Your goal is to guess the hidden code.\n"
            "• After each guess, you'll receive feedback:\n"
            "   ✔️ = Correct digit in correct position\n"
            "   ↔️ = Correct digit in wrong position\n"
            "   ✖️ = Incorrect digit\n"
            "• No duplicate digits (Easy), duplicates allowed (Medium/Hard).\n"
            "• You have limited guesses — use them wisely!\n"
            "• You can request hints using the AI hint button.\n"
            "• Daily Puzzle resets every midnight.\n"
        )
        messagebox.showinfo("How to Play", rules)

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeCrackGUI(root)
    root.mainloop()