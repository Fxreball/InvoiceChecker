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

# Functie om de Excel-gegevens te laden
def read_invoice(bestand):
    try:
        df = pd.read_excel(bestand)
        print(df.columns.tolist())
    except Exception as e:
        return {"error": f"Kan bestand niet laden: {str(e)}"}

    kolommen_nodig = ['frm_perc', 'master_title_description', 'play_week', 'boxoffice']
    for kolom in kolommen_nodig:
        if kolom not in df.columns:
            return {"error": f"Kolom '{kolom}' ontbreekt in het bestand"}

    # Zet om naar datetime
    df['play_week'] = pd.to_datetime(df['play_week'], errors='coerce')

    # Sorteer op play_week (oud naar nieuw)
    df = df.sort_values('play_week')

    # Format voor we teruggeven
    df['play_week'] = df['play_week'].dt.strftime('%d-%m-%Y')

    print(df['boxoffice'].head())
    return df[['frm_perc', 'master_title_description', 'play_week', 'boxoffice']].to_dict(orient='records')


def clean_title(title):
    return re.sub(r"\s*\(.*?\)", "", title).strip()

def search_percentage(play_week, title):
    file = os.path.join(UPLOAD_FOLDER, 'percentages.xlsx')

    if not os.path.exists(file):
        return {"error": "percentages.xlsx bestand niet gevonden in uploads folder."}

    df = pd.read_excel(file, header=None, usecols=[0, 1, 2])
    df.columns = ['play_week', 'title', 'percentage']

    df['play_week'] = pd.to_datetime(df['play_week'], errors='coerce').dt.strftime('%d-%m-%Y')
    df['percentage'] = pd.to_numeric(df['percentage'], errors='coerce') * 100
    df['percentage'] = df['percentage'].round(2)

    try:
        play_week = pd.to_datetime(play_week, format='%d-%m-%Y').strftime('%d-%m-%Y')
    except ValueError:
        return {"error": f"Invalid date format for play_week: {play_week}"}

    df_filtered = df[df['play_week'] == play_week]
    best_match = process.extractOne(title, df_filtered['title'], scorer=fuzz.partial_ratio)

    if best_match and best_match[1] >= 70:
        matched_title = best_match[0]
        result = df_filtered[df_filtered['title'] == matched_title]
        return result.to_dict(orient='records')

    return {"message": "Geen resultaten gevonden."}

def search_boxoffice(play_week, title):
    file = os.path.join(UPLOAD_FOLDER, 'recettes.xlsx')

    if not os.path.exists(file):
        return {"error": "recettes.xlsx bestand niet gevonden in uploads folder."}

    try:
        df = pd.read_excel(file, usecols=[2, 4, 17])
        df.columns = ['Start Datum', 'Titel', 'BOR Rec.']
    except Exception as e:
        return {"error": f"Fout bij lezen van recettes-bestand: {str(e)}"}

    # Normaliseer datums (verwijder tijd)
    df['Start Datum'] = pd.to_datetime(df['Start Datum'], dayfirst=True, errors='coerce').dt.normalize()

    try:
        play_week_date = pd.to_datetime(play_week, dayfirst=True, errors='coerce').normalize()
    except Exception as e:
        return {"error": f"Ongeldig datumformaat voor play_week: {str(e)}"}

    if pd.isna(play_week_date):
        return {"error": "Ongeldig of leeg datumformaat voor play_week."}

    df_filtered = df[df['Start Datum'] == play_week_date]

    if df_filtered.empty:
        return {"message": "Geen data gevonden voor deze datum."}

    best_match = process.extractOne(title, df_filtered['Titel'], scorer=fuzz.partial_ratio)

    if best_match and best_match[1] >= 70:
        matched_title = best_match[0]
        result = df_filtered[df_filtered['Titel'] == matched_title]
        return result[['Start Datum', 'Titel', 'BOR Rec.']].to_dict(orient='records')

    return {"message": "Geen boxoffice gevonden."}

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
            percentage_result = search_percentage(play_week, title)
            boxoffice_result = search_boxoffice(play_week, title)

            combined_result = {
                "play_week": play_week,
                "title": title
            }

            if isinstance(percentage_result, list) and percentage_result:
                combined_result["percentage"] = percentage_result[0].get("percentage")
            else:
                combined_result["percentage"] = "Niet gevonden"

            if isinstance(boxoffice_result, list) and boxoffice_result:
                combined_result["boxoffice"] = boxoffice_result[0].get("BOR Rec.")
            else:
                combined_result["boxoffice"] = "Niet gevonden"

            results.append(combined_result)
        else:
            results.append({"error": "Ongeldige invoer", "data": item})

    return jsonify(results)

@app.route('/', methods=['GET'])
def home():
    return "API is running! :)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
