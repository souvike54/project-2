import os
import sqlite3
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

# Configure where uploaded files will be saved
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Creates the folder if it doesn't exist

# Initialize our database
def init_db():
    with sqlite3.connect('academic.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT,
                title TEXT,
                material_type TEXT,
                file_name TEXT,
                yt_link TEXT
            )
        ''')
        conn.commit()

init_db()

@app.route('/')
def home():
    school_classes = ["Primary", "Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7", "Class 8"]
    return render_template('index.html', classes=school_classes)

@app.route('/class/<class_name>')
def class_page(class_name):
    # Fetch all materials for this specific class from the database
    with sqlite3.connect('academic.db') as conn:
        c = conn.cursor()
        c.execute("SELECT title, material_type, file_name, yt_link FROM materials WHERE class_name=?", (class_name,))
        materials = c.fetchall()
        
    return render_template('class_page.html', class_name=class_name, materials=materials)

@app.route('/upload/<class_name>', methods=['GET', 'POST'])
def upload_page(class_name):
    if request.method == 'POST':
        title = request.form['title']
        material_type = request.form['material_type']
        
        file_name = ""
        yt_link = ""

        # Handle File Upload
        if material_type == 'file':
            file = request.files['file']
            if file and file.filename != '':
                file_name = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
        
        # Handle YouTube Link
        elif material_type == 'link':
            yt_link = request.form['yt_link']

        # Save to database
        with sqlite3.connect('academic.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO materials (class_name, title, material_type, file_name, yt_link) VALUES (?, ?, ?, ?, ?)",
                      (class_name, title, material_type, file_name, yt_link))
            conn.commit()

        # Send them back to the class dashboard
        return redirect(url_for('class_page', class_name=class_name))

    # If GET request, just show the form
    return render_template('upload.html', class_name=class_name)

# This route allows users to download/view the uploaded PDFs
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)