# train_model.py
# Trains your classifier on the labeled data
# Saves the model to disk — reuse forever

import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils import resample


def build_balanced_dataset(df):
    extra_examples = pd.DataFrame([
        {"text": "Oil tanker attacks in the Strait of Hormuz raise supply fears and push up petro prices", "label": "BAD"},
        {"text": "India signs a new oil import deal with Saudi Arabia to boost supply security", "label": "GOOD"},
        {"text": "A football match in Mumbai drew a large crowd and had no energy impact", "label": "NEUTRAL"},
        {"text": "A refinery shutdown threatens fuel availability and raises transport costs", "label": "BAD"},
        {"text": "Shipping lanes reopen and prices stabilize after the disruption eases", "label": "GOOD"},
    ])
    df = pd.concat([df, extra_examples], ignore_index=True)

    balanced_parts = []
    target_size = 28
    for label in ["BAD", "GOOD", "NEUTRAL"]:
        label_rows = df[df["label"] == label]
        if len(label_rows) < target_size:
            label_rows = resample(label_rows, replace=True, n_samples=target_size, random_state=42)
        else:
            label_rows = label_rows.sample(n=target_size, random_state=42)
        balanced_parts.append(label_rows)

    return pd.concat(balanced_parts, ignore_index=True)


# ── load data ─────────────────────────────────
df = pd.read_csv("training_data.csv").dropna()
print(f"Training on {len(df)} examples")
print(df["label"].value_counts())

balanced_df = build_balanced_dataset(df)
print("\nBalanced distribution:")
print(balanced_df["label"].value_counts())

X = balanced_df["text"]
y = balanced_df["label"]

# ── split train / test ────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# ── build pipeline ────────────────────────────
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        stop_words="english",
    )),
    ("clf", LinearSVC(
        class_weight="balanced",
        random_state=42
    ))
])

# ── train ─────────────────────────────────────
pipeline.fit(X_train, y_train)

# ── evaluate ──────────────────────────────────
y_pred = pipeline.predict(X_test)
print("\nModel performance:")
print(classification_report(y_test, y_pred, zero_division=0))


model_path = "scout_model.pkl"
joblib.dump(pipeline, model_path)
print(f"\nModel saved to {model_path}")
print("You never need to train again unless you add new data.")

# quick self-check
reloaded = joblib.load(model_path)
print("Model reload check: OK")
print(reloaded.predict(["Oil prices rise after tanker attacks near Hormuz"]))