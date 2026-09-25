import os
import re
import json
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

VECTOR_STORE_DIR = os.path.join("data", "vector_store")
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

def load_text_documents():
    docs = []
    
    # 1. Bank Fraud Policy
    policy_path = os.path.join("docs", "knowledge", "fraud_policy.md")
    if os.path.exists(policy_path):
        with open(policy_path, "r", encoding="utf-8") as f:
            policy_text = f.read()
        
        # Split by sections or rules
        rule_sections = re.split(r'\n(?=- \*\*Rule R\d+:)', policy_text)
        for idx, section in enumerate(rule_sections):
            m = re.search(r'\*\*Rule (R\d+):([^\*]+)\*\*', section)
            rule_id = m.group(1) if m else f"POL-{idx}"
            title = m.group(0) if m else f"Policy Section {idx}"
            docs.append({
                "doc_id": f"POLICY-{rule_id}",
                "doc_type": "policy_rule",
                "title": title,
                "content": section.strip(),
                "metadata": {
                    "rule_id": rule_id,
                    "source": "fraud_policy.md"
                }
            })
    
    # 2. Fraud Typologies
    typology_path = os.path.join("docs", "knowledge", "fraud_typologies.md")
    if os.path.exists(typology_path):
        with open(typology_path, "r", encoding="utf-8") as f:
            typology_text = f.read()
        
        sections = re.split(r'\n(?=## Typology \d+:)', typology_text)
        for idx, section in enumerate(sections):
            m = re.search(r'## Typology \d+:\s*([^\n\(]+)(?:\(([^)]+)\))?', section)
            pattern = m.group(2).strip() if m and m.group(2) else f"typology_{idx}"
            title = m.group(0).strip() if m else f"Typology {idx}"
            docs.append({
                "doc_id": f"TYPOLOGY-{pattern}",
                "doc_type": "fraud_typology",
                "title": title,
                "content": section.strip(),
                "metadata": {
                    "pattern": pattern,
                    "source": "fraud_typologies.md"
                }
            })
            
    # 3. Regulatory Standards (FinCEN, FATF, FFIEC)
    reg_path = os.path.join("docs", "knowledge", "regulatory_fincen_fatf_ffiec.md")
    if os.path.exists(reg_path):
        with open(reg_path, "r", encoding="utf-8") as f:
            reg_text = f.read()
        
        sections = re.split(r'\n(?=## \d+\. )', reg_text)
        for idx, section in enumerate(sections):
            m = re.search(r'## \d+\.\s*([^\n]+)', section)
            title = m.group(1).strip() if m else f"Regulation {idx}"
            docs.append({
                "doc_id": f"REG-{idx}",
                "doc_type": "regulatory_guidance",
                "title": title,
                "content": section.strip(),
                "metadata": {
                    "source": "regulatory_fincen_fatf_ffiec.md"
                }
            })
            
    # 4. Historical Closed Cases (5,565 records)
    cc_path = os.path.join("data", "closed_cases_history.csv")
    if os.path.exists(cc_path):
        df_cc = pd.read_csv(cc_path)
        for idx, r in df_cc.iterrows():
            cid = str(r['case_id'])
            notes = str(r['analyst_notes'])
            pattern = str(r['pattern'])
            outcome = str(r['outcome'])
            exp = float(r['exposure_usd'])
            
            docs.append({
                "doc_id": f"CASE-{cid}",
                "doc_type": "closed_case_memory",
                "title": f"Closed Case {cid} ({outcome}, {pattern})",
                "content": notes,
                "metadata": {
                    "case_id": cid,
                    "customer_id": str(r['customer_id']),
                    "card_id": str(r['card_id']),
                    "outcome": outcome,
                    "pattern": pattern,
                    "exposure_usd": exp,
                    "actions_taken": str(r['actions_taken']),
                    "report_filed": str(r['report_filed'])
                }
            })
            
    return docs

def build_vector_store():
    print("Loading documents for vector indexing...")
    docs = load_text_documents()
    print(f"Total documents to index: {len(docs)}")
    
    # Extract text corpus
    texts = [f"{d['title']} {d['content']}" for d in docs]
    
    # Compute TF-IDF matrix
    print("Fitting TfidfVectorizer...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=25000,
        sublinear_tf=True,
        stop_words='english'
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    
    # Save artifacts
    print(f"Saving vector store artifacts to {VECTOR_STORE_DIR}...")
    with open(os.path.join(VECTOR_STORE_DIR, "corpus.json"), "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2)
        
    with open(os.path.join(VECTOR_STORE_DIR, "vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)
        
    with open(os.path.join(VECTOR_STORE_DIR, "tfidf_matrix.pkl"), "wb") as f:
        pickle.dump(tfidf_matrix, f)
        
    print("Vector store indexing complete!")
    return docs, vectorizer, tfidf_matrix

class VectorRetriever:
    def __init__(self, store_dir=VECTOR_STORE_DIR):
        with open(os.path.join(store_dir, "corpus.json"), "r", encoding="utf-8") as f:
            self.docs = json.load(f)
        with open(os.path.join(store_dir, "vectorizer.pkl"), "rb") as f:
            self.vectorizer = pickle.load(f)
        with open(os.path.join(store_dir, "tfidf_matrix.pkl"), "rb") as f:
            self.tfidf_matrix = pickle.load(f)
            
    def search(self, query: str, top_k: int = 5, doc_type: str = None):
        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.tfidf_matrix)[0]
        
        results = []
        ranked_indices = np.argsort(scores)[::-1]
        for idx in ranked_indices:
            doc = self.docs[idx]
            if doc_type and doc['doc_type'] != doc_type:
                continue
            score = float(scores[idx])
            if score <= 0.0:
                break
            results.append({
                "doc_id": doc['doc_id'],
                "doc_type": doc['doc_type'],
                "title": doc['title'],
                "score": round(score, 4),
                "metadata": doc['metadata'],
                "content_snippet": doc['content'][:300] + ("..." if len(doc['content']) > 300 else "")
            })
            if len(results) >= top_k:
                break
        return results

if __name__ == "__main__":
    docs, vec, mat = build_vector_store()
    retriever = VectorRetriever()
    
    print("\n=== Smoke Test: Search Policy Rules ===")
    test_q = "customer denies authorizing transaction exposure over 1000 block card file report"
    res = retriever.search(test_q, top_k=2, doc_type="policy_rule")
    for r in res:
        print(f"[{r['score']}] {r['doc_id']}: {r['title']}")
        print(f"   {r['content_snippet'][:150]}...")
        
    print("\n=== Smoke Test: Search Closed Cases Memory ===")
    test_q2 = "three small online authorizations under 5 dollars card testing sequence"
    res2 = retriever.search(test_q2, top_k=3, doc_type="closed_case_memory")
    for r in res2:
        print(f"[{r['score']}] {r['doc_id']} (Pattern: {r['metadata']['pattern']}, Exposure: ${r['metadata']['exposure_usd']}):")
        print(f"   {r['content_snippet'][:150]}...\n")
