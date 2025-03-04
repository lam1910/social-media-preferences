
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Union, List, Dict
from database import SessionLocal, Prediction

app = FastAPI()

# Dependency to get a database session
def get_db():
    """
    Provides a database session for each request.
    Closes the session after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the request model
class PredictionRequest(BaseModel):
    features: Union[Dict[str, float], List[Dict[str, float]]]
    """
    Accepts either:
    - A single set of features (dictionary)
    - A list of feature sets (list of dictionaries)
    """

# Define the response model
class PredictionResponse(BaseModel):
    
    features: Dict[str, float]
    prediction: float
    
    """
    Represents the structure of the response returned after making a prediction.
    """

# Prediction endpoint
@app.post("/predict", response_model=Union[PredictionResponse, List[PredictionResponse]])
def predict(request: PredictionRequest):
    """
    Handles POST requests to /predict.
    Processes input features to generate predictions.
    Supports both single and multiple predictions.
    """
    # Normalize the input to a list of feature dictionaries
    if isinstance(request.features, dict):
        feature_sets = [request.features]
    elif isinstance(request.features, list) and all(isinstance(f, dict) for f in request.features):
        feature_sets = request.features
    else:
        raise HTTPException(status_code=400, detail="Invalid format for 'features'. Must be a dict or list of dicts.")



