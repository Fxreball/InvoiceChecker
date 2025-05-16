# Stap 1: Start met een officiële node image
FROM node:18-slim as build

# Stap 2: Stel de werkmap in
WORKDIR /app

# Stap 3: Kopieer de package.json en de package-lock.json
COPY package.json package-lock.json ./

# Stap 4: Installeer de dependencies
RUN npm install

# Stap 5: Kopieer de rest van de applicatie
COPY . .

# Stap 6: Bouw de React app
RUN npm run build

# Stap 7: Gebruik een lichte webserver om de app te serveren
FROM nginx:alpine

# Stap 8: Kopieer de build directory naar de nginx server directory
COPY --from=build /app/build /usr/share/nginx/html

# Stap 9: Expose poort 80 om het publiek toegankelijk te maken
EXPOSE 80

# Stap 10: Start de nginx server
CMD ["nginx", "-g", "daemon off;"]
