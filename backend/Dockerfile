# Gebruik een lichte Python-image
FROM python:3.11

# Stel de werkdirectory in
WORKDIR /app

# Kopieer projectbestanden
COPY . .

# Installeer afhankelijkheden
RUN pip install --no-cache-dir -r requirements.txt

# Open poort 5000
EXPOSE 5000

# Start de Flask-server
CMD ["python", "server.py"]
