
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Load the dataset
df = pd.read_csv("game_stats.csv")

# Define difficulty labels based on time_taken and guesses_used
def label_difficulty(row):
    if row['time_taken'] <= 30 and row['guesses_used'] <= 5:
        return 'easy'
    elif row['time_taken'] <= 60:
        return 'medium'
    else:
        return 'hard'

df['difficulty_label'] = df.apply(label_difficulty, axis=1)

# Features and target
features = ['time_taken', 'guesses_used', 'hints_used', 'code_length', 'allow_duplicates']
X = df[features]
y = df['difficulty_label']

# Convert boolean to int
X['allow_duplicates'] = X['allow_duplicates'].astype(int)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
predictions = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, predictions))
print("Classification Report:\n", classification_report(y_test, predictions))

# Save model
joblib.dump(model, "difficulty_predictor.pkl")
print("Model saved as difficulty_predictor.pkl")
