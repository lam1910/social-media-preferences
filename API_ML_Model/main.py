from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Union, List, Dict
from datetime import datetime
from database import SessionLocal, Prediction

app = FastAPI()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the request model
class PredictionRequest(BaseModel):
    features: Union[Dict[str, float], List[Dict[str, float]]]

# Define the response model
class PredictionResponse(BaseModel):
    features: Dict[str, float]
    prediction: float

# Placeholder for the machine learning model
def dummy_model(features: Dict[str, float]) -> float:
    return sum(features.values()) * 0.5  # Example computation

# Prediction endpoint
@app.post("/predict", response_model=Union[PredictionResponse, List[PredictionResponse]])
def predict(request: PredictionRequest, db: Session = Depends(get_db)):
    # Normalize the input to a list of feature dictionaries
    if isinstance(request.features, dict):
        feature_sets = [request.features]
    elif isinstance(request.features, list) and all(isinstance(f, dict) for f in request.features):
        feature_sets = request.features
    else:
        raise HTTPException(status_code=400, detail="Invalid format for 'features'. Must be a dict or list of dicts.")

    predictions = []

    for feature_set in feature_sets:
        prediction_value = dummy_model(feature_set)

        # Create a new Prediction instance for the database
        db_prediction = Prediction(
            features=feature_set,
            prediction=prediction_value
        )
        db.add(db_prediction)  # Add to the session
        predictions.append(db_prediction)  # Collect for later use

    db.commit()  # Commit all changes to the database

    for db_prediction in predictions:
        db.refresh(db_prediction)

    # Return the appropriate response
    if len(predictions) == 1:
        return predictions[0]  # Single prediction response
    else:
        return predictions  # List of predictions response

# Endpoint to retrieve past predictions
@app.get("/past-predictions", response_model=List[PredictionResponse])
def get_past_predictions(db: Session = Depends(get_db)):
    return db.query(Prediction).all()
