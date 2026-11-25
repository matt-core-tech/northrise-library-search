import io
import os
import unittest
from app import app, documents, titles, categories, load_existing_documents, BASE_DIR, UPLOAD_FOLDER


class NorthriseLibrarySearchTestCase(unittest.TestCase):
    def setUp(self):
        """Set up Flask test client and ensure standard test state."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        # Ensure documents are loaded in consistent state
        load_existing_documents()

    def test_index_page(self):
        """Test index page returns HTTP 200 and displays indexed document count."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Northrise University Library Search", html)
        self.assertIn(f"Documents indexed: {len(documents)}", html)
        self.assertGreater(len(documents), 0)

    def test_search_relevant_query(self):
        """Test search returns relevant documents ranked with cosine similarity."""
        response = self.client.get('/search?q=binary+search+trees')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("binary_search_trees.txt", html)
        self.assertIn("Score:", html)
        self.assertIn("result(s) found", html)

    def test_search_category_filter(self):
        """Test category filter narrows results to selected category."""
        response = self.client.get('/search?q=subproblems&category=Dynamic')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("dynamic_programming.txt", html)
        self.assertIn("Score:", html)

    def test_search_empty_query(self):
        """Test empty query returns 0 results gracefully."""
        response = self.client.get('/search?q=')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("0 result(s) found", html)

    def test_search_no_matching_terms(self):
        """Test non-existent query terms return 0 results gracefully."""
        response = self.client.get('/search?q=xyznonexistenttoken987654321')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("0 result(s) found", html)
        self.assertIn("No results matched your query", html)

    def test_search_stop_words_only(self):
        """Test search query with only stop words does not crash the vectorizer."""
        response = self.client.get('/search?q=the+and+or+in+on')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("0 result(s) found", html)

    def test_serve_existing_document(self):
        """Test serving a raw text document from the corpus."""
        response = self.client.get('/documents/big_o.txt')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        response.close()
        self.assertIn("Big O", content)

    def test_serve_missing_document(self):
        """Test serving a non-existent document returns HTTP 404."""
        response = self.client.get('/documents/non_existent_file_xyz.txt')
        self.assertEqual(response.status_code, 404)

    def test_upload_valid_document(self):
        """Test uploading a new valid .txt document."""
        test_filename = "test_upload_doc.txt"
        test_filepath = os.path.join(UPLOAD_FOLDER, test_filename)

        try:
            data = {
                'file': (io.BytesIO(b"Unit testing document for search index verification."), test_filename)
            }
            response = self.client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            html = response.data.decode('utf-8')
            self.assertIn("uploaded and indexed successfully", html)
            self.assertIn(test_filename, titles)
        finally:
            # Clean up test file
            if os.path.exists(test_filepath):
                os.remove(test_filepath)
            load_existing_documents()

    def test_upload_invalid_extension(self):
        """Test uploading an invalid file extension is rejected."""
        data = {
            'file': (io.BytesIO(b"binary payload"), "malicious.exe")
        }
        response = self.client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Invalid file type. Please upload a .txt file.", html)

    def test_security_sensitive_credentials_excluded(self):
        """Security audit: Ensure no credential files exist in repository or documents."""
        # Check documents folder
        doc_files = os.listdir(UPLOAD_FOLDER)
        self.assertNotIn("Chilimba_Pasword.txt", doc_files)
        self.assertFalse(any("password" in f.lower() for f in doc_files))

        # Check whole repository
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                self.assertNotIn("chilimba", file.lower())
                self.assertNotIn("pasword", file.lower())

    def test_secret_key_configuration(self):
        """Security audit: Ensure secret key is non-empty and configurable."""
        self.assertTrue(bool(app.secret_key))
        self.assertNotEqual(app.secret_key, "library_secret")


if __name__ == '__main__':
    unittest.main()
