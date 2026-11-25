# Northrise University Library Search Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Machine Learning](https://img.shields.io/badge/IR-scikit--learn-orange.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An Information Retrieval (IR) web application engineered for academic document discovery at Northrise University. The system implements vector space text retrieval using Term Frequency-Inverse Document Frequency (TF-IDF) feature extraction and Cosine Similarity scoring to rank and retrieve relevant computer science literature and institutional documents.

---

## Overview

Traditional keyword lookups fail to capture term importance across a corpus. This search engine implements an algebraic vector space model that:

1. **Tokenizes and transforms** raw document text and incoming search queries into normalized sparse TF-IDF vectors.
2. **Computes document-to-query relevance** via high-dimensional cosine similarity.
3. **Ranks matching documents** in descending order of relevance, filtering out non-informative and zero-similarity results.
4. **Supports dynamic corpus ingestion** allowing authorized users to upload and index new `.txt` literature in real time.

---

## Key Features

- **Vector Space Retrieval:** High-performance text indexing powered by `scikit-learn`'s `TfidfVectorizer` with stop-word removal.
- **Cosine Similarity Ranking:** Normalizes vector magnitudes so document length does not unfairly skew relevance scores.
- **Dynamic Ingestion & Instant Indexing:** Direct web upload for `.txt` files with `secure_filename` sanitization and automated re-indexing without server restart.
- **Automatic Category Classification:** Derives document categories automatically from filename naming conventions (e.g. `dynamic_programming.txt` $\to$ `Dynamic`).
- **Interactive Web Interface:** Responsive interface with client-side search suggestions and speech-to-text querying via the browser Web Speech API.
- **Production-Ready & Portable:** Path-independent directory resolution, robust stop-word exception handling, and configurable session secret keys via environment variables.

---

## Mathematical Foundation

### 1. Term Frequency-Inverse Document Frequency (TF-IDF)

For a term $t$ in a document $d$ within a corpus $D$:

$$\text{TF}(t, d) = \frac{f_{t,d}}{\sum_{t' \in d} f_{t', d}}$$

$$\text{IDF}(t, D) = \ln\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$

Each document and query is transformed into a vector in $\mathbb{R}^{|V|}$, where $|V|$ is the size of the vocabulary.

### 2. Cosine Similarity

The relevance score between the query vector $\mathbf{q}$ and document vector $\mathbf{d}$ is the cosine of the angle between them:

$$\text{similarity}(\mathbf{q}, \mathbf{d}) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \|\mathbf{d}\|} = \frac{\sum_{i=1}^{|V|} q_i d_i}{\sqrt{\sum_{i=1}^{|V|} q_i^2} \sqrt{\sum_{i=1}^{|V|} d_i^2}}$$

Scores range from $0.0$ (orthogonal / no shared meaningful terms) to $1.0$ (identical term distribution). Only documents with $\text{score} > 0$ are presented to the user.

---

## Repository Structure

```
northrise-library-search/
├── app.py                     # Flask application, routing, and IR pipeline
├── requirements.txt           # Production and testing dependencies
├── .gitignore                 # Python, environment, and system exclusions
├── README.md                  # System documentation
├── documents/                 # Academic text corpus (CS topics & guides)
│   ├── 4_Best_approach_for_a_small_team.txt
│   ├── Athens.txt
│   ├── BIT_Systems.txt
│   ├── Northrise_University_Library_Search.txt
│   ├── big_o.txt
│   ├── binary_search_trees.txt
│   ├── dynamic_programming.txt
│   ├── greedy_algorithms.txt
│   ├── hash_tables.txt
│   ├── linked_lists.txt
│   ├── recursion.txt
│   ├── searching_sorting.txt
│   ├── stacks_and_queues.txt
│   └── trees_and_graphs.txt
├── static/
│   ├── back.jpg               # UI background asset
│   └── styles.css             # Editorial styling rules
├── templates/
│   ├── index.html             # Search homepage & document uploader
│   └── results.html           # Search results view with score badges
└── tests/
    └── test_search.py         # Automated test suite (12 test cases)
```

---

## Installation & Setup

### Prerequisites

- Python 3.10+
- `pip` package manager

### 1. Clone the Repository

```bash
git clone https://github.com/matt-core-tech/northrise-library-search.git
cd northrise-library-search
```

### 2. Create and Activate a Virtual Environment

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration (Optional)

You can set a custom secret key and port using environment variables:

```bash
# Optional environment variables
export FLASK_SECRET_KEY="your-secure-random-secret"
export PORT=5000
export FLASK_DEBUG=False
```

If `FLASK_SECRET_KEY` is not provided, the application generates a cryptographically secure 24-byte hex key at runtime.

### 5. Launch the Application

```bash
python app.py
```

Open your browser and navigate to `http://127.0.0.1:5000`.

---

## Running the Automated Test Suite

The test suite validates route behavior, search ranking accuracy, category filtering, file upload security, and corpus sanitization.

Execute the test runner:

```bash
python -m unittest discover -s tests -v
```

### Test Coverage Highlights

- **`test_index_page`**: Confirms HTTP 200 and initial indexing of corpus documents.
- **`test_search_relevant_query`**: Confirms TF-IDF similarity calculation and score descending order.
- **`test_search_category_filter`**: Validates filtering by category metadata.
- **`test_search_empty_query` / `test_search_no_matching_terms`**: Verifies graceful handling of empty or out-of-vocabulary queries.
- **`test_search_stop_words_only`**: Ensures vocabulary edge cases (all stop words) do not crash the vectorizer.
- **`test_upload_valid_document`**: Verifies `.txt` upload, filesystem write, and in-memory index expansion.
- **`test_upload_invalid_extension`**: Ensures non-`.txt` files are rejected.
- **`test_security_corpus_sanitization`**: Asserts that sensitive credential files are permanently absent from the repository.
- **`test_secret_key_configuration`**: Verifies dynamic, non-hardcoded secret key initialization.

---

## Security & Sanitization

1. **Corpus Sanitization:** The original development corpus underwent a security review. Accidental local credential files (`Chilimba_Pasword.txt`) were permanently excised prior to repository initialization and verified via automated test assertions.
2. **Session Security:** Removed hardcoded static secrets (`library_secret`) in favor of environment-driven fallback configurations (`os.urandom(24).hex()`).
3. **Upload Protection:** Strictly permits `.txt` files through `ALLOWED_EXTENSIONS` and enforces `werkzeug.utils.secure_filename` to prevent path traversal attacks.

---

## Author

**Mathews Chishimba**  
GitHub: [@matt-core-tech](https://github.com/matt-core-tech)
