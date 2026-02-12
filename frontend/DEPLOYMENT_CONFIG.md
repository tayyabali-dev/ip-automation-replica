# Frontend Deployment Configuration

This document explains how to configure the frontend for different deployment scenarios, including the 4-server architecture.

## Environment Variables

The frontend uses the following environment variables:

- `NEXT_PUBLIC_API_URL`: The URL of the backend API server
- `NODE_ENV`: The deployment environment (development, production)

## Environment Files

### `.env.local`
Current local development configuration. This file is used for your personal development setup.

### `.env.example`
Template file showing all available environment variables. Copy this to create your own `.env.local`.

### `.env.development`
Default development environment configuration.

### `.env.production`
Production environment configuration. Update the API URL to point to your production backend server.

### `.env.4server`
Configuration for 4-server deployment architecture. Update the `NEXT_PUBLIC_API_URL` to point to your backend server.

## Deployment Scenarios

### 1. Local Development
```bash
# Use default .env.local or .env.development
npm run dev
```

### 2. Production Deployment
```bash
# Copy .env.production and update the API URL
cp .env.production .env.local
# Edit .env.local with your production backend URL
npm run build
npm start
```

### 3. 4-Server Deployment
```bash
# Copy .env.4server and update the backend server IP/hostname
cp .env.4server .env.local
# Edit .env.local with your backend server details
# Example: NEXT_PUBLIC_API_URL=http://192.168.1.100:8000/api/v1
npm run build
npm start
```

## Configuration Examples

### Local Development
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NODE_ENV=development
```

### 4-Server Setup with Internal Network
```env
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000/api/v1
NODE_ENV=production
```

### 4-Server Setup with Domain
```env
NEXT_PUBLIC_API_URL=http://backend.yourdomain.com:8000/api/v1
NODE_ENV=production
```

### 4-Server Setup with Load Balancer
```env
NEXT_PUBLIC_API_URL=http://api.yourdomain.com/api/v1
NODE_ENV=production
```

## 4-Server Deployment

For the 4-server deployment architecture, ensure the frontend server can communicate with the backend server by configuring the correct API URL in your environment variables.

## Troubleshooting

### Network Connectivity Issues
- Ensure the backend server is accessible from the frontend server
- Check firewall settings on both servers
- Verify the backend server is running on the specified port
- Test connectivity: `curl http://backend-server-ip:8000/api/v1/health`

### CORS Issues
- Ensure the backend CORS configuration allows requests from the frontend domain
- Check browser developer tools for CORS error messages

### Configuration Validation
The frontend includes automatic configuration validation that will:
- Check if `NEXT_PUBLIC_API_URL` is set
- Validate the URL format
- Log the current configuration on startup

Check the browser console or server logs for configuration messages.

## Security Considerations

- Never expose sensitive backend URLs in public repositories
- Use environment-specific configuration files
- Consider using a reverse proxy or load balancer for production deployments
- Ensure HTTPS is used in production environments