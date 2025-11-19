# Deployment Guide

## 🚀 Quick Deployment Guide

### Option 1: Backend on Render + Frontend on Vercel

#### Backend (Render)

1. **Sign up** at [render.com](https://render.com)

2. **Create New Web Service**
   - Connect your GitHub repository
   - Root directory: `retail-forecasting-system/backend`
   - Runtime: Python 3
   - Build command: `pip install -r ../requirements.txt`
   - Start command: `cd app && uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables** (Add in Render dashboard):
   ```
   PYTHON_VERSION=3.9.0
   MODEL_DIR=saved_models
   ```

4. **Deploy** - Render will automatically build and deploy

5. **Note your API URL**: `https://your-app.onrender.com`

#### Frontend (Vercel)

1. **Sign up** at [vercel.com](https://vercel.com)

2. **Import Project**
   - Connect GitHub repository
   - Root directory: `retail-forecasting-system/frontend`
   - Framework: Next.js

3. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-url.onrender.com
   ```

4. **Deploy** - Vercel will build and deploy automatically

---

### Option 2: Railway (Full Stack)

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Deploy Backend**:
   ```bash
   cd retail-forecasting-system/backend
   railway init
   railway up
   ```

4. **Deploy Frontend**:
   ```bash
   cd ../frontend
   railway init
   railway up
   ```

---

### Option 3: Docker Deployment

See `docker-compose.yml` for full containerized deployment.

```bash
docker-compose up -d
```

---

## 📋 Pre-Deployment Checklist

- [ ] Train models locally first
- [ ] Upload trained models to backend
- [ ] Set correct environment variables
- [ ] Test API endpoints
- [ ] Configure CORS origins
- [ ] Set up error monitoring (Sentry)
- [ ] Configure domain names
- [ ] Set up SSL certificates

---

## 🔧 Production Optimizations

### Backend
- Use Gunicorn with multiple workers
- Enable Redis for caching
- Set up PostgreSQL for data persistence
- Configure logging to file/service
- Enable API rate limiting

### Frontend
- Enable production build optimizations
- Configure CDN for static assets
- Set up analytics (Google Analytics)
- Enable error tracking (Sentry)
- Optimize images

---

## 🔒 Security Best Practices

1. **Never commit** `.env` files
2. **Use environment variables** for all secrets
3. **Enable HTTPS** only in production
4. **Configure CORS** with specific origins
5. **Implement rate limiting** on API
6. **Use API keys** for authentication (future)
7. **Validate all inputs** on backend
8. **Sanitize user uploads**

---

## 📊 Monitoring

### Recommended Tools

- **Backend**: Sentry, Datadog, New Relic
- **Frontend**: Vercel Analytics, Google Analytics
- **Uptime**: UptimeRobot, Pingdom
- **Logs**: Logtail, Papertrail

---

## 🆘 Troubleshooting

### Common Issues

**Backend won't start**:
- Check Python version (3.9+)
- Verify all dependencies installed
- Check environment variables
- Review logs for errors

**Frontend can't connect to API**:
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS configuration on backend
- Ensure backend is running
- Check network/firewall settings

**Models not loading**:
- Ensure models are in correct directory
- Check file permissions
- Verify pickle compatibility
- Re-train if needed

---

## 📞 Support

For deployment issues, check:
- GitHub Issues
- Render/Vercel documentation
- Stack Overflow

---

**Happy Deploying! 🎉**
