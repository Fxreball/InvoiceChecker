from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import re
from rapidfuzz import fuzz, process
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==== Functie om Excel facturen te lezen ====
def read_invoice(bestand):
    try:
        df = pd.read_excel(bestand)
    except Exception as e:
        return {"error": f"Kan bestand niet laden: {str(e)}"}

    kolommen_nodig = ['frm_perc', 'master_title_description', 'play_week', 'boxoffice']
    for kolom in kolommen_nodig:
        if kolom not in df.columns:
            return {"error": f"Kolom '{kolom}' ontbreekt in het bestand"}

    df['play_week'] = pd.to_datetime(df['play_week'], errors='coerce').dt.strftime('%d-%m-%Y')
    return df[['frm_perc', 'master_title_description', 'play_week', 'boxoffice']].to_dict(orient='records')

# ==== Functie om haakjes uit titels te verwijderen ====
def clean_title(title):
    return re.sub(r"\s*\(.*?\)", "", title).strip()

# ==== Zoek percentages ====
def search_percentage(play_week, title):
    file = os.path.join(UPLOAD_FOLDER, 'percentages.xlsx')
    df = pd.read_excel(file, header=None, usecols=[0, 1, 2])
    df.columns = ['play_week', 'title', 'percentage']

    df['play_week'] = pd.to_datetime(df['play_week'], errors='coerce').dt.strftime('%d-%m-%Y')
    df['percentage'] = pd.to_numeric(df['percentage'], errors='coerce') * 100
    df['percentage'] = df['percentage'].round(2)

    try:
        play_week = pd.to_datetime(play_week, format='%d-%m-%Y').strftime('%d-%m-%Y')
    except ValueError:
        return []

    df_filtered = df[df['play_week'] == play_week]

    if df_filtered.empty:
        return []

    best_match = process.extractOne(title, df_filtered['title'], scorer=fuzz.partial_ratio)
    if best_match and best_match[1] >= 70:
        matched_title = best_match[0]
        result = df_filtered[df_filtered['title'] == matched_title]
        return result.to_dict(orient='records')

    return []

# ==== Zoek boxoffice ====
def search_boxoffice(play_week, title):
    file = os.path.join(UPLOAD_FOLDER, 'recettes.xlsx')
    if not os.path.exists(file):
        return []

    df = pd.read_excel(file, usecols=['Start Datum', 'Titel', 'Flash Rec.'])
    df['Start Datum'] = pd.to_datetime(df['Start Datum'], errors='coerce').dt.strftime('%d-%m-%Y')
    play_week = pd.to_datetime(play_week, format='%d-%m-%Y').strftime('%d-%m-%Y')
    df_filtered = df[df['Start Datum'] == play_week]

    if df_filtered.empty:
        return []

    best_match = process.extractOne(title, df_filtered['Titel'], scorer=fuzz.partial_ratio)
    if best_match and best_match[1] >= 70:
        matched_title = best_match[0]
        result = df_filtered[df_filtered['Titel'] == matched_title]
        return result[['Start Datum', 'Titel', 'Flash Rec.']].to_dict(orient='records')

    return []

# ==== Upload routes ====
@app.route('/upload', methods=['POST'])
def upload_invoice():
    if 'file' not in request.files:
        return jsonify({"error": "Geen bestand geüpload"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Geen bestand geselecteerd"}), 400
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

@app.route('/upload-recettes', methods=['POST'])
def upload_recettes():
    if 'file' not in request.files:
        return jsonify({"error": "Geen bestand geüpload"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Geen bestand geselecteerd"}), 400
    try:
        file_path = os.path.join(UPLOAD_FOLDER, 'recettes.xlsx')
        file.save(file_path)
        return jsonify({"message": "Bestand succesvol geüpload"}), 200
    except Exception as e:
        return jsonify({"error": f"Kan bestand niet opslaan: {str(e)}"}), 500

# ==== Search endpoint ====
@app.route('/search', methods=['POST'])
def search_endpoint():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Request body moet een lijst zijn."}), 400

    results = []

    for item in data:
        title = item.get('master_title_description')
        play_week = item.get('play_week')
        frm_perc = item.get('frm_perc')
        frm_boxoffice = item.get('boxoffice')

        if title and play_week:
            percentage_result = search_percentage(play_week, title)
            boxoffice_result = search_boxoffice(play_week, title)

            combined_result = {
                "play_week": play_week,
                "title": title,
                "frm_perc": frm_perc,
                "frm_boxoffice": frm_boxoffice
            }

            # Percentage uit bestand
            if percentage_result:
                combined_result["found_percentage"] = percentage_result[0].get("percentage")
            else:
                combined_result["found_percentage"] = "Niet gevonden"

            # Boxoffice uit recettes
            if boxoffice_result:
                combined_result["found_boxoffice"] = boxoffice_result[0].get("Flash Rec.")
            else:
                combined_result["found_boxoffice"] = "Niet gevonden"

            results.append(combined_result)
        else:
            results.append({"error": "Ongeldige invoer", "data": item})

    return jsonify(results)

# ==== Home route ====
@app.route('/', methods=['GET'])
def home():
    return "API is running! :)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
