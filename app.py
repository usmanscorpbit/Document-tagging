import os
from flask import Flask, render_template, request, redirect, url_for, flash
from tagger import extract_tags
from classifier import classify_document
from database import init_db, save_document, get_all_documents, get_document, update_tags, delete_document
import fitz  # PyMuPDF

app = Flask(__name__)
app.secret_key = 'university_project_2024'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

init_db()

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_text_from_file(filepath, ext):
    if ext == 'pdf':
        text = ''
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    else:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('Please select a file first.')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected.')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('Only .txt and .pdf files are supported.')
        return redirect(url_for('index'))

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    ext = filename.rsplit('.', 1)[1].lower()
    text = read_text_from_file(filepath, ext)

    # Extract top 20 tags — first 10 = auto-selected, next 10 = suggestions
    all_tags = extract_tags(text, top_n=20)
    selected_tags = all_tags[:10]
    suggested_tags = all_tags[10:]

    word_count = len(text.split())
    category = classify_document(text)
    file_size = os.path.getsize(filepath)

    doc_id = save_document(filename, filepath, file_size, selected_tags, word_count, category)

    return render_template('result.html',
        doc=get_document(doc_id),
        suggested_tags=suggested_tags
    )

@app.route('/update_tags/<int:doc_id>', methods=['POST'])
def update_tags_route(doc_id):
    tags_input = request.form.get('tags', '')
    tags = [t.strip() for t in tags_input.split(',') if t.strip()]
    update_tags(doc_id, tags)
    flash('Tags saved successfully!')
    return redirect(url_for('documents'))

@app.route('/documents')
def documents():
    query = request.args.get('q', '').strip().lower()
    docs = get_all_documents()
    if query:
        docs = [d for d in docs if
                query in d['filename'].lower() or
                any(query in tag.lower() for tag in d['tags']) or
                query in d.get('category', '').lower()]
    return render_template('documents.html', docs=docs, query=query)

@app.route('/view/<int:doc_id>')
def view(doc_id):
    doc = get_document(doc_id)
    if not doc:
        flash('Document not found.')
        return redirect(url_for('documents'))
    text = ''
    if os.path.exists(doc['filepath']):
        ext = doc['filename'].rsplit('.', 1)[-1].lower()
        text = read_text_from_file(doc['filepath'], ext)
    return render_template('view.html', doc=doc, text=text)

@app.route('/delete/<int:doc_id>', methods=['POST'])
def delete(doc_id):
    delete_document(doc_id)
    flash('Document deleted.')
    return redirect(url_for('documents'))

if __name__ == '__main__':
    app.run(debug=True)
