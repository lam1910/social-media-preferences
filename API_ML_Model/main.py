import os
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Union, List
from database import SessionLocal, Prediction

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

    predictions = []

    for raw_features in raw_feature_sets:
        print("Raw features received:", raw_features)
        # Validate that all required raw features are present.
        for key in RAW_FEATURES:
            if key not in raw_features:
                raise HTTPException(status_code=400, detail=f"Missing raw feature: {key}")

        final_features = {}
        frequencies = ['basketball',
    'football', 'soccer', 'softball', 'volleyball', 'swimming', 'cheerleading',
    'baseball', 'tennis', 'sports', 'cute', 'sex', 'sexy', 'hot', 'kissed',
    'dance', 'band', 'marching', 'music', 'rock', 'god', 'church', 'jesus',
    'bible', 'hair', 'dress', 'blonde', 'mall', 'shopping', 'clothes',
    'hollister', 'abercrombie', 'die', 'death', 'drunk', 'drugs']
        singulier  = ["gradyear","age", "NumberOffriends","basketball"]

        # Filter the raw features for the relevant keys in 'frequencies'
        filtered_raw_features = {key: raw_features[key] for key in frequencies if key in raw_features}
        singulier_raw_features = {key: raw_features[key] for key in singulier if key in raw_features}

        print("Filtered raw features:", filtered_raw_features)

        # --- Process Gender ---
        raw_gender = raw_features["gender"]
        print("Processing gender value:", raw_gender)
        try:
            gender_features = process_gender(raw_gender)
            final_features.update(gender_features)
        except Exception as ge:
            raise HTTPException(status_code=400, detail=f"Error processing gender: {str(ge)}")

        # --- Process Remaining Features ---
        for col in singulier_raw_features:
            print(f"Processing feature: {col}, Raw Value: {raw_features[col]}")

            raw_value = singulier_raw_features[col]
            print(f"Processing feature: {col}, Raw Value: {singulier_raw_features}, Type: {type(raw_value)}")

            # Process 'gradyear' with scaling
            if col == "gradyear":
                transformed_value = mms.transform([[raw_value]])
                print(f"Scaled gradyear output (Type: {type(transformed_value)}):", transformed_value)
                # Ensure it's an array before accessing elements
                transformed_value = transformed_value.to_numpy().flatten()[0]
                final_features[col] = float(transformed_value)
                print(final_features)

            elif col in ["age", "NumberOffriends"]:
                final_features[col] = float(raw_value)
                print(f"Floated value {col} output (Type: {type(final_features[col])}):", final_features[col])
                print(final_features)    

            
            elif col == "basketball":
                print(filtered_raw_features)
                # For other features that need to be scaled using `sts`
                try:
                    # Here we extract the numeric features for scaling
                    numeric_features = list(filtered_raw_features.values())  # Get feature values as a list
                    print(f"Numeric features for scaling: {numeric_features}")
                    
                    transformed_value = sts.transform([numeric_features])  # Transform the values
                    print(f"Transformed {col} values: {transformed_value}")

                    # Convert the DataFrame to a NumPy array and flatten it
                    transformed_value_array = transformed_value.to_numpy().flatten()  # Convert to array and flatten
                    
                    # Loop through the transformed values and add them to final_features with proper column names
                    for i, col_name in enumerate(filtered_raw_features.keys()):
                        final_features[col_name] = float(transformed_value_array[i])
                        print(f"Scaled {col_name} value:", transformed_value_array[i])
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error during scaling: {str(e)}")


        # --- Build Final Feature Vector ---
        vector_parts = []
        for col in ORDER_OF_FEATURE_INPUT:
            if col not in final_features:
                raise HTTPException(status_code=400, detail=f"Missing processed feature: {col}")
            vector_parts.append(np.array([[final_features[col]]]))

        try:
            feature_vector = np.hstack(vector_parts)
            print("Final feature vector constructed:", feature_vector)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error concatenating feature vector: {str(e)}")

        # --- Make the Prediction ---
        try:
            cluster_pred = kmeans.predict(feature_vector)
            print("Cluster prediction output:", cluster_pred)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")

        prediction_value = float(cluster_pred[0])
        print("Final prediction value:", prediction_value)

        # --- Save the Prediction to the Database ---
        db_prediction = Prediction(
            features=raw_features,  # or use final_features if you wish to store processed values
            prediction=prediction_value
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        predictions.append(db_prediction)

    if len(predictions) == 1:
        return predictions[0]
    else:
        return predictions

# --- PAST PREDICTIONS ENDPOINT ---
@app.get("/past-predictions", response_model=List[PredictionResponse])
def get_past_predictions(db: Session = Depends(get_db)):
    return db.query(Prediction).all()
