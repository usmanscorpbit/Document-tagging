CATEGORY_KEYWORDS = {
    'Business': [
        'business', 'company', 'product', 'sales', 'market', 'customer',
        'revenue', 'profit', 'commerce', 'ecommerce', 'woocommerce', 'shopify',
        'inventory', 'order', 'discount', 'wholesale', 'retail', 'payment',
        'invoice', 'price', 'shop', 'store', 'client', 'brand', 'marketing'
    ],
    'Legal': [
        'law', 'legal', 'court', 'contract', 'agreement', 'rights', 'liability',
        'clause', 'terms', 'conditions', 'policy', 'compliance', 'regulation',
        'jurisdiction', 'plaintiff', 'defendant', 'attorney', 'statute', 'act'
    ],
    'Technical': [
        'software', 'code', 'programming', 'algorithm', 'database', 'system',
        'network', 'server', 'api', 'function', 'class', 'method', 'variable',
        'framework', 'library', 'developer', 'application', 'frontend', 'backend',
        'python', 'javascript', 'html', 'css', 'sql', 'github', 'deployment'
    ],
    'Academic': [
        'research', 'study', 'analysis', 'hypothesis', 'methodology', 'experiment',
        'results', 'conclusion', 'abstract', 'references', 'journal', 'paper',
        'university', 'academic', 'theory', 'literature', 'citation', 'thesis',
        'objective', 'scope', 'features', 'classification', 'nlp'
    ],
    'Medical': [
        'patient', 'treatment', 'diagnosis', 'symptoms', 'medicine', 'disease',
        'health', 'clinical', 'hospital', 'doctor', 'therapy', 'drug', 'medical',
        'peptide', 'protein', 'amino', 'purity', 'reconstitution', 'vial', 'dosage'
    ],
    'Finance': [
        'finance', 'financial', 'investment', 'stock', 'portfolio', 'budget',
        'accounting', 'tax', 'revenue', 'expense', 'balance', 'asset', 'liability',
        'equity', 'bank', 'loan', 'interest', 'cost', 'profit', 'loss', 'audit'
    ],
}

def classify_document(text):
    text_lower = text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(text_lower.count(kw) for kw in keywords)
        scores[category] = score

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return 'General'
    return best
