import pickle
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV, cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from collections import Counter
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from scipy.stats import randint
import argparse

# --- Command-line arguments ---
parser = argparse.ArgumentParser(description="Train sign language classifier.")
parser.add_argument("--data_file", type=str, default='data.pickle', help="Path to the data.pickle file.")
parser.add_argument("--sequence_length", type=int, default=10, help="Sequence length for dynamic signs.")
parser.add_argument("--num_static_classes", type=int, default=24, help="Number of static classes")
args = parser.parse_args()

# --- Load data and check shapes ---
data_dict = pickle.load(open(args.data_file, 'rb'))

# --- Check shapes and enforce consistency ---
expected_static_len = 42
expected_dynamic_len = args.sequence_length * expected_static_len
data = []
labels = []
static_count = 0
dynamic_count= 0

for i, (item, label) in enumerate(zip(data_dict['data'], data_dict['labels'])):
    item_len = len(item)
    if int(label) < args.num_static_classes:  # Static sign
        if item_len != expected_static_len:
            print(f"Warning: Item {i} (static) has unexpected length {item_len}. Expected {expected_static_len}. Skipping.")
            continue
        data.append(item)
        labels.append(label)
        static_count +=1
    else:  # Dynamic sign
        if item_len != expected_dynamic_len:
            print(f"Warning: Item {i} (dynamic) has unexpected length {item_len}. Expected {expected_dynamic_len}. Skipping.")
            continue
        data.append(item)
        labels.append(label)
        dynamic_count+= 1

print(f"Loaded {static_count} Static and {dynamic_count} Dynamic samples")


# --- DETAILED TYPE AND SHAPE CHECK ---
for i, item in enumerate(data):
    if not isinstance(item, list):
        print(f"Error: Item {i} is not a list! Type: {type(item)}")
    else:
        if len(item) != expected_static_len and len(item) != expected_dynamic_len:
            print(f"Error, item {i}, length = {len(item)}")
# --- END DETAILED CHECK ---

data = np.asarray(data)  # This is where the error occurs
labels = np.asarray(labels)

# --- Rest of your training code ---
# (The rest of your train_classifier.py code remains the same)
# Check class distribution
class_counts = Counter(labels)
print("Class counts:", class_counts)

# Check for and handle NaN or infinite values
if np.any(np.isnan(data)) or np.any(np.isinf(data)):
    print("Warning: NaN or Inf values found in data.  Replacing with 0.")
    data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)


x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=labels)

# --- Option 1: RandomForest with Hyperparameter Tuning and SMOTE ---
smote = SMOTE(random_state=42)
param_dist_rf = {
    'model__n_estimators': randint(50, 200),
    'model__max_depth': [5, 10, 15, 20, None],
    'model__min_samples_split': randint(2, 11),
    'model__min_samples_leaf': randint(1, 5),
    'model__class_weight': ['balanced', 'balanced_subsample', None]
}
pipeline_rf = ImbPipeline([
    ('smote', smote),
    ('model', RandomForestClassifier(random_state=42))
])
random_search_rf = RandomizedSearchCV(pipeline_rf,
                                    param_distributions=param_dist_rf,
                                    n_iter=20,
                                    cv=5,
                                    verbose=2,
                                    n_jobs=-1,
                                    random_state=42)

random_search_rf.fit(x_train, y_train)
print("Best parameters (RandomForest):", random_search_rf.best_params_)
best_model_rf = random_search_rf.best_estimator_
y_predict_rf = best_model_rf.predict(x_test)
score_rf = accuracy_score(y_predict_rf, y_test)
print(f'RandomForest Accuracy: {score_rf * 100:.2f}%')


# --- Option 2: XGBoost with Hyperparameter Tuning and SMOTE ---
param_dist_xgb = {
    'model__n_estimators': randint(50, 200),
    'model__max_depth': randint(3, 11),
    'model__learning_rate': [0.01, 0.1, 0.2, 0.3],
    'model__subsample': [0.7, 0.8, 0.9, 1.0],
    'model__colsample_bytree': [0.7, 0.8, 0.9, 1.0],
    'model__gamma': [0, 0.1, 0.2, 0.3],
    # 'model__scale_pos_weight': ...  # Optional, for imbalanced data
}

pipeline_xgb = ImbPipeline([
    ('smote', SMOTE(random_state=42)),
    ('model', xgb.XGBClassifier(objective='multi:softmax',
                                  num_class=len(set(labels)),
                                  random_state=42,
                                  use_label_encoder=False,
                                  eval_metric='mlogloss'))
])
random_search_xgb = RandomizedSearchCV(pipeline_xgb,
                                     param_distributions=param_dist_xgb,
                                     n_iter=20,
                                     cv=5,
                                     verbose=2,
                                     n_jobs=-1,
                                     random_state=42)

random_search_xgb.fit(x_train, y_train)
print("Best parameters (XGBoost):", random_search_xgb.best_params_)
best_model_xgb = random_search_xgb.best_estimator_
y_predict_xgb = best_model_xgb.predict(x_test)
score_xgb = accuracy_score(y_predict_xgb, y_test)
print(f'XGBoost Accuracy: {score_xgb * 100:.2f}%')


# --- Cross-Validation (Example with XGBoost) ---
cv_scores = cross_val_score(best_model_xgb, data, labels, cv=5)
print("Cross-validation scores:", cv_scores)
print("Mean cross-validation score:", cv_scores.mean())

# --- Choose and Save the Best Model ---
if score_xgb > score_rf:
    best_model = best_model_xgb
    model_filename = 'best_model_xgb.p'
    print("XGBoost is the better model.")
else:
    best_model = best_model_rf
    model_filename = 'best_model_rf.p'
    print("RandomForest is the better model.")


with open(model_filename, 'wb') as f:
    pickle.dump({'model': best_model}, f)

print(f"Best model saved to {model_filename}")