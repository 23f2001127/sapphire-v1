import os
from flask import Flask, render_template, request, send_from_directory, session
import secrets
# --- CRITICAL IMPORTS ---
from processor import CarbonProcessor 

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure the upload directory exists so the app doesn't crash on the first run
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

processor = CarbonProcessor()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['bill']
        if file:
            # Use os.path.join for Windows/Linux compatibility
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            
            # AI Extraction & Calculation
            fuel, units = processor.extract_data(path)
            co2 = processor.calculate_emissions(fuel, units)
            
            result_data = {"fuel": fuel, "units": units, "co2": co2}
            
            # Generate the PDF
            report_file = processor.generate_pdf_report(result_data)
            session['last_report'] = report_file
            
            return render_template('index.html', result=result_data, report=report_file)
    return render_template('index.html', result=None)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)