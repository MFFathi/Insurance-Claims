import pickle
import pandas as pd

def validate_pkl(path):
    try:
        with open(path, 'rb') as f:
            bundle = pickle.load(f)

        print(f"✅ Loaded bundle from {path}")
        print(f"📦 Keys found:", bundle.keys())

        # --- Check model ---
        if "ml" not in bundle:
            print("❌ 'ml' key missing!")
            return
        else:
            print("✅ Model exists.")

        # --- Check feature_names ---
        feature_names = bundle.get("feature_names")
        if not feature_names or not isinstance(feature_names, list):
            print("❌ feature_names missing or not list!")
            return
        print(f"✅ feature_names: {len(feature_names)} features")

        # --- Check X_min and denom ---
        X_min = bundle.get("X_min")
        denom = bundle.get("denom")

        X_min_series = pd.Series(X_min)
        denom_series = pd.Series(denom)

        if not all(X_min_series.apply(lambda x: isinstance(x, (int, float)))):
            print("❌ X_min contains non-floats!")
            print(X_min_series.dtypes)
            return

        if not all(denom_series.apply(lambda x: isinstance(x, (int, float)))):
            print("❌ denom contains non-floats!")
            print(denom_series.dtypes)
            return

        print("✅ X_min and denom all floats.")

        # --- Check category mappings ---
        category_mappings = bundle.get("category_mappings")
        if not isinstance(category_mappings, dict):
            print("❌ category_mappings missing or invalid!")
            return
        print("✅ category_mappings present.")

        print("🎯 All checks passed. Your .pkl is good!")

    except Exception as e:
        print(f"❌ Error validating .pkl: {e}")

# --- Run ---
if __name__ == "__main__":
    path_to_check = "/Users/bearcheung/Documents/Year3/AAI/Project/Insurance-Claims/knn_model_bundle_3.pkl"  # Update path if needed
    validate_pkl(path_to_check)
