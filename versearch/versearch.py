import json
import numpy as np

# 1. Load the data
with open('q-cosine-similarity-server.json', 'r') as f:
    data = json.load(f)

# Extract IDs and embeddings from the LIST of dictionaries
doc_ids = [doc['doc_id'] for doc in data['documents']]
doc_embs = np.array([doc['embedding'] for doc in data['documents']])

query_ids = [q['query_id'] for q in data['queries']]
query_embs = np.array([q['embedding'] for q in data['queries']])

# 2. Vectorized Cosine Similarity
# doc_embs shape: (250, 64), query_embs shape: (10, 64)
# Resulting sims matrix shape: (250, 10) where sims[i, j] is sim between doc i and query j
sims = doc_embs @ query_embs.T

# 3. Ranking with strict tie-breaking
results = {}
doc_indices = np.arange(len(doc_ids)) # [0, 1, 2, ..., 249]

for q_idx in range(len(query_ids)):
    q_sims = sims[:, q_idx]
    
    # np.lexsort sorts by the last array first, then the second to last.
    # Primary: -q_sims (descending similarity)
    # Secondary: doc_indices (ascending index, which matches ascending doc_id)
    sorted_indices = np.lexsort((doc_indices, -q_sims))
    
    # Grab top 5
    top5_indices = sorted_indices[:5]
    top5_ids = [doc_ids[i] for i in top5_indices]
    
    results[query_ids[q_idx]] = top5_ids

# 4. Output
output_json = json.dumps(results, indent=2)
print(output_json)

# Optional: Save to file
with open('results.json', 'w') as f:
    f.write(output_json)