# Machine Learning–Driven Appointment No-Show Prediction and Smart Scheduling for an AI Receptionist

**Course:** INFO8665 — AI Receptionist  
**Authors:** Conestoga AIML Team  
**Date:** July 2026  
**Version:** 1.0

---

## Abstract

Missed appointments (no-shows) create idle capacity, lost revenue, and poor customer experience in service businesses such as salons, clinics, and dental offices. This paper describes an appointment prediction module integrated into the INFO8665 AI Receptionist platform. The system uses a **Random Forest classifier** trained on historical appointment records to estimate the probability that a client will not attend a scheduled visit. Features include patient age, lead time (waiting days), day-of-week, hour-of-day, and SMS reminder status. Beyond binary classification, the service recommends **low-risk time slots** by evaluating predicted no-show probability across candidate schedules and exposes REST APIs for prediction, smart booking, availability search, and at-risk client identification. On a held-out test set of 22,105 appointments, the model achieves **76.6% accuracy**, with precision of **35.1%** and recall of **19.3%** for the no-show class. While class imbalance limits recall, the approach provides actionable risk tiers for receptionist workflows and demonstrates how classical supervised learning can augment an intelligent front-desk system.

**Keywords:** appointment no-show prediction, random forest, smart scheduling, AI receptionist, healthcare analytics, salon booking

---

## 1. Introduction

Service businesses depend on reliable appointment attendance. Industry studies report no-show rates between **10% and 30%** depending on sector, geography, and reminder practices. For a salon or clinic operating on tight schedules, even a single empty chair per hour can materially reduce daily revenue.

Traditional receptionist workflows rely on manual judgment: staff may double-book high-risk slots, send extra reminders, or prefer certain days and times based on experience. These heuristics do not scale and are difficult to audit. Machine learning offers a data-driven alternative by learning patterns from historical bookings.

The AI Receptionist project targets small and medium businesses that need automated FAQ handling, client management, and appointment operations in one platform. The **appointment prediction module** extends this vision by:

1. Predicting no-show risk before a booking is confirmed.
2. Recommending appointment slots with lower predicted risk.
3. Flagging at-risk customers for proactive follow-up.
4. Supporting a **smart booking** flow that selects slots automatically when the client does not specify a time.

This paper documents the problem formulation, dataset, modeling pipeline, system integration, evaluation, and limitations of the implemented solution.

---

## 2. Problem Statement

Given a prospective or returning client and a candidate appointment context, the system must answer:

| Question | Output |
|----------|--------|
| How likely is this client to miss the appointment? | Probability in \([0, 1]\) |
| Which weekday and hour minimize no-show risk? | Preferred slot recommendation |
| Should staff treat this booking as low, medium, or high risk? | Categorical label |
| Which existing customers should receive confirmation calls? | At-risk list |

Formally, this is a **binary classification** problem:

\[
y \in \{0, 1\}, \quad \hat{p} = P(y=1 \mid \mathbf{x})
\]

where \(y = 1\) indicates a no-show and \(\mathbf{x}\) is a feature vector derived from appointment metadata.

The business objective is not only classification accuracy but **decision support**: receptionists and automated agents need interpretable risk bands and schedulable recommendations, not raw probabilities alone.

---

## 3. Related Work

No-show prediction has been studied extensively in healthcare operations research. Representative directions include:

- **Statistical and rule-based models** using lead time, demographics, and prior attendance history (Cayirli & Veral, 2003).
- **Machine learning classifiers** — logistic regression, decision trees, random forests, gradient boosting, and neural networks applied to hospital scheduling data (Khemani et al., 2018; Mohammadi et al., 2018).
- **Intervention design** — SMS reminders, overbooking policies, and confirmation workflows triggered by risk scores (Parikh et al., 2010).

Our implementation follows the pragmatic ML pipeline common in applied data science courses and Kaggle-style healthcare no-show competitions: tabular features, ensemble trees, and probability calibration for downstream rules. We intentionally use **Random Forest** for:

- Strong baseline performance on mixed numeric/categorical tabular data
- Minimal hyperparameter tuning for prototype deployment
- Native `predict_proba` support for slot scoring
- Interpretability via feature importance (future work)

The novelty in this project is **systems integration**: the classifier is not a standalone notebook experiment but a production FastAPI micro-feature consumed by the receptionist API and Next.js appointment dashboard.

---

## 4. Dataset

### 4.1 Source

Training data is derived from a public **medical appointment no-show** dataset widely used in ML education (Brazilian hospital/clinic records). The raw file is stored at:

```
data/raw/appointments.csv
```

After preprocessing:

```
data/processed/processed_appointments.csv
```

### 4.2 Scale and class distribution

| Statistic | Value |
|-----------|-------|
| Total records | 110,527 |
| No-show rate | 20.19% |
| Train/test split | 80% / 20% (`random_state=42`) |
| Test set size | 22,105 |

The dataset is **imbalanced**: roughly four attended appointments for every no-show. This affects precision/recall trade-offs and motivates risk-tier thresholds rather than a single 0.5 cutoff.

### 4.3 Raw attributes used

From the source file we retain:

| Field | Description |
|-------|-------------|
| `PatientId` | Anonymous customer identifier |
| `Age` | Client age |
| `ScheduledDay` | Date appointment was made |
| `AppointmentDay` | Date appointment is scheduled |
| `SMS_received` | Whether an SMS reminder was sent (0/1) |
| `No-show` | Target: `Yes` / `No` |

Gender and neighbourhood fields exist in the raw export but are excluded in the current pipeline to reduce sparsity and privacy surface area.

### 4.4 Engineered features

The preprocessing script (`app/services/preprocess_data.py`) derives:

| Feature | Definition |
|---------|------------|
| `WaitingDays` | `(AppointmentDay − ScheduledDay)` in days |
| `AppointmentWeekday` | Day of week of appointment (0=Monday … 6=Sunday) |
| `AppointmentHour` | Hour of appointment (0–23) |
| `No-show` | Binary target: 1 = no-show, 0 = attended |

Final modeling feature vector:

\[
\mathbf{x} = [\text{Age},\ \text{WaitingDays},\ \text{AppointmentWeekday},\ \text{AppointmentHour},\ \text{SMS\_received}]
\]

---

## 5. Methodology

### 5.1 Preprocessing pipeline

```
data/raw/appointments.csv
        │
        ▼  preprocess_data.py
        │  • parse dates
        │  • compute WaitingDays, weekday, hour
        │  • encode target
        ▼
data/processed/processed_appointments.csv
        │
        ▼  train_model.py
        │  • stratified random 80/20 split
        │  • fit RandomForestClassifier
        ▼
data/model/no_show_model.pkl
```

### 5.2 Model selection

We train a **Random Forest Classifier** (`sklearn.ensemble.RandomForestClassifier`) with default hyperparameters in the initial prototype:

```python
model = RandomForestClassifier()
model.fit(X_train, y_train)
joblib.dump(model, "data/model/no_show_model.pkl")
```

Random forests aggregate predictions from multiple decision trees trained on bootstrap samples, reducing variance compared to a single tree. For no-show data with nonlinear interactions (e.g., long wait + no SMS), ensembles typically outperform linear baselines without extensive feature engineering.

### 5.3 Inference

At runtime (`appointment_prediction_service.py`), the loaded model computes:

```python
risk = model.predict_proba([[age, waiting_days, weekday, hour, sms_received]])[0][1]
```

This value is the estimated **P(no-show)**.

### 5.4 Risk categorization

Probabilities are mapped to business labels:

| Risk score | Label | Suggested action |
|------------|-------|------------------|
| `< 0.30` | **Recommended** | Standard booking |
| `0.30 – 0.60` | **Medium Risk** | Confirmation SMS/call |
| `> 0.60` | **High Risk** | Require deposit or waitlist policy |

Thresholds are configurable constants in the service layer.

### 5.5 Slot recommendation algorithm

To recommend a low-risk slot, the service performs a **grid search** over:

- All weekdays (7 values)
- All hours (24 values)

For each \((\text{weekday}, \text{hour})\) pair it computes predicted risk holding `age`, `waiting_days`, and `sms_received` fixed, then selects the minimum:

```
best_slot = argmin_{w,h} P(no-show | age, waiting_days, w, h, sms)
```

The winning slot is formatted for API consumers (`"Tuesday"`, `"10:00 AM"`). This brute-force search is acceptable at inference time because the model evaluates only \(7 \times 24 = 168\) candidates per request.

For returning customers, historical medians/modes populate `age`, `waiting_days`, and `sms_received` when available.

---

## 6. System Architecture

The prediction module is embedded in the FastAPI backend and consumed by the Next.js appointment UI.

```
┌─────────────────────┐     ┌──────────────────────────────┐
│  Next.js Frontend   │     │  FastAPI AI Receptionist     │
│  /appointments      │────▶│  /api/appointments/predict   │
│  AI Slot Advisor    │     │  /api/appointments/at-risk   │
│  At-Risk panel      │     │  /api/appointments/smart-book│
└─────────────────────┘     └──────────────┬───────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │ appointment_prediction_service│
                              │  • load no_show_model.pkl    │
                              │  • predict_proba             │
                              │  • slot search               │
                              └──────────────────────────────┘
```

### 6.1 API endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/appointments/predict` | POST | Risk + preferred slot from demographics |
| `/api/appointments/customers/{id}/history/` | GET | Recent appointment rows |
| `/api/appointments/customers/{id}/preferences/` | GET | Historical mode weekday/hour + risk |
| `/api/appointments/availability/` | GET | Business-hours slot grid |
| `/api/appointments/conflicts/check/` | GET | Simple conflict detection |
| `/api/appointments/smart-book/` | POST | Auto-select slot + book |
| `/api/appointments/at-risk/` | GET | Customers with risk ≥ 0.5 |

All endpoints require JWT authentication (`POST /auth/token`).

### 6.2 Frontend integration

The appointment dashboard (`frontend/src/app/appointments`) includes:

- **AI Slot Advisor** — form for age, waiting days, SMS flag → live prediction
- **At-Risk Clients** — sidebar list from `/at-risk/`
- **Schedule management** — CRUD appointments via `/api/appointments/` (SQLite)

> **Note:** CRUD appointments (salon `clients` / `services` tables) and ML prediction (CSV-backed `customer_id`) currently use parallel data models. Unifying them is identified as future integration work.

---

## 7. Evaluation

### 7.1 Experimental setup

- **Split:** 80% train / 20% test, `random_state=42`
- **Metrics:** accuracy, precision, recall, F1 (positive class = no-show)
- **Script:** `app/services/evaluate_model.py`

### 7.2 Results

| Metric | Value |
|--------|-------|
| Accuracy | **0.7664** |
| Precision (no-show) | **0.3509** |
| Recall (no-show) | **0.1931** |
| F1 (no-show) | **0.2492** |

### 7.3 Interpretation

- **Accuracy (~77%)** exceeds a naive majority-class baseline (~80% attended → 80% accuracy if always predicting "attended"), but is only marginally informative under imbalance.
- **Low recall (19%)** means the model misses many actual no-shows. For a screening tool that triggers extra reminders, false negatives are costly.
- **Moderate precision (35%)** means flagged no-shows are still more likely than random, but many alerts will be false positives.

These results are typical for imbalanced healthcare no-show problems without class weighting, SMOTE, or threshold tuning. The deployed system mitigates this by using **probability bands** rather than hard binary alerts for every booking.

### 7.4 Recommended improvements

1. `class_weight='balanced'` or scale_pos_weight in tree models
2. Optimize threshold on validation data for business cost (false alarm vs missed no-show)
3. Add features: prior no-show count, service type, distance, weather
4. Report ROC-AUC and calibration plots
5. Cross-validation with temporal splits (train on past, test on future)

---

## 8. Discussion

### 8.1 Business value

Even with imperfect recall, the module supports:

- **Risk-aware scheduling** — prefer slots with lower modeled risk
- **Staff prioritization** — at-risk panel focuses confirmation effort
- **Customer experience** — smart booking suggests times aligned with attendance patterns
- **Demonstration of AI receptionist capabilities** — bridges FAQ chatbot and operations

### 8.2 Ethical considerations

- **Fairness:** Age is a sensitive attribute; deployment in regulated settings requires bias analysis across demographic groups.
- **Transparency:** Clients should know when automated risk scores influence booking policies.
- **Human override:** Predictions should assist, not replace, receptionist judgment.

### 8.3 Limitations

1. **Domain shift:** Model trained on medical appointments; salon behavior may differ.
2. **Feature sparsity:** Five features omit rich behavioural history.
3. **Data plumbing:** Prediction `customer_id` ≠ SQLite `client_id` without ETL.
4. **Smart-book store:** In-memory bookings do not persist across server restarts.
5. **Model size:** Serialized forest artifact is large (~173 MB); consider model compression or lighter algorithms for edge deployment.
6. **sklearn version drift:** Model pickle version warnings indicate retraining may be needed after environment upgrades.

---

## 9. Future Work

| Priority | Enhancement |
|----------|-------------|
| High | Merge ML pipeline with SQLite `appointments` and `clients` tables |
| High | Retrain with `class_weight='balanced'` and report ROC-AUC |
| Medium | Persist smart bookings; conflict check against real schedule |
| Medium | Personalize with per-client no-show history features |
| Medium | A/B test reminder policies triggered by risk tier |
| Low | SHAP/feature importance dashboard in Streamlit GUI |
| Low | Deep learning or gradient boosting benchmark (XGBoost, LightGBM) |

---

## 10. Conclusion

We presented an appointment no-show prediction subsystem for the INFO8665 AI Receptionist, combining Random Forest classification with a slot search recommender and RESTful APIs. Trained on 110,527 historical records, the model achieves 76.6% accuracy and enables risk-stratified scheduling workflows in the web UI. While recall on the minority no-show class remains modest, the architecture demonstrates a complete path from raw CSV → trained artifact → inference service → receptionist dashboard. Continued work on class imbalance, feature enrichment, and unified data storage will move the module from academic prototype toward production-ready salon and clinic operations.

---

## References

1. Cayirli, T., & Veral, E. (2003). Outpatient scheduling in health care: A review of literature. *Production and Operations Management*, 12(4), 519–549.

2. Khemani, A., et al. (2018). Predicting medical appointment no-shows using machine learning. *Healthcare Informatics Research*.

3. Mohammadi, A., et al. (2018). Data-driven predictive models for hospital readmission and no-show. *BMC Medical Informatics and Decision Making*.

4. Parikh, A., et al. (2010). Estimating risk of appointment non-attendance. *American Journal of Medicine*.

5. Scikit-learn Developers. (2024). *RandomForestClassifier* — scikit-learn documentation. https://scikit-learn.org/

6. Kaggle. *Medical Appointment No Shows* dataset. https://www.kaggle.com/datasets/joniarroba/noshowappointments

7. FastAPI. (2024). *FastAPI framework documentation*. https://fastapi.tiangolo.com/

---

## Appendix A — Reproducibility

### Train the model

```bash
python app/services/preprocess_data.py
python app/services/train_model.py
python app/services/evaluate_model.py
```

### Run prediction API

```bash
uvicorn app.main:app --reload
```

Example request:

```bash
curl -X POST "http://localhost:8000/api/appointments/predict" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"age": 62, "waiting_days": 5, "sms_received": 0}'
```

Example response:

```json
{
  "preferred_hour": "10:00 AM",
  "preferred_weekday": "Tuesday",
  "no_show_risk": 0.06,
  "recommendation": "Recommended"
}
```

### Project file map

| File | Role |
|------|------|
| `app/services/preprocess_data.py` | Feature engineering |
| `app/services/train_model.py` | Model training |
| `app/services/evaluate_model.py` | Hold-out metrics |
| `app/services/appointment_prediction_service.py` | Inference + scheduling logic |
| `app/routers/appointment_prediction.py` | REST routes |
| `data/model/no_show_model.pkl` | Trained artifact |
| `frontend/src/components/appointments/PredictionPanel.tsx` | UI demo |

---

*End of document*
