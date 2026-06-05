from transformers import pipeline

# Hardcoded list of highly toxic / bad keywords for instant 100% reliable matching
BAD_WORDS = [
    "kill", "murder", "hate", "abuse", "die", "threat", "hack", "spam", 
    "fuck", "bitch", "bastard", "idiot", "fool", "damn", "shit", "abusive",
    "destroy you", "beat you", "hurt you", "hacked", "scam"
]

classifier = None
classifier_loaded = False

def get_classifier():
    global classifier, classifier_loaded
    if not classifier_loaded:
        try:
            print("[AI Engine] Loading Transformers toxic-bert pipeline (lazy-loading)...")
            classifier = pipeline(
                "text-classification",
                model="unitary/toxic-bert"
            )
            print("[AI Engine] Transformers pipeline loaded successfully.")
        except Exception as e:
            print(f"[AI Engine] Transformers pipeline failed to load: {e}. Using fallback keyword classifier.")
            classifier = None
        classifier_loaded = True
    return classifier


def analyze_text(text):
    if not text or not isinstance(text, str) or not text.strip():
        return 0.0, "LOW"
    text_lower = text.lower()
    
    # 1. First run the explicit keyword matching for 100% reliability
    for word in BAD_WORDS:
        if word in text_lower:
            # Force high toxicity and critical level for explicitly bad words
            return 0.95, "CRITICAL"

    # 2. Try the neural network classifier
    score = 0.0
    clf = get_classifier()
    if clf:
        try:
            res = clf(text)
            if res:
                result = res[0]
                # If the classifier predicts toxic labels with high probability
                # or depending on the model's output schema, let's treat the score
                # as the toxicity probability.
                score = result.get("score", 0.0)
                # Some models return label names like 'toxic' or 'non-toxic'
                label = result.get("label", "").lower()
                if "non-toxic" in label or "neutral" in label:
                    score = 1.0 - score
        except Exception as e:
            print(f"Classifier prediction error: {e}")
            score = 0.0

    if score < 0.3:
        level = "LOW"
    elif score < 0.6:
        level = "MEDIUM"
    elif score < 0.85:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return score, level