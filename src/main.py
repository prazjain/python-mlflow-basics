import mlflow

from mlflow.models import infer_signature

import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import argparse

parser=argparse.ArgumentParser()
parser.add_argument("--mode", choices=['local', 'dagshub', 'aws'])
args=parser.parse_args()

# Load the Iris dataset
X, y = datasets.load_iris(return_X_y=True)

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Define the model hyperparameters
params = {
    "solver": "lbfgs",
    "max_iter": 1000,
    "multi_class": "auto",
    "random_state": 8888,
}

# Train the model
lr = LogisticRegression(**params)
lr.fit(X_train, y_train)

# Predict on the test set
y_pred = lr.predict(X_test)

# Calculate metrics
accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(y_test, y_pred, average='micro')

recall = recall_score(y_test, y_pred, average='micro')

f1 = f1_score(y_test, y_pred, average='micro')

url = ''
if args.mode == 'local':
    url = "http://127.0.0.1:8080"
elif args.mode == 'dagshub':
    url = 'https://dagshub.com/prazjain/python-mlflow-basics.mlflow'
elif args.mode == 'aws':
    url = 'http://ec2-54-87-42-139.compute-1.amazonaws.com:5000/'

# Set our tracking server uri for logging
mlflow.set_tracking_uri(uri=url)

# Create a new MLflow Experiment
mlflow.set_experiment("MLflow IRIS Data experiment")

# Start an MLflow run
with mlflow.start_run():
    # Log the hyperparameters
    mlflow.log_params(params)

    # Log the loss metric
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1", f1)

    # Set a tag that we can use to remind ourselves what this run was for
    mlflow.set_tag("Training Info", "Basic LR model for iris data")

    # Infer the model signature
    signature = infer_signature(X_train, lr.predict(X_train))

    # Log the model
    model_info = mlflow.sklearn.log_model(
        sk_model=lr,
        artifact_path="iris_model",
        signature=signature,
        input_example=X_train,
        registered_model_name="tracking-quickstart",
    )
