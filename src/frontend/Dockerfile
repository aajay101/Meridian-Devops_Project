
# Stage 1: Build Vue application
FROM node:22-alpine AS builder

WORKDIR /app

# Install frontend dependencies
COPY package*.json ./

RUN npm ci

# Copy frontend source
COPY . .

# Generate production build
RUN npm run build


# Stage 2: Serve using Nginx
FROM nginx:alpine

# Remove default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy production build from Node stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
