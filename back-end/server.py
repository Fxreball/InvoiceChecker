from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

def search_percentage(play_week, title):
    file = 'uploads/percentages.xlsx' 

    # Lees het percentages bestand. (Alleen kolom A, B en C)
    df = pd.read_excel(file, header=None, usecols=[0, 1, 2])
    
    # Geef kolommen beschrijvende namen
    df.columns = ['play_week', 'title', 'percentage']

    # Zet 'play_week' om naar datetime formaat
    df['play_week'] = pd.to_datetime(df['play_week'], errors='coerce')

    # Zorg ervoor dat 'percentage' een numeriek type is en correct afrondt
    df['percentage'] = pd.to_numeric(df['percentage'], errors='coerce') * 100  # Vermenigvuldig met 100
    df['percentage'] = df['percentage'].round(2)  # Rond af op twee decimalen

    # Zoek naar de film op naam en datum
    result = df[(df['play_week'] == play_week) & (df['title'] == title)]

    # Controleer of er een resultaat is gevonden
    if not result.empty:
        # Zet het resultaat om naar een lijst van dictionaries
        result_dict = result[['play_week', 'title', 'percentage']].to_dict(orient='records')
        
        for item in result_dict:
            item['play_week'] = item['play_week'].strftime('%d-%m-%Y') # Zet play_week om naar DD-MM-YYYY
            item['percentage'] = f"{item['percentage']:.2f}".replace('.', ',')  # Gebruik komma als decimaalteken

        return result_dict
    else:
        return {'message': 'Geen resultaat gevonden.'}

# Zoek film route
@app.route('/search', methods=['POST'])
def search_endpoint(): 
    data = request.get_json()
    
    title = data['master_title_description']
    play_week = data['play_week']
    
    results = search_percentage(play_week, title)
    return jsonify(results)

# API Status
@app.route('/', methods=['GET'])
def home():
    return "API is running! :)"

if __name__ == '__main__':
    app.run(debug=True)
