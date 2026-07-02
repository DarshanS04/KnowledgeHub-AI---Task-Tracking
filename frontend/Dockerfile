# ==============================================================================
# KnowledgeHub AI - Frontend Dockerfile
# ==============================================================================
FROM node:22-alpine as builder

WORKDIR /app

# Copy package descriptors
COPY package*.json ./

# Install packages
RUN npm ci

# Copy codebase
COPY . .

# Run build step
RUN npm run build

# Runner Nginx container
FROM nginx:1.25-alpine

# Copy custom nginx config if needed, otherwise use default
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
