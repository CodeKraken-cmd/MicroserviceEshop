FROM node:20 AS build
WORKDIR /app
COPY package.json .
COPY tsconfig*.json . 2>/dev/null || true
COPY vite.config.ts .
COPY tailwind.config.js postcss.config.js .
COPY index.html .
COPY src ./src
RUN npm ci && npm run build
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
RUN printf 'server { listen 80; root /usr/share/nginx/html; index index.html; location / { try_files $uri /index.html; } }' > /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx","-g","daemon off;"]
