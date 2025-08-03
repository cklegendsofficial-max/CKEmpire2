# Multi-stage build for CK Empire Frontend
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Set environment variables for production build
ENV NODE_ENV=production
ENV REACT_APP_API_URL=http://localhost:8000
ENV REACT_APP_ENVIRONMENT=production

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Create non-root user
RUN addgroup -g 1001 -S ckempire && \
    adduser -S ckempire -u 1001

# Change ownership of nginx directories
RUN chown -R ckempire:ckempire /var/cache/nginx && \
    chown -R ckempire:ckempire /var/log/nginx && \
    chown -R ckempire:ckempire /etc/nginx/conf.d && \
    chown -R ckempire:ckempire /usr/share/nginx/html && \
    touch /var/run/nginx.pid && \
    chown -R ckempire:ckempire /var/run/nginx.pid

# Switch to non-root user
USER ckempire

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 