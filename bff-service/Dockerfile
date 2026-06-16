FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production

COPY package*.json ./
RUN npm ci --omit=dev

COPY dist ./dist

EXPOSE 3000
CMD ["node", "dist/index.js"]
