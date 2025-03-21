from flask import Flask, request, jsonify
import pandas as pd
import re
from rapidfuzz import fuzz, process

app = Flask(__name__)

def clean_title(title):
    """ Verwijdert haakjes en hun inhoud uit de titel """
    return re.sub(r"\s*\(.*?\)", "", title).strip()

def search_percentage(play_week, title):
    file = 'uploads/percentages.xlsx'

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

    # Fuzzy matchen op titel
    best_match = process.extractOne(title, df_filtered['title'], scorer=fuzz.ratio)

    if best_match and best_match[1] >= 60:  # 70% match drempel
        matched_title = best_match[0]
        result = df_filtered[df_filtered['title'] == matched_title]
        return result.to_dict(orient='records')

    return {"message": "Geen resultaten gevonden."}

@app.route('/search', methods=['POST'])
def search_endpoint(): 
    data = request.get_json()
    
    if not isinstance(data, list):  # Zorg ervoor dat de input een lijst is
        return jsonify({"error": "Request body moet een lijst zijn."}), 400

    results = []

    for item in data:
        title = item.get('master_title_description')
        play_week = item.get('play_week')

        if title and play_week:
            result = search_percentage(play_week, title)
            if isinstance(result, list) and result:
                results.extend(result)  # Voeg alle gevonden resultaten toe
            else:
                results.append({"play_week": play_week, "title": title, "message": "Geen resultaten gevonden."})
        else:
            results.append({"error": "Ongeldige invoer", "data": item})

    return jsonify(results)

@app.route('/', methods=['GET'])
def home():
    return "API is running! :)"

if __name__ == '__main__':
    app.run(debug=True)