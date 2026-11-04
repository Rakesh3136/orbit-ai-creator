FROM node:20-alpine
WORKDIR /app
COPY apps/web/package*.json ./
RUN npm install
COPY apps/web ./
ARG AIMN_INTERNAL_API_URL=http://api:8000
ENV AIMN_INTERNAL_API_URL=$AIMN_INTERNAL_API_URL NODE_ENV=production
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "start"]
