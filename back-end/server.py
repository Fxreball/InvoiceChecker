from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

def search_percentage(play_week, title):
    file = 'uploads/percentages.xlsx'

    # Lees het percentages bestand. (Alleen kolom A, B en C)
    df = pd.read_excel(file, header=None, usecols=[0, 1, 2])

    # Geef kolommen beschrijvende namen
    df.columns = ['play_week', 'title', 'percentage']

    # Zet 'play_week' om naar datetime formaat (zodat het goed kan worden vergeleken)
    df['play_week'] = pd.to_datetime(df['play_week'], errors='coerce').dt.strftime('%d-%m-%Y')

    # Zorg ervoor dat 'percentage' een numeriek type is en correct afrondt
    df['percentage'] = pd.to_numeric(df['percentage'], errors='coerce') * 100
    df['percentage'] = df['percentage'].round(2)

    # Zet de play_week-parameter om naar hetzelfde formaat als de dataframe
    try:
        play_week = pd.to_datetime(play_week, format='%d-%m-%Y').strftime('%d-%m-%Y')
    except ValueError:
        return {"error": f"Invalid date format for play_week: {play_week}"}

    # Zoek naar de film op naam en datum
    result = df[(df['play_week'] == play_week) & (df['title'].str.lower() == title.lower())]

    if not result.empty:
        return result.to_dict(orient='records')  # Geef resultaat als JSON terug
    else:
        return {"message": "Geen resultaten gevonden."}  # Teruggeven in JSON-vorm

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

            if isinstance(result, list) and result:  # Als resultaten zijn gevonden
                for res in result:
                    results.append({
                        "play_week": res["play_week"],
                        "title": res["title"],
                        "percentage": res["percentage"]
                    })
            else:
                results.append({
                    "play_week": play_week,
                    "title": title,
                    "percentage": "Geen percentage gevonden."
                })
        else:
            results.append({"error": "Ongeldige invoer", "data": item})

    return jsonify(results)

# API Status
@app.route('/', methods=['GET'])
def home():
    return "API is running! :)"

if __name__ == '__main__':
    app.run(debug=True)
