from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib

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

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier()

model.fit(X_train, y_train)

joblib.dump(
    model,
    "data/model/no_show_model.pkl"
)
