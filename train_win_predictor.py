import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load the data
df = pd.read_csv("game_stats.csv")

# Encode categorical columns
df['result'] = df['result'].map({'win': 1, 'loss': 0})
df['difficulty'] = LabelEncoder().fit_transform(df['difficulty'])

# Select features and target
features = [
    'difficulty', 'time_taken', 'guesses_used', 'hints_used',
    'code_length', 'allow_duplicates'
]
X = df[features]
y = df['result']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, predictions))
print(classification_report(y_test, predictions))

# Save model
joblib.dump(model, "win_predictor.pkl")
print("Model saved as win_predictor.pkl")
