from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB


# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


DATASET_PATH = Path(__file__).with_name("spam.csv")
SCAM_KEYWORDS = [
    # Banking & Financial Scams
    "bank",
    "account",
    "password",
    "otp",
    "verify",
    "urgent",
    "click",
    "link",
    "payment",
    "blocked",
    "suspended",
    "update",
    "card",
    "atm",
    "balance",
    "security",
    "confirm",
    "authentication",
    "transfer",
    "wire",
    "transaction",
    # Prize & Giveaway Scams
    "prize",
    "win",
    "claim",
    "offer",
    "gift",
    "congratulations",
    "selected",
    "reward",
    "lottery",
    "free",
    # Urgent & Authority Scams
    "act now",
    "limited time",
    "expire",
    "immediately",
    "expire",
    "deadline",
    # Personal Info & Access
    "credentials",
    "pin",
    "code",
    "cvv",
    "ssn",
    # Tech Support & Malware Scams
    "virus",
    "infected",
    "malware",
    "warning",
    "alert",
    "support",
    "technical",
    "software",
    # Romance & Trust Scams
    "love",
    "dear",
    "money",
    "overseas",
    "visa",
    "fees",
    "help me",
    "honey",
    "darling",
    # Phishing Common Phrases
    "validate",
    "authenticate",
    "reactivate",
    "reopen",
    "unlock",
    "restore",
    "recover",
    # Delivery & Package Scams
    "package",
    "delivery",
    "parcel",
    "tracking",
    "shipment",
    "pending",
    "collect",
    "courier",
    # Fake Investment & Money Making
    "invest",
    "return",
    "profit",
    "earn",
    "dividend",
    "interest",
    "guarantee",
    "boost",
    "rich",
    "passive income",
    # Job & Work Scams
    "hire",
    "job",
    "work",
    "salary",
    "position",
    "apply",
    "recruit",
    "employment",
    # Identity & Documents
    "identity",
    "document",
    "verification",
    "proof",
    "license",
    "passport",
    # Impersonation & Fake Authority
    "admin",
    "support team",
    "official",
    "compliance",
    "department",
    "authority",
    # Common Scam Inducing Words
    "click here",
    "here now",
    "act fast",
    "don't miss",
    "exclusive",
    "special",
    "limited",
    "secret",
    "guaranteed",
    "risk-free",
]
SAFETY_RECOMMENDATIONS = [
    "Do not click unknown links or download attachments.",
    "Do not share OTPs, passwords, or bank details by message.",
    "Verify the sender through an official website or phone number.",
    "If money or urgency is involved, pause and confirm with a trusted source.",
]


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_dataset(dataset_path: Path = DATASET_PATH) -> pd.DataFrame:
    """Load and prepare the SMS spam dataset."""
    try:
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found at {dataset_path}")
        df = pd.read_csv(dataset_path, usecols=["v1", "v2"], encoding="latin-1")
        df = df.rename(columns={"v1": "label", "v2": "message"})
        df["label"] = df["label"].map({"ham": 0, "spam": 1})
        df["message"] = df["message"].fillna("").apply(clean_text)
        result = df.dropna(subset=["label"])
        logger.info(f"Dataset loaded successfully. Shape: {result.shape}")
        return result
    except FileNotFoundError as e:
        logger.error(f"Dataset loading failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while loading dataset: {e}")
        raise


def train_model(test_size: float = 0.2, random_state: int = 42) -> dict:
    """Train the spam detection model."""
    try:
        df = load_dataset()
        x_train, x_test, y_train, y_test = train_test_split(
            df["message"],
            df["label"],
            test_size=test_size,
            random_state=random_state,
            stratify=df["label"],
        )

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        x_train_vec = vectorizer.fit_transform(x_train)
        x_test_vec = vectorizer.transform(x_test)

        model = MultinomialNB()
        model.fit(x_train_vec, y_train)

        y_pred = model.predict(x_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        logger.info(
            f"Model trained successfully. Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}"
        )

        return {
            "dataset": df,
            "vectorizer": vectorizer,
            "model": model,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    except Exception as e:
        logger.error(f"Error during model training: {e}")
        raise


def find_scam_keywords(message: str) -> list[str]:
    """Find scam keywords in a message."""
    lowered_message = message.lower()
    return [keyword for keyword in SCAM_KEYWORDS if keyword in lowered_message]


def predict_message(message: str, model, vectorizer) -> dict:
    """Predict whether a message is scam or safe."""
    try:
        if not message or not isinstance(message, str):
            raise ValueError("Message must be a non-empty string")

        cleaned_message = clean_text(message)
        vector_input = vectorizer.transform([cleaned_message])
        prediction = int(model.predict(vector_input)[0])
        probabilities = model.predict_proba(vector_input)[0]
        keyword_hits = find_scam_keywords(message)
        raw_probability = float(probabilities[1])

        adjusted_probability = max(raw_probability, min(0.99, 0.15 * len(keyword_hits)))
        is_scam = prediction == 1 or bool(keyword_hits)

        result = {
            "is_scam": is_scam,
            "model_prediction": prediction,
            "raw_probability": raw_probability,
            "scam_probability": adjusted_probability,
            "keyword_hits": keyword_hits,
            "cleaned_message": cleaned_message,
        }
        logger.debug(f"Prediction made: {result}")
        return result
    except ValueError as e:
        logger.error(f"Invalid input for prediction: {e}")
        raise
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        raise
