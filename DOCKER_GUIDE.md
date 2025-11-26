# 🐳 Docker Deployment Guide for TripPlanner

This guide will walk you through containerizing and running the TripPlanner application using Docker.

---

## 📋 Prerequisites

Before you begin, ensure you have:
- ✅ Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- ✅ Docker Compose installed (usually comes with Docker Desktop)
- ✅ Your API keys ready (Google AI, Amadeus)

### Check Docker Installation

```bash
docker --version
docker-compose --version
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example or create new
cat > .env << EOF
GOOGLE_API_KEY=your_google_api_key_here
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here
EOF
```

**⚠️ IMPORTANT**: Replace the placeholder values with your actual API keys!

### Step 2: Build the Docker Image

```bash
# Build the image
docker-compose build

# Or build without cache (if you made changes)
docker-compose build --no-cache
```

**What happens:**
- Downloads Python 3.11 base image
- Installs all dependencies from `requirements.txt`
- Copies your application code
- Sets up Streamlit to run on port 8501

### Step 3: Run the Container

```bash
# Start the container
docker-compose up

# Or run in detached mode (background)
docker-compose up -d
```

**Access the app:**
Open your browser to: **http://localhost:8501**

---

## 🛠️ Detailed Docker Commands

### Building

```bash
# Build with docker-compose
docker-compose build

# Build directly with Docker (without compose)
docker build -t tripplanner:latest .

# Build with specific tag
docker build -t tripplanner:v1.0 .
```

### Running

```bash
# Run with docker-compose (recommended)
docker-compose up

# Run in background
docker-compose up -d

# Run with Docker directly (pass env variables)
docker run -d \
  -p 8501:8501 \
  -e GOOGLE_API_KEY="your_key" \
  -e AMADEUS_API_KEY="your_key" \
  -e AMADEUS_API_SECRET="your_secret" \
  --name tripplanner \
  tripplanner:latest
```

### Managing Containers

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Stop the container
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart the container
docker-compose restart

# View logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for last 100 lines
docker-compose logs --tail=100
```

### Debugging

```bash
# Execute commands inside running container
docker-compose exec tripplanner bash

# Or with Docker directly
docker exec -it tripplanner-app bash

# Inside container, you can:
# - Check Python version: python --version
# - Test imports: python -c "import streamlit; print(streamlit.__version__)"
# - View files: ls -la
# - Check environment: env | grep API
```

---

## 📁 Understanding the Docker Setup

### Dockerfile Explained

```dockerfile
FROM python:3.11-slim          # Base image with Python 3.11
WORKDIR /app                   # Set working directory
COPY requirements.txt .        # Copy dependencies first (caching)
RUN pip install -r requirements.txt  # Install dependencies
COPY . .                       # Copy application code
EXPOSE 8501                    # Expose Streamlit port
CMD ["streamlit", "run", "app.py"]  # Start command
```

### .dockerignore Explained

This file tells Docker what NOT to copy into the image:
- ✅ Excludes `venv/` (virtual environment)
- ✅ Excludes `.env` files (secrets)
- ✅ Excludes `__pycache__/` (Python cache)
- ✅ Excludes `.git/` (Git history)

### docker-compose.yml Explained

```yaml
services:
  tripplanner:           # Service name
    build: .             # Build from current directory
    ports:
      - "8501:8501"      # Map host:container ports
    environment:         # Pass environment variables
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    env_file:
      - .env             # Load from .env file
```

---

## 🔒 Security Best Practices

### 1. Never Commit .env Files

Add to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

### 2. Use Docker Secrets (Production)

For production deployments:
```bash
# Create secrets
echo "your_google_key" | docker secret create google_api_key -
echo "your_amadeus_key" | docker secret create amadeus_api_key -

# Reference in docker-compose.yml
secrets:
  - google_api_key
  - amadeus_api_key
```

### 3. Use Multi-Stage Builds (Optional)

For smaller images:
```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["streamlit", "run", "app.py"]
```

---

## 🌐 Deployment Options

### Option 1: Local Development

```bash
docker-compose up
```
Access at: http://localhost:8501

### Option 2: Cloud Deployment (AWS, GCP, Azure)

1. **Push to Container Registry**

```bash
# Tag for Docker Hub
docker tag tripplanner:latest yourusername/tripplanner:latest

# Push to Docker Hub
docker push yourusername/tripplanner:latest

# Or for Google Container Registry
docker tag tripplanner:latest gcr.io/your-project/tripplanner:latest
docker push gcr.io/your-project/tripplanner:latest
```

2. **Deploy to Cloud Run (GCP)**

```bash
gcloud run deploy tripplanner \
  --image gcr.io/your-project/tripplanner:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key
```

3. **Deploy to ECS (AWS)**

```bash
# Create task definition and service
aws ecs create-service \
  --cluster your-cluster \
  --service-name tripplanner \
  --task-definition tripplanner:1 \
  --desired-count 1
```

### Option 3: Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml tripplanner

# Scale service
docker service scale tripplanner_tripplanner=3
```

---

## 🔧 Troubleshooting

### Issue 1: Port Already in Use

```bash
# Find what's using port 8501
lsof -i :8501

# Kill the process
kill -9 <PID>

# Or use different port in docker-compose.yml
ports:
  - "8502:8501"  # Access via localhost:8502
```

### Issue 2: Container Keeps Restarting

```bash
# Check logs
docker-compose logs

# Common causes:
# - Missing environment variables
# - Port conflicts
# - Application crashes
```

### Issue 3: Can't Connect to Container

```bash
# Verify container is running
docker ps

# Check if port is mapped correctly
docker port tripplanner-app

# Test from inside container
docker exec tripplanner-app curl http://localhost:8501/_stcore/health
```

### Issue 4: Changes Not Reflected

```bash
# Rebuild without cache
docker-compose build --no-cache

# Restart container
docker-compose restart
```

---

## 📊 Performance Optimization

### 1. Use .dockerignore

Already configured! Reduces build context size.

### 2. Layer Caching

```dockerfile
# Good: Copy requirements first
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Bad: Copy everything first (invalidates cache on any change)
COPY . .
RUN pip install -r requirements.txt
```

### 3. Use Smaller Base Image

```dockerfile
# Current: python:3.11-slim (smaller)
# Alternative: python:3.11-alpine (smallest, but may need build tools)
```

### 4. Multi-Stage Builds

See Security Best Practices section above.

---

## 📈 Monitoring

### Basic Monitoring

```bash
# Resource usage
docker stats

# Specific container
docker stats tripplanner-app

# Container logs
docker-compose logs -f --tail=100
```

### Advanced Monitoring

Integrate with:
- **Prometheus** + **Grafana** for metrics
- **ELK Stack** for log aggregation
- **Datadog** or **New Relic** for APM

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] Environment variables configured via secrets (not .env)
- [ ] Health checks configured
- [ ] Resource limits set (CPU, memory)
- [ ] Logging configured (to external service)
- [ ] Monitoring set up
- [ ] Backup strategy for persistent data
- [ ] CI/CD pipeline configured
- [ ] SSL/TLS certificates configured
- [ ] Rate limiting implemented
- [ ] Error tracking (e.g., Sentry)

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Streamlit Docker Guide](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
- [Container Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 🆘 Need Help?

If you encounter issues:

1. Check logs: `docker-compose logs`
2. Verify environment variables: `docker exec tripplanner-app env`
3. Test connectivity: `docker exec tripplanner-app curl localhost:8501`
4. Rebuild from scratch: `docker-compose down && docker-compose build --no-cache && docker-compose up`

---

## 🎉 Summary

You now have a fully containerized TripPlanner application!

**Quick Commands:**
```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose build --no-cache
```

**Access the app:** http://localhost:8501

Happy containerizing! 🐳✨
