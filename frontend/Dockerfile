# Development stage
FROM node:18-alpine as development

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]

# Build stage
FROM node:18-alpine as build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
ARG VITE_API_URL=http://localhost:8000
RUN VITE_API_URL=$VITE_API_URL npm run build

# Production stage
FROM nginx:alpine as production

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
