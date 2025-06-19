# Deployment Guide

This guide covers deploying the Cascadia Watershed Lookup application to various platforms.

## 🚀 Prerequisites

Before deploying, ensure you have:

1. **Unified watershed dataset** (`cascadia_watersheds.gpkg`) created following the data processing pipeline
2. **Geocoding API key** from [geocode.maps.co](https://geocode.maps.co/) (optional but recommended)
3. **Git repository** pushed to GitHub
4. **Docker** installed (for containerized deployments)

## 🐳 Docker Deployment

### Local Docker Testing

```bash
# Build the image
docker build -t cascadia-watershed-lookup .

# Run with environment variables
docker run -p 5000:5000 \
  -e GEOCODING_API_KEY=your_api_key_here \
  -v $(pwd)/data:/app/data \
  cascadia-watershed-lookup
```

### Docker Compose (Recommended for Local Development)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - GEOCODING_API_KEY=${GEOCODING_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## ☁️ Cloud Platform Deployments

### Heroku

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Add Buildpacks** (for geospatial dependencies)
   ```bash
   heroku buildpacks:add --index 1 heroku-community/apt
   heroku buildpacks:add --index 2 heroku/python
   ```

4. **Create Aptfile** for system dependencies:
   ```bash
   echo "gdal-bin libgdal-dev libspatialindex-dev" > Aptfile
   ```

5. **Set Environment Variables**
   ```bash
   heroku config:set GEOCODING_API_KEY=your_api_key_here
   heroku config:set FLASK_ENV=production
   ```

6. **Deploy**
   ```bash
   git push heroku main
   ```

7. **Upload Dataset** (via Heroku CLI or file upload)
   ```bash
   # This is challenging for large files - consider cloud storage
   ```

### Railway

1. **Connect GitHub Repository**
   - Go to [Railway](https://railway.app/)
   - Connect your GitHub account
   - Select the repository

2. **Configure Environment Variables**
   ```
   GEOCODING_API_KEY=your_api_key_here
   FLASK_ENV=production
   PORT=5000
   ```

3. **Auto-Deploy**
   - Railway will automatically build and deploy
   - Monitor deployment in Railway dashboard

### DigitalOcean App Platform

1. **Create App**
   ```bash
   # Install doctl CLI
   brew install doctl  # macOS
   
   # Or use web interface at https://cloud.digitalocean.com/apps
   ```

2. **App Specification** (`.do/app.yaml`):
   ```yaml
   name: cascadia-watershed-lookup
   services:
   - name: web
     source_dir: /
     github:
       repo: your-username/CascadiaWatershedLookup
       branch: main
     run_command: gunicorn --bind 0.0.0.0:8080 app:app
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     envs:
     - key: GEOCODING_API_KEY
       value: your_api_key_here
     - key: FLASK_ENV
       value: production
   ```

3. **Deploy**
   ```bash
   doctl apps create --spec .do/app.yaml
   ```

### AWS (Elastic Beanstalk)

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize Application**
   ```bash
   eb init -p python-3.11 cascadia-watershed-lookup
   ```

3. **Create Environment**
   ```bash
   eb create production
   ```

4. **Configure Environment Variables**
   ```bash
   eb setenv GEOCODING_API_KEY=your_api_key_here FLASK_ENV=production
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

## 📊 Data Deployment Strategies

The watershed dataset (`cascadia_watersheds.gpkg`) is typically 100MB+ and needs special handling:

### Option 1: Cloud Storage + Download on Startup

```python
# Add to app.py initialization
import boto3
from urllib.request import urlretrieve

def download_dataset():
    if not os.path.exists('data/cascadia_watersheds.gpkg'):
        print("Downloading watershed dataset...")
        urlretrieve(
            'https://your-bucket.s3.amazonaws.com/cascadia_watersheds.gpkg',
            'data/cascadia_watersheds.gpkg'
        )
```

### Option 2: Git LFS (Large File Storage)

```bash
# Install git-lfs
git lfs install

# Track large files
git lfs track "*.gpkg"
git add .gitattributes
git add data/cascadia_watersheds.gpkg
git commit -m "Add watershed dataset with LFS"
git push
```

### Option 3: Docker Volume Mount

```bash
# Upload to cloud storage, mount at runtime
docker run -v /path/to/data:/app/data cascadia-watershed-lookup
```

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# Essential
GEOCODING_API_KEY=your_geocoding_api_key
FLASK_ENV=production

# Optional
SECRET_KEY=your_secret_key_for_sessions
WATERSHED_DATA_PATH=data/cascadia_watersheds.gpkg
PORT=5000
```

### Production Settings

Create `.env.production`:

```bash
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secure-secret-key
GEOCODING_API_KEY=your_api_key
```

## 🔍 Monitoring & Health Checks

### Health Check Endpoint

The app includes `/api/health` for monitoring:

```bash
curl https://your-app.com/api/health
```

Response:
```json
{
  "status": "healthy",
  "service": "available",
  "version": "1.0.0"
}
```

### Logging Configuration

```python
# Add to app.py for production logging
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

## 🚨 Troubleshooting

### Common Issues

1. **GDAL/Geospatial Library Errors**
   ```bash
   # Ensure system dependencies are installed
   apt-get install gdal-bin libgdal-dev libspatialindex-dev
   ```

2. **Large File Upload Issues**
   - Use cloud storage for dataset
   - Consider data compression
   - Implement progressive data loading

3. **Memory Issues**
   - Increase instance size
   - Implement dataset lazy loading
   - Use data chunking strategies

4. **Geocoding API Rate Limits**
   - Implement request caching
   - Add retry logic with backoff
   - Consider multiple API providers

### Performance Optimization

1. **Enable Caching**
   ```python
   from flask_caching import Cache
   
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   
   @cache.memoize(timeout=3600)
   def cached_geocode(address):
       return geocode_address(address)
   ```

2. **Database Optimization**
   - Ensure spatial indexes are built
   - Consider PostGIS for larger datasets
   - Implement connection pooling

3. **CDN Integration**
   - Use CDN for static assets
   - Cache API responses appropriately
   - Implement gzip compression

## 🔐 Security Considerations

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables or secret management
   - Rotate keys regularly

2. **Rate Limiting**
   ```python
   from flask_limiter import Limiter
   from flask_limiter.util import get_remote_address
   
   limiter = Limiter(app, key_func=get_remote_address)
   
   @app.route('/api/lookup', methods=['POST'])
   @limiter.limit("10 per minute")
   def api_lookup():
       # ... existing code
   ```

3. **HTTPS Configuration**
   - Always use HTTPS in production
   - Configure SSL/TLS certificates
   - Implement HSTS headers

## 📈 Scaling Considerations

1. **Horizontal Scaling**
   - Use load balancers
   - Implement stateless design
   - Consider microservices architecture

2. **Database Scaling**
   - Implement read replicas
   - Consider sharding for global deployment
   - Use connection pooling

3. **Caching Strategies**
   - Redis for distributed caching
   - CDN for static content
   - Application-level caching

---

For additional help, see the [main README](../README.md) or open an issue on GitHub.