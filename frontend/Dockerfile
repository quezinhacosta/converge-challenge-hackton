# Estagio 1: Build da aplicacao Angular
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build -- --configuration=production

# Estagio 2: Servidor Nginx Alpine
FROM nginx:1.27-alpine

COPY --from=build /app/dist/pulso-frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
