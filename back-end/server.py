from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import re
from rapidfuzz import fuzz, process
import os

app = Flask(__name__)

CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Functie om de Excel-gegevens te laden
def read_invoice(bestand):
    try:
        # Lees het Excel-bestand in
        df = pd.read_excel(bestand)
    except Exception as e:
        return {"error": f"Kan bestand niet laden: {str(e)}"}

    # Benodigde kolommen
    kolommen_nodig = ['frm_perc', 'master_title_description', 'play_week']
    
    # Controleer of alle kolommen aanwezig zijn
    for kolom in kolommen_nodig:
        if kolom not in df.columns:
            return {"error": f"Kolom '{kolom}' ontbreekt in het bestand"}

    # Zet de 'play_week' kolom om naar datetime en formateer naar DD_MM_YYYY
    df['play_week'] = pd.to_datetime(df['play_week'], errors='coerce').dt.strftime('%d-%m-%Y')

    # Selecteer en retourneer de data als JSON
    return df[['frm_perc', 'master_title_description', 'play_week']].to_dict(orient='records')

def clean_title(title):
    """ Verwijdert haakjes en hun inhoud uit de titel """
    return re.sub(r"\s*\(.*?\)", "", title).strip()

def search_percentage(play_week, title):
    file = os.path.join(UPLOAD_FOLDER, 'percentages.xlsx')

    # Lees het percentages bestand (Alleen kolommen A, B en C)
    df = pd.read_excel(file, header=None, usecols=[0, 1, 2])
    df.columns = ['play_week', 'title', 'percentage']

    # Formatteer 'play_week'
    df['play_week'] = pd.to_datetime(df['play_week'], errors='coerce').dt.strftime('%d-%m-%Y')

    # Zorg dat 'percentage' numeriek is en rond af
    df['percentage'] = pd.to_numeric(df['percentage'], errors='coerce') * 100
    df['percentage'] = df['percentage'].round(2)

    # Converteer play_week
    try:
        play_week = pd.to_datetime(play_week, format='%d-%m-%Y').strftime('%d-%m-%Y')
    except ValueError:
        return {"error": f"Invalid date format for play_week: {play_week}"}

    # Filter alleen de juiste speeldatum
    df_filtered = df[df['play_week'] == play_week]

    # Fuzzy matchen op titel (met een lagere drempel)
    best_match = process.extractOne(title, df_filtered['title'], scorer=fuzz.partial_ratio)

    if best_match and best_match[1] >= 70:
        matched_title = best_match[0]
        result = df_filtered[df_filtered['title'] == matched_title]
        return result.to_dict(orient='records')

    return {"message": "Geen resultaten gevonden."}

# Route voor bestand uploaden
@app.route('/upload', methods=['POST'])
def upload_invoice():
    if 'file' not in request.files:
        return jsonify({"error": "Geen bestand geüpload"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Geen bestand geselecteerd"}), 400

    # Voer de lees_facturen functie uit
    invoice_data = read_invoice(file)
    
    return jsonify(invoice_data)

@app.route('/upload-percentages', methods=['POST'])
def upload_percentages():
    if 'file' not in request.files:
        return jsonify({"error": "Geen bestand geüpload"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Geen bestand geselecteerd"}), 400

    try:
        file_path = os.path.join(UPLOAD_FOLDER, 'percentages.xlsx')
        file.save(file_path)
        return jsonify({"message": "Bestand succesvol geüpload"}), 200
    except Exception as e:
        return jsonify({"error": f"Kan bestand niet opslaan: {str(e)}"}), 500

@app.route('/search', methods=['POST'])
def search_endpoint(): 
    data = request.get_json()
    
    if not isinstance(data, list):
        return jsonify({"error": "Request body moet een lijst zijn."}), 400

    results = []

    for item in data:
        title = item.get('master_title_description')
        play_week = item.get('play_week')

        if title and play_week:
            result = search_percentage(play_week, title)
            if isinstance(result, list) and result:
                results.extend(result)
            else:
                results.append({"play_week": play_week, "title": title, "message": "Geen resultaten gevonden."})
        else:
            results.append({"error": "Ongeldige invoer", "data": item})
    
    print(results)
    return jsonify(results)

@app.route('/', methods=['GET'])
def home():
    return "API is running! :)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
