
from typing import Union, List, Dict
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import session
from fastapi import HTTPException



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
    id: int
    features: Dict[str, float]
    prediction: float
    timestamp: datetime
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
