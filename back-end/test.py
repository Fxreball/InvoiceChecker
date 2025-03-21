import pandas as pd

def search_percentage(title, play_week):
    file = 'uploads/percentages.xlsx'

    # Lees het percentages bestand. (Alleen kolom A, B en C)
    df = pd.read_excel(file, header=None, usecols=[0, 1, 2])

    # Geef kolommen beschrijvende namen
    df.columns = ['play_week', 'title', 'percentage']

    # Zet 'play_week' om naar datetime formaat (zodat het goed kan worden vergeleken)
    df['play_week'] = pd.to_datetime(df['play_week'], errors='coerce').dt.strftime('%d-%m-%Y')

    # Zorg ervoor dat 'percentage' een numeriek type is en correct afrondt
    df['percentage'] = pd.to_numeric(df['percentage'], errors='coerce') * 100  # Vermenigvuldig met 100
    df['percentage'] = df['percentage'].round(2)  # Rond af op twee decimalen

    # Zet de play_week-parameter om naar hetzelfde formaat als de dataframe
    play_week = pd.to_datetime(play_week, format='%d-%m-%Y').strftime('%d-%m-%Y')

    # Zoek naar de film op naam en datum
    result = df[(df['play_week'] == play_week) & (df['title'].str.lower() == title.lower())]

    if not result.empty:
        # Print de gevonden resultaten
        for index, row in result.iterrows():
            print(f"Speelweek: {row['play_week']}, Film: {row['title']}, Percentage: {row['percentage']}")
    else:
        print("Geen resultaten gevonden.")

# Test de functie
title = 'Babygirl'
play_week = '06-03-2024'

search_percentage(title, play_week)
