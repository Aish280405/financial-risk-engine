#!/usr/bin/env python3
"""
Sentiment Evaluation Script

Evaluates the existing FinBERT sentiment implementation against a labelled
financial news dataset (Financial PhraseBank) stored in data/evaluation/.

Does NOT retrain or fine-tune FinBERT. Uses the existing analyze_sentiment()
function from the risk engine.
"""

import os
import sys
import csv
from collections import Counter

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.sentiment import analyze_sentiment


def dataset_label_to_finbert(label: str) -> str:
    """Map dataset sentiment label to FinBERT output label.
    
    The Financial PhraseBank dataset uses: positive, neutral, negative
    FinBERT outputs: negative, neutral, positive (via label.lower())
    """
    mapping = {
        "positive": "positive",
        "neutral": "neutral", 
        "negative": "negative",
    }
    return mapping.get(label.lower(), "neutral")


def evaluate():
    """Run the full evaluation and print metrics."""
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "evaluation", "all-data.csv"
    )
    
    # Load labelled dataset
    true_labels = []
    texts = []
    
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Format: sentiment,"text content"
            idx = line.index(",")
            true_sent = line[:idx].strip().lower()
            # Extract text between quotes
            text_start = idx + 1
            text = line[text_start:].strip('"').strip()
            
            if text:  # skip empty texts
                true_labels.append(true_sent)
                texts.append(text)
    
    print(f"Loaded {len(texts)} samples from {csv_path}")
    print(f"True label distribution: {Counter(true_labels)}")
    print()
    
    # Run FinBERT sentiment on each text
    pred_labels = []
    for i, text in enumerate(texts):
        try:
            result = analyze_sentiment(text)
            finbert_label = result["sentiment_label"].lower()
            pred_labels.append(finbert_label)
        except Exception as e:
            print(f"Error on sample {i}: {e}")
            pred_labels.append("neutral")  # fallback
    
    print(f"Predicted label distribution: {Counter(pred_labels)}")
    print()
    
    # Calculate metrics
    # Only compute for the three known classes
    classes = ["positive", "neutral", "negative"]
    
    # Build confusion matrix
    cm = Counter()
    for true, pred in zip(true_labels, pred_labels):
        cm_key = (true, pred)
        cm[cm_key] += 1
    
    print("Confusion Matrix (True \\ Predicted):")
    print("            | Pred: positive  Pred: neutral  Pred: negative")
    print("--------------------------------------------------------")
    for true_class in classes:
        row_total = sum(cm[(true_class, pred)] for pred in classes)
        print(f"True: {true_class:9} | ", end="")
        for pred_class in classes:
            count = cm.get((true_class, pred_class), 0)
            print(f"{count:5}", end="")
            if pred_class != classes[-1]:
                print("  ", end="")
        print()
    print()
    
    # Calculate per-class metrics
    print("Per-Class Metrics:")
    print("-" * 40)
    
    for true_class in classes:
        true_pos = cm.get((true_class, true_class), 0)
        
        # Precision: TP / (TP + FP) = TP / (all predictions of this class)
        false_pos = sum(cm.get((other, true_class), 0) for other in classes if other != true_class)
        pred_total = sum(cm.get((true_other, true_class), 0) for true_other in classes)
        
        precision = true_pos / pred_total if pred_total > 0 else 0.0
        
        # Recall: TP / (TP + FN) = TP / (all samples of this class)
        false_neg = sum(cm.get((true_class, other), 0) for other in classes if other != true_class)
        true_total = sum(cm.get((true_class, true_other), 0) for true_other in classes)
        
        recall = true_pos / true_total if true_total > 0 else 0.0
        
        # F1: 2 * (precision * recall) / (precision + recall)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        print(f"{true_class:9}:  precision={precision:.3f}  recall={recall:.3f}  f1={f1:.3f}")
    
    # Overall accuracy
    correct = sum(cm.get((c, c), 0) for c in classes)
    total = len(true_labels)
    accuracy = correct / total if total > 0 else 0.0
    
    print()
    print("-" * 40)
    print(f"Overall Accuracy: {accuracy:.3f} ({correct}/{total})")
    print(f"Subset evaluated: {total} samples from Financial PhraseBank dataset")


if __name__ == "__main__":
    evaluate()