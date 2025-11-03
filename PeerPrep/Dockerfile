FROM node:22.20.0-alpine AS build-stage

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci

COPY . .

RUN npm run build

# Serve stage
FROM nginx:alpine

RUN mkdir -p /app/www
COPY --from=build-stage /app/dist /app/www

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
