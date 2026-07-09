import pandas as pd

df = pd.read_csv("data/raw/appointments.csv")

print(df.columns)

selected_columns = [
    "PatientId",
    "Age",
    "Gender",
    "ScheduledDay",
    "AppointmentDay",
    "SMS_received",
    "No-show",
]

df = df[selected_columns]

df["ScheduledDay"] = pd.to_datetime(df["ScheduledDay"])
df["AppointmentDay"] = pd.to_datetime(df["AppointmentDay"])

df["WaitingDays"] = (df["AppointmentDay"] - df["ScheduledDay"]).dt.days

df["AppointmentWeekday"] = df["AppointmentDay"].dt.weekday

df["AppointmentHour"] = df["AppointmentDay"].dt.hour

features = [
    "Age",
    "WaitingDays",
    "AppointmentWeekday",
    "AppointmentHour",
    "SMS_received",
]

target = "No-show"

df["No-show"] = df["No-show"].map({"Yes": 1, "No": 0})

df = df[["PatientId"] + features + [target]]

df.to_csv("data/processed/processed_appointments.csv", index=False)
