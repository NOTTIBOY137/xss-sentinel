import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from pathlib import Path

class XSSClassifier:
    def __init__(self, model_path=None):
        self.vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 3))
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        
        # If model path is provided, try to load the model
        if model_path:
            self.load_model(model_path)
    
    def train(self, xss_payloads, benign_samples):
        """Train the XSS classifier model"""
        # Prepare data
        X = xss_payloads + benign_samples
        y = [1] * len(xss_payloads) + [0] * len(benign_samples)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Transform text data to numerical features
        X_train_features = self.vectorizer.fit_transform(X_train)
        X_test_features = self.vectorizer.transform(X_test)
        
        # Train the model
        self.model.fit(X_train_features, y_train)
        
        # Evaluate
        accuracy = self.model.score(X_test_features, y_test)
        print(f"Model trained with accuracy: {accuracy:.4f}")
        
        self.is_trained = True
        return accuracy
    
    def predict(self, texts):
        """Predict if texts are XSS payloads or not"""
        if not self.is_trained:
            raise ValueError("Model is not trained yet")
        
        # Transform input
        features = self.vectorizer.transform(texts)
        
        # Predict
        predictions = self.model.predict(features)
        probabilities = self.model.predict_proba(features)[:, 1]  # Probability of being XSS
        
        return list(zip(predictions, probabilities))
    
    def save_model(self, model_dir="data/models"):
        """Save the trained model and vectorizer"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        os.makedirs(model_dir, exist_ok=True)
        
        # Save model
        model_path = os.path.join(model_dir, "xss_model.pkl")
        vectorizer_path = os.path.join(model_dir, "xss_vectorizer.pkl")
        
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        print(f"Model saved to {model_path}")
        return model_path
    
    def load_model(self, model_dir="data/models"):
        """Load a trained model and vectorizer"""
        model_path = os.path.join(model_dir, "xss_model.pkl")
        vectorizer_path = os.path.join(model_dir, "xss_vectorizer.pkl")
        
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            self.is_trained = True
            print(f"Model loaded from {model_path}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
