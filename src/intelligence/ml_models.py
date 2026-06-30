import os
import pickle
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Target path for saving/loading the trained model
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "classifier.pkl")

class MLClassifier:
    """Manages training and prediction of feedback category using scikit-learn."""

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """Loads model from disk if it exists."""
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                logger.info("Successfully loaded ML classifier model from disk.")
            except Exception as e:
                logger.error(f"Failed to load ML classifier model: {e}")
                self.model = None
        else:
            self.model = None

    def predict(self, text: str) -> Optional[str]:
        """
        Predicts the category of feedback text using the trained model.
        Returns None if no model is trained.
        """
        if self.model is None or not text:
            return None
        try:
            prediction = self.model.predict([text])[0]
            # Ensure predicted label is valid and not empty
            return str(prediction) if prediction else None
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None

    def train_model(self, data: List[Tuple[str, str]]) -> bool:
        """
        Trains the classifier on a list of (text, category) tuples.
        Saves the trained model to disk.
        """
        if len(data) < 5:  # Need a minimal amount of samples to train
            logger.warning("Insufficient data to train ML model. Need at least 5 samples.")
            return False

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import Pipeline

            texts = [item[0] for item in data]
            labels = [item[1] for item in data]

            # Build standard TF-IDF + Logistic Regression pipeline
            pipeline = Pipeline([
                ("tfidf", TfidfVectorizer(max_features=1000, stop_words="english")),
                ("clf", LogisticRegression(class_weight="balanced", C=1.0))
            ])

            # Train the model
            pipeline.fit(texts, labels)
            self.model = pipeline

            # Save the model
            os.makedirs(MODEL_DIR, exist_ok=True)
            with open(MODEL_PATH, "wb") as f:
                pickle.dump(self.model, f)

            logger.info("Successfully trained and saved ML classifier.")
            return True

        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            return False
