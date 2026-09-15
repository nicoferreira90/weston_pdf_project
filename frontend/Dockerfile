FROM node:22-slim

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html tsconfig.json vite.config.ts ./
COPY src ./src

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
