FROM node:20-alpine
WORKDIR /app
COPY apps/web/package*.json ./
RUN npm install
COPY apps/web ./
ARG NEXT_PUBLIC_AIMN_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_AIMN_API_URL=$NEXT_PUBLIC_AIMN_API_URL NODE_ENV=production
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "start"]
