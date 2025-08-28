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
        # Lees het Excel-bestand in
        df = pd.read_excel(bestand)
        print(df.columns.tolist())
    except Exception as e:
        return {"error": f"Kan bestand niet laden: {str(e)}"}

    # Benodigde kolommen
    kolommen_nodig = ['frm_perc', 'master_title_description', 'play_week', 'boxoffice', 'code_description_cinema']
    
    # Controleer of alle kolommen aanwezig zijn
    for kolom in kolommen_nodig:
        if kolom not in df.columns:
            return {"error": f"Kolom '{kolom}' ontbreekt in het bestand"}

    # Zet de 'play_week' kolom om naar datetime en formateer naar DD_MM_YYYY
    df['play_week'] = pd.to_datetime(df['play_week'], errors='coerce').dt.strftime('%d-%m-%Y')

    print(df['boxoffice'].head())

    # Selecteer en retourneer de data als JSON
    return df[['frm_perc', 'master_title_description', 'play_week', 'boxoffice', 'code_description_cinema']].to_dict(orient='records')

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

def search_boxoffice(play_week, title, cinema_location):
    file = os.path.join(UPLOAD_FOLDER, 'recettes.xlsx')

    if not os.path.exists(file):
        return {"error": "Recettes-bestand niet gevonden."}

    try:
        df = pd.read_excel(file, usecols=['Start Datum', 'Titel', 'Flash Rec.', 'Bioscoop'])
    except Exception as e:
        return {"error": f"Fout bij lezen van bestand: {str(e)}"}

    # Zorg dat Start Datum en play_week beiden strings in dd-mm-YYYY zijn
    df['Start Datum'] = df['Start Datum'].astype(str).str.strip()
    play_week = play_week.strip()

    # Filter nu alleen op de bioscoop die in de factuur staat
    df_filtered = df[
        (df['Start Datum'] == play_week) &
        (df['Bioscoop'].str.strip().str.lower() == cinema_location.strip().lower()) &
        (df['Flash Rec.'].notna())
    ].copy()

    if df_filtered.empty:
        return {"message": "Geen resultaten gevonden."}

    df_filtered['Titel_clean'] = df_filtered['Titel'].str.strip().str.lower()
    title_clean = title.strip().lower()

    best_match = process.extractOne(title_clean, df_filtered['Titel_clean'], scorer=fuzz.partial_ratio)

    if best_match and best_match[1] >= 70:
        matched_title = best_match[0]
        result = df_filtered[df_filtered['Titel_clean'] == matched_title]
        return result[['Start Datum', 'Titel', 'Flash Rec.', 'Bioscoop']].to_dict(orient='records')

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
        cinema_location = item.get('code_description_cinema')

        if title and play_week and cinema_location:
            percentage_result = search_percentage(play_week, title)
            boxoffice_result = search_boxoffice(play_week, title, cinema_location)

            combined_result = {
                "play_week": play_week,
                "title": title,
                "location": cinema_location
            }


            if isinstance(percentage_result, list) and percentage_result:
                combined_result["found_percentage"] = percentage_result[0].get("percentage")
            else:
                combined_result["found_percentage"] = "Niet gevonden"

            if isinstance(boxoffice_result, list) and boxoffice_result:
                combined_result["found_boxoffice"] = boxoffice_result[0].get("Flash Rec.")
            else:
                combined_result["found_boxoffice"] = "Niet gevonden"

            results.append(combined_result)

        else:
            results.append({"error": "Ongeldige invoer", "data": item})
    
    return jsonify(results)


@app.route('/', methods=['GET'])
def home():
    return "API is running! :)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
