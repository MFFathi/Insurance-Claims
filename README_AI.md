# MLModel - Insurance Claims ML Module

This directory contains the machine learning components of the Insurance Claims Processing System, focusing on KNN regression models for settlement value prediction.

## Overview

The MLModel directory contains:
- Jupyter notebooks for data analysis and model development
- Python scripts for model training and evaluation
- Trained model files (.pkl)
- Utilities for model management

## Key Components

### Notebooks
- `KNN_Settlement_Training.ipynb`: Trains KNN regression models for settlement value prediction
- `improved_preprocessing.ipynb`: Data preprocessing and feature engineering
- `model_checker.ipynb`: Validates model performance
- `first_iter.ipynb`: Initial model exploration with Random Forest

### Scripts
- `create_notebook.py`: Generates analysis notebooks programmatically
- `trainer.py`: Command-line model training utility
- `ml_module.py`: Core ML implementation with scikit-learn integration

## Getting Started

### Prerequisites
- Python 3.8+
- scikit-learn 1.4.2
- pandas 2.2.2
- Jupyter Notebook/Lab

### Setup

1. Ensure you're in the project's virtual environment:
```bash
source ../venv/bin/activate  # On Windows: ..\venv\Scripts\activate
```

2. Install required dependencies:
```bash
pip install -r ../requirements.txt
```

### Training Models

Run the trainer script to create a new model:
```bash
python trainer.py
```

This will:
- Load and preprocess the claims data
- Train a KNN regression model
- Save the model as a pickle file with version information

### Using Notebooks

To explore the data and model development process:
```bash
jupyter notebook
```

Key notebooks to review:
- `improved_preprocessing.ipynb` - For data preparation
- `KNN_Settlement_Training.ipynb` - For model training details

### Model Evaluation

To check model performance:
```bash
python -c "import pickle; model = pickle.load(open('knn_model_0.4.pkl', 'rb')); print(f'Model loaded: {model}')"
```

## Integration with Django

Models trained in this directory can be uploaded through the web interface by AI Engineers at:
`/ml/models/upload/`

The system supports multiple model versions (0.1 to 0.4) for A/B testing and performance comparison.

## Model Features

The KNN models predict:
- Settlement values based on claim details
- Processing time estimation
- Risk assessment

## Troubleshooting

If you encounter issues:
1. Verify data files exist in the expected location
2. Check model version compatibility
3. Ensure scikit-learn version matches requirements (1.4.2)
4. Review model parameters in `ml_module.py`