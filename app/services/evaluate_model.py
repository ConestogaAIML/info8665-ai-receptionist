import joblib
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

df = pd.read_csv(
    "data/processed/processed_appointments.csv"
)

X = df[
    [
        "Age",
        "WaitingDays",
        "AppointmentWeekday",
        "AppointmentHour",
        "SMS_received"
    ]
]

y = df["No-show"]

_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = joblib.load("data/model/no_show_model.pkl")

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("Accuracy:", accuracy)
