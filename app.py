import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize application
app = Flask(__name__)

# Secret key: read from environment or generate a secure random hex key
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24).hex()

# Configure upload and storage paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "documents")
ALLOWED_EXTENSIONS = {'txt'}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# In-memory corpus collections and vectorizer
documents = []
titles = []
categories = []
vectorizer = TfidfVectorizer(stop_words="english")


def allowed_file(filename):
    """Check if file extension is permitted."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_category(filename):
    """Derive category from filename prefix convention."""
    if '_' in filename:
        prefix = filename.split('_')[0]
        return prefix.capitalize()
    return "General"


def load_existing_documents():
    """Load and index all valid .txt documents present in the documents directory."""
    documents.clear()
    titles.clear()
    categories.clear()

    if os.path.exists(UPLOAD_FOLDER):
        for filename in sorted(os.listdir(UPLOAD_FOLDER)):
            if allowed_file(filename):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read().strip()
                    if text:
                        documents.append(text)
                        titles.append(filename)
                        categories.append(extract_category(filename))
                except Exception as err:
                    print(f"Warning: could not read {filename}: {err}")


# Index available corpus on startup
load_existing_documents()


@app.route('/')
def index():
    """Home view showing total indexed documents and available categories."""
    num_docs = len(documents)
    unique_categories = sorted(set(categories))
    return render_template('index.html', num_docs=num_docs, categories=unique_categories)


@app.route('/upload', methods=['POST'])
def upload():
    """Upload and dynamically index a new .txt document."""
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not filename:
            flash("Invalid file name.")
            return redirect(url_for('index'))

        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        documents.append(text)
        titles.append(filename)
        categories.append(extract_category(filename))

        flash(f"'{filename}' uploaded and indexed successfully!")
    else:
        flash("Invalid file type. Please upload a .txt file.")
    return redirect(url_for('index'))


@app.route('/search')
def search():
    """Search documents using TF-IDF representation and Cosine Similarity."""
    query = request.args.get('q', '').strip()
    selected_cat = request.args.get('category', 'All')
    results = []

    if not query or not documents:
        return render_template('results.html', query=query, results=results, num_results=0, category_filter=selected_cat)

    # Filter documents by category if specified
    filtered_docs = []
    filtered_titles = []
    filtered_cats = []
    for doc, title, cat in zip(documents, titles, categories):
        if selected_cat == "All" or cat == selected_cat:
            filtered_docs.append(doc)
            filtered_titles.append(title)
            filtered_cats.append(cat)

    if not filtered_docs:
        return render_template('results.html', query=query, results=[], num_results=0, category_filter=selected_cat)

    # TF-IDF vectorization and cosine similarity
    try:
        tfidf = vectorizer.fit_transform(filtered_docs + [query])
        scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
        feature_names = vectorizer.get_feature_names_out().tolist() if hasattr(vectorizer, 'get_feature_names_out') else []

        for i, score in enumerate(scores):
            if score > 0:
                snippet = filtered_docs[i][:300].replace('\n', ' ')
                results.append({
                    "title": filtered_titles[i],
                    "score": round(float(score), 4),
                    "category": filtered_cats[i],
                    "snippet": snippet,
                    "top_terms": feature_names[:5]
                })

        # Rank results descending by similarity score
        results.sort(key=lambda x: x["score"], reverse=True)
    except ValueError:
        # Handles edge cases (e.g. query consists entirely of stop words not in vocabulary)
        results = []

    return render_template('results.html', query=query, results=results, num_results=len(results), category_filter=selected_cat)


@app.route('/documents/<path:filename>')
def serve_document(filename):
    """Serve raw text document from the documents directory."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(host="0.0.0.0", port=port, debug=debug)
