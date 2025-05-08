import pickle
from pprint import pprint

def load_model(model_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
        print(f"\nModel from {model_path}:")
        print(f"Type: {type(model)}")
        if isinstance(model, dict):
            print("Keys:", model.keys())
            for key in model.keys():
                print(f"\nValue type for key '{key}': {type(model[key])}")
                if key == 'ml' and hasattr(model[key], 'models'):
                    print("Available model names:", model[key].models.keys())
                elif key == 'feature_names':
                    print("Expected features:", model[key])
                elif key == 'model':
                    print("Model type:", type(model[key]))
                    if hasattr(model[key], 'named_steps'):
                        print("Pipeline steps:", model[key].named_steps.keys())
        return model

# Load both models
print("\nInspecting Random Forest model:")
rf_model = load_model('MLModel/insurance_model.pkl')
print("\nInspecting KNN model:")
knn_model = load_model('MLModel/knn_model_bundle_15.pkl') 