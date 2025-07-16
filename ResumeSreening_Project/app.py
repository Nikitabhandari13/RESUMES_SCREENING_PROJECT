import os
import fitz  # PyMuPDF
import docx
from flask import Flask, render_template, request

app = Flask(__name__)
UPLOAD_FOLDER = 'resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# === TEXT EXTRACTION ===
def extract_text(path):
    if path.endswith('.pdf'):
        text = ""
        doc = fitz.open(path)
        for page in doc:
            text += page.get_text()
        return text
    elif path.endswith('.docx'):
        doc = docx.Document(path)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif path.endswith('.txt'):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# === MAIN ROUTE ===
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
      #  jd = request.form['jd']
        selected_skills = request.form.getlist('skills')
        
        files = request.files.getlist('resumes')
        resume_texts = []
        filenames = []

        for file in files:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            text = extract_text(filepath)
            resume_texts.append(text)
            filenames.append(file.filename)

        # === SKILL-BASED RANKING LOGIC ===
        results = []
        for filename, text in zip(filenames, resume_texts):
            skill_count = 0
            for skill in selected_skills:
                if skill.lower() in text.lower():
                    skill_count += 1
            match_score = skill_count / len(selected_skills) if selected_skills else 0
            results.append((filename, match_score))

        ranked = sorted(results, key=lambda x: x[1], reverse=True)

        return render_template('result.html', results=ranked)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
