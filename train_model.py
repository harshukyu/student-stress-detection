import pickle
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load real dataset
df = pd.read_csv("StressLevelDataset.csv")

# Use relevant features
X = df[["sleep_quality", "study_load", "anxiety_level", "mental_health_history"]]
y = df["stress_level"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Decision Tree
model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(X_train, y_train)

# Accuracy
predictions = model.predict(X_test)
acc = accuracy_score(y_test, predictions)
print(f"Model Accuracy: {acc * 100:.1f}%")

# Save model
with open("stress_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved as stress_model.pkl")
print("Training complete!")