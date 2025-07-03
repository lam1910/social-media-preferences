import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Union, List
from database import SessionLocal, Prediction
from datetime import datetime

app = FastAPI()

# --- GLOBAL SETTINGS & MODEL LOADING ---

# Build the absolute path for the model directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "model-binary")
print("Absolute MODEL_PATH:", MODEL_PATH)
print("Files in MODEL_PATH:", os.listdir(MODEL_PATH))


# Load the pickled objects.
ohe = joblib.load(os.path.join(MODEL_PATH, 'gender-encoder.pkl'))
mms = joblib.load(os.path.join(MODEL_PATH, 'gradyear-scaler.pkl'))
sts = joblib.load(os.path.join(MODEL_PATH, 'keyword-frequency-scaler.pkl'))
kmeans = joblib.load(os.path.join(MODEL_PATH, 'model-social-media-kmeans.pkl'))

# Debug prints for OneHotEncoder
print("Categories:", ohe.categories_)
print("Transformed 'M':", ohe.transform(pd.DataFrame({"gender": ["M"]})).to_numpy())

# --- EXPECTED FEATURES ---

# List of raw feature keys (the payload must contain all these keys).
RAW_FEATURES = [
    "gradyear", "age", "NumberOffriends", "basketball",
    "football", "soccer", "softball", "volleyball", "swimming", "cheerleading",
    "baseball", "tennis", "sports", "cute", "sex", "sexy", "hot", "kissed",
    "dance", "band", "marching", "music", "rock", "god", "church", "jesus",
    "bible", "hair", "dress", "blonde", "mall", "shopping", "clothes",
    "hollister", "abercrombie", "die", "death", "drunk", "drugs", "gender"
]

# This ordered list is what your model expects.
ORDER_OF_FEATURE_INPUT = [
    'gradyear', 'age', 'NumberOffriends',  'basketball',
    'football', 'soccer', 'softball', 'volleyball', 'swimming', 'cheerleading',
    'baseball', 'tennis', 'sports', 'cute', 'sex', 'sexy', 'hot', 'kissed',
    'dance', 'band', 'marching', 'music', 'rock', 'god', 'church', 'jesus',
    'bible', 'hair', 'dress', 'blonde', 'mall', 'shopping', 'clothes',
    'hollister', 'abercrombie', 'die', 'death', 'drunk', 'drugs',
    'gender_F', 'gender_M', 'gender_NA'
]

# --- DEPENDENCY: Database Session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# # Define the request model.
# The "features" can be a dict (single instance) or a list of dicts.
class PredictionRequest(BaseModel):
    features: Union[
        Dict[str, Union[float, int, str]], 
        List[Dict[str, Union[float, int, str]]]
    ]

# Define the response model.
class PredictionResponse(BaseModel):
    features: Dict[str, Union[float, int, str]]
    insertion_timestamp: datetime
    prediction: float

# --- HELPER FUNCTION FOR PROCESSING GENDER ---
def process_gender(raw_gender: Union[str, int]) -> Dict[str, float]:
    """
    Processes the raw gender value and returns a dictionary with keys:
    'gender_F', 'gender_M', 'gender_NA'.
    Debug prints are added at each step.
    """
    try:
        print("Step 1: Creating DataFrame for gender with value:", raw_gender)
        gender_df = pd.DataFrame({"gender": [raw_gender]})
        print("Gender DataFrame:", gender_df)
    except Exception as e:
        raise Exception(f"Error creating DataFrame: {e}")
    
    try:
        print("Step 2: Transforming DataFrame with OneHotEncoder.")
        gender_encoded = ohe.transform(gender_df)
        print("After transform, raw output:", gender_encoded)
    except Exception as e:
        raise Exception(f"Error during transform: {e}")
    
    try:
        print("Step 3: Converting transformation result to numpy array.")
        if hasattr(gender_encoded, "toarray"):
            gender_encoded = gender_encoded.toarray()
            print("Used toarray() ->", gender_encoded)
        else:
            gender_encoded = gender_encoded.to_numpy()
            print("Used to_numpy() ->", gender_encoded)
    except Exception as e:
        raise Exception(f"Error converting to numpy array: {e}")
    
    try:
        print("Step 4: Extracting encoded gender values.")
        gender_cols = ['gender_F', 'gender_M', 'gender_NA']
        gender_features = {}
        for idx, col in enumerate(gender_cols):
            gender_features[col] = float(gender_encoded[0][idx])
        print("Gender features extracted:", gender_features)
        return gender_features
    except Exception as e:
        raise Exception(f"Error processing gender features: {e}")

# --- PREDICTION ENDPOINT ---
@app.post("/predict", response_model=Union[PredictionResponse, List[PredictionResponse]])
def predict(request: PredictionRequest, db: Session = Depends(get_db)):
    # Wrap the single dictionary into a list.
    if isinstance(request.features, dict):
        raw_feature_sets = [request.features]
    elif isinstance(request.features, list) and all(isinstance(f, dict) for f in request.features):
        raw_feature_sets = request.features
    else:
        raise HTTPException(status_code=400, detail="Invalid format for feature input; must be a dict.")

    predictions = []  # This will now store Prediction objects to be bulk inserted.

    for raw_features in raw_feature_sets:
        print("Raw features received:", raw_features)
        # Validate that all required raw features are present.
        for key in RAW_FEATURES:
            if key not in raw_features:
                raise HTTPException(status_code=400, detail=f"Missing raw feature: {key}")

        final_features = {}
        frequencies = [
            'basketball', 'football', 'soccer', 'softball', 'volleyball', 'swimming', 'cheerleading',
            'baseball', 'tennis', 'sports', 'cute', 'sex', 'sexy', 'hot', 'kissed',
            'dance', 'band', 'marching', 'music', 'rock', 'god', 'church', 'jesus',
            'bible', 'hair', 'dress', 'blonde', 'mall', 'shopping', 'clothes',
            'hollister', 'abercrombie', 'die', 'death', 'drunk', 'drugs'
        ]
        singulier = ["gradyear", "age", "NumberOffriends", "basketball"]

        # Filter features
        filtered_raw_features = {key: raw_features[key] for key in frequencies if key in raw_features}
        singulier_raw_features = {key: raw_features[key] for key in singulier if key in raw_features}

        # Process gender
        raw_gender = raw_features["gender"]
        gender_features = process_gender(raw_gender)
        final_features.update(gender_features)

        # Process remaining features
        for col in singulier_raw_features:
            raw_value = singulier_raw_features[col]

            if col == "gradyear":
                transformed_value = mms.transform([[raw_value]])
                transformed_value = transformed_value.to_numpy().flatten()[0]
                final_features[col] = float(transformed_value)

            elif col in ["age", "NumberOffriends"]:
                final_features[col] = float(raw_value)

            elif col == "basketball":
                numeric_features = list(filtered_raw_features.values())
                transformed_value = sts.transform([numeric_features])
                transformed_value_array = transformed_value.to_numpy().flatten()
                for i, col_name in enumerate(filtered_raw_features.keys()):
                    final_features[col_name] = float(transformed_value_array[i])

        # Build final feature vector
        vector_parts = []
        for col in ORDER_OF_FEATURE_INPUT:
            if col not in final_features:
                raise HTTPException(status_code=400, detail=f"Missing processed feature: {col}")
            vector_parts.append(np.array([[final_features[col]]]))

        feature_vector = np.hstack(vector_parts)
        cluster_pred = kmeans.predict(feature_vector)
        prediction_value = float(cluster_pred[0])

        # Create Prediction object (do NOT commit yet)
        db_prediction = Prediction(
            features=raw_features,
            prediction=prediction_value
        )
        predictions.append(db_prediction)  # Append to the list for batch save

    # --- NEW: Save all predictions at once ---
    db.add_all(predictions)   # Add all objects in one call
    db.commit()               # Single commit for all inserts
    for p in predictions:     # Refresh each object so IDs etc. are populated
        db.refresh(p)

    # --- Return response ---
    if len(predictions) == 1:
        return predictions[0]
    else:
        return predictions


# --- PAST PREDICTIONS ENDPOINT ---
@app.get("/past-predictions", response_model=List[PredictionResponse])
def get_past_predictions(db: Session = Depends(get_db)):
    return db.query(Prediction).all()
