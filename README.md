# INFO8665 AI Receptionist

## Project Structure

```
info8665-ai-receptionist/
├── README.md
├── orchestrator.ipynb       # Main orchestrator notebook
├── data-collection/         # Raw datasets and database files
├── training/                # Trained model artifacts
│   └── trained-model-v0.h5
├── dev/                     # Execution scripts
│   └── dev-run-v0.py
└── documentation/           # Project documentation
```

## How It Works

1. `orchestrator.ipynb` reads datasets from the `data-collection/` folder and/or database.
2. The orchestrator trains the model and saves intermediate files (trained models, configs) to `training/`.
3. The orchestrator calls execution scripts stored in the `dev/` folder.
