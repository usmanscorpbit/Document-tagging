import re
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import numpy as np

# Generic words that appear often in any document but carry no meaning as tags
EXTRA_STOPWORDS = {
    'page', 'allow', 'option', 'options', 'show', 'like', 'use', 'used',
    'make', 'need', 'want', 'able', 'will', 'just', 'also', 'back',
    'well', 'good', 'click', 'button', 'drop', 'select', 'field',
    'fields', 'item', 'items', 'list', 'based', 'number', 'time',
    'times', 'date', 'input', 'edit', 'create', 'add', 'set',
    'view', 'note', 'notes', 'custom', 'current', 'default', 'sure',
    'example', 'end', 'new', 'old', 'https', 'com', 'www', 'once',
    'going', 'each', 'way', 'best', 'main', 'simply', 'certain',
    'provide', 'details', 'soon', 'pop', 'site', 'print', 'send',
    'image', 'bottom', 'top', 'left', 'right', 'section', 'address',
    'email', 'name', 'status', 'type', 'size', 'weight', 'value',
    'card', 'check', 'different', 'local', 'total', 'personal',
    'multiple', 'single', 'available', 'follow', 'track', 'track',
    'creation', 'deletion', 'allow', 'must', 'copy'
}

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    return text

def is_meaningful(term):
    words = term.split()
    # filter out if all words are stopwords or very short
    if all(len(w) <= 3 for w in words):
        return False
    if all(w in EXTRA_STOPWORDS for w in words):
        return False
    return True

def extract_tags(text, top_n=10):
    if not text or not text.strip():
        return []

    sentences = [s.strip() for s in re.split(r'[.!?\n]', text) if len(s.strip()) > 10]

    if len(sentences) < 2:
        words = clean_text(text).split()
        words = [w for w in words if len(w) > 3 and w not in EXTRA_STOPWORDS]
        counter = Counter(words)
        return [word for word, _ in counter.most_common(top_n)]

    try:
        vectorizer = TfidfVectorizer(
            max_features=200,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=1
        )
        tfidf_matrix = vectorizer.fit_transform(sentences)
        scores = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
        feature_names = vectorizer.get_feature_names_out()

        # Score bigrams higher — they are more specific and meaningful
        boosted_scores = []
        for i, name in enumerate(feature_names):
            score = scores[i]
            if len(name.split()) == 2:
                score *= 1.6  # boost 2-word phrases
            boosted_scores.append(score)

        boosted_scores = np.array(boosted_scores)
        top_indices = boosted_scores.argsort()[::-1]

        tags = []
        seen_roots = set()

        for i in top_indices:
            term = feature_names[i]
            if not is_meaningful(term) or term in EXTRA_STOPWORDS:
                continue

            # Deduplicate: skip if a root word already exists
            # e.g. skip "orders" if "order" already added, skip "discounts" if "discount" added
            root = term.rstrip('s')
            if root in seen_roots or term in seen_roots:
                continue

            tags.append(term)
            seen_roots.add(term)
            seen_roots.add(root)

            if len(tags) >= top_n:
                break

        return tags

    except Exception:
        words = clean_text(text).split()
        words = [w for w in words if len(w) > 3 and w not in EXTRA_STOPWORDS]
        counter = Counter(words)
        return [word for word, _ in counter.most_common(top_n)]
