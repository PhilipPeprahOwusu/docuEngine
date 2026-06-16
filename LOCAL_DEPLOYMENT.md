# Local Kubernetes Deployment Guide

## 🎯 Deploy Document Intelligence Platform Locally (100% FREE)

This guide shows you how to run the full Kubernetes setup on your local machine without any cloud costs.

---

## Prerequisites

- **Docker Desktop** (includes Kubernetes) OR **Minikube**
- **8GB RAM** minimum (16GB recommended)
- **20GB free disk space**

---

## Option 1: Docker Desktop (Easiest)

### Step 1: Install Docker Desktop

Download and install from: https://www.docker.com/products/docker-desktop

### Step 2: Enable Kubernetes

1. Open Docker Desktop
2. Go to **Settings** → **Kubernetes**
3. Check **Enable Kubernetes**
4. Click **Apply & Restart**
5. Wait 2-3 minutes for Kubernetes to start

### Step 3: Verify Installation

```bash
# Check if kubectl is working
kubectl version --client

# Check nodes
kubectl get nodes
# Should show: docker-desktop   Ready    control-plane   1m    v1.28.x
```

### Step 4: Build Docker Image Locally

```bash
# Navigate to project directory
cd /Users/philipowusu/Development/docuengine

# Build image (this stays local, no push needed)
docker build -t docuengine:local .

# Verify image
docker images | grep docuengine
```

### Step 5: Update Configuration for Local Use

```bash
# Update configmap for local services
cat > k8s/configmap-local.yaml <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: docuengine-config
  namespace: docuengine
data:
  PROJECT_NAME: "Document Intelligence Agent Platform"
  ENVIRONMENT: "local"
  DEBUG: "True"
  POSTGRES_DB: "document_intelligence"
  POSTGRES_USER: "docuser"
  REDIS_URL: "redis://redis-service:6379"
  QDRANT_URL: "http://qdrant-service:6333"
EOF

# Create a simplified secrets file
cat > k8s/secrets-local.yaml <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: docuengine-secrets
  namespace: docuengine
type: Opaque
stringData:
  DB_PASSWORD: "localpass123"
  DATABASE_URL: "postgresql://docuser:localpass123@postgres-service:5432/document_intelligence"
  SECRET_KEY: "local-dev-secret-key-change-in-production"
  LLM_PROVIDER: "openai"
  OPENAI_API_KEY: "your-key-here"  # Add your actual key
  GEMINI_API_KEY: ""
  ANTHROPIC_API_KEY: ""
EOF
```

### Step 6: Deploy Everything

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply configuration
kubectl apply -f k8s/configmap-local.yaml
kubectl apply -f k8s/secrets-local.yaml

# Deploy databases (these work as-is)
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/qdrant-statefulset.yaml

# Wait for databases to be ready (2-3 minutes)
kubectl wait --for=condition=ready pod -l app=postgres -n docuengine --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n docuengine --timeout=300s
kubectl wait --for=condition=ready pod -l app=qdrant -n docuengine --timeout=300s

# Deploy application (using local image)
kubectl apply -f k8s/app-deployment-local.yaml

# Wait for app to be ready
kubectl wait --for=condition=ready pod -l app=docuengine-app -n docuengine --timeout=300s
```

### Step 7: Run Database Migrations

```bash
# Get app pod name
POD_NAME=$(kubectl get pods -n docuengine -l app=docuengine-app -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -n docuengine $POD_NAME -- alembic upgrade head
```

### Step 8: Access Your Application

**Option A: Port Forward (Recommended)**
```bash
# Forward port to localhost
kubectl port-forward -n docuengine svc/docuengine-service 8000:80

# Access in browser:
# http://localhost:8000
# http://localhost:8000/docs (API documentation)
```

**Option B: NodePort**
```bash
# Access directly via NodePort
# http://localhost:30080
```

---

## Option 2: Minikube

### Step 1: Install Minikube

**macOS:**
```bash
brew install minikube
```

**Linux:**
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**Windows:**
```powershell
choco install minikube
```

### Step 2: Start Minikube

```bash
# Start with adequate resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Set kubectl to use minikube
kubectl config use-context minikube
```

### Step 3: Build Image in Minikube

```bash
# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)

# Build image
cd /Users/philipowusu/Development/docuengine
docker build -t docuengine:local .

# Verify
docker images | grep docuengine
```

### Step 4: Deploy Application

```bash
# Follow the same deployment steps as Docker Desktop
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap-local.yaml
kubectl apply -f k8s/secrets-local.yaml
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/qdrant-statefulset.yaml

# Wait for databases
sleep 60

# Deploy app
kubectl apply -f k8s/app-deployment-local.yaml
```

### Step 5: Access Application

```bash
# Get the service URL
minikube service docuengine-service -n docuengine --url

# Or use port forwarding
kubectl port-forward -n docuengine svc/docuengine-service 8000:80
```

### Step 6: Access Kubernetes Dashboard

```bash
# Open dashboard
minikube dashboard
```

---

## 🔍 Verify Everything Works

### Check All Pods

```bash
kubectl get pods -n docuengine

# Expected output:
# NAME                              READY   STATUS    RESTARTS   AGE
# docuengine-app-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
# postgres-0                        1/1     Running   0          5m
# qdrant-0                          1/1     Running   0          5m
# redis-xxxxxxxxxx-xxxxx            1/1     Running   0          5m
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs  # macOS
# Or visit: http://localhost:8000/docs in browser
```

### Check Logs

```bash
# View app logs
kubectl logs -n docuengine -l app=docuengine-app --tail=50

# Follow logs (live)
kubectl logs -n docuengine -l app=docuengine-app -f
```

---

## 🔄 Development Workflow

### Making Code Changes

```bash
# 1. Make your code changes

# 2. Rebuild image
docker build -t docuengine:local .

# 3. Restart deployment (for Docker Desktop)
kubectl rollout restart deployment/docuengine-app -n docuengine

# 3. For Minikube, rebuild in minikube context
eval $(minikube docker-env)
docker build -t docuengine:local .
kubectl rollout restart deployment/docuengine-app -n docuengine

# 4. Wait for new pods
kubectl rollout status deployment/docuengine-app -n docuengine
```

### Quick Iteration Alternative

For faster development, use docker-compose instead:

```bash
# Start everything
docker-compose up -d

# Make changes
# Code changes auto-reload with --reload flag

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

---

## 🛠️ Useful Commands

### View All Resources

```bash
kubectl get all -n docuengine
```

### Connect to Database

```bash
kubectl exec -it postgres-0 -n docuengine -- psql -U docuser -d document_intelligence
```

### Connect to Redis

```bash
kubectl exec -it $(kubectl get pod -n docuengine -l app=redis -o jsonpath='{.items[0].metadata.name}') -n docuengine -- redis-cli
```

### Access Qdrant Dashboard

```bash
kubectl port-forward -n docuengine qdrant-0 6333:6333
# Open: http://localhost:6333/dashboard
```

### View Resource Usage

```bash
# Requires metrics-server
kubectl top pods -n docuengine
kubectl top nodes
```

---

## 🐛 Troubleshooting

### Pods Stuck in Pending

```bash
# Check events
kubectl get events -n docuengine --sort-by='.lastTimestamp'

# Increase resources
# Docker Desktop: Settings → Resources → Increase CPU/Memory
# Minikube: minikube delete && minikube start --cpus=4 --memory=8192
```

### Image Pull Errors

```bash
# Verify image exists locally
docker images | grep docuengine

# Rebuild if needed
docker build -t docuengine:local .

# For Minikube, ensure you're using minikube's Docker
eval $(minikube docker-env)
docker build -t docuengine:local .
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
kubectl get pods -n docuengine -l app=postgres

# Check logs
kubectl logs postgres-0 -n docuengine

# Verify connection string
kubectl exec -it postgres-0 -n docuengine -- psql -U docuser -d document_intelligence -c "SELECT 1;"
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
kubectl port-forward -n docuengine svc/docuengine-service 8080:80
```

---

## 🧹 Clean Up

### Remove Application

```bash
# Delete namespace (removes everything)
kubectl delete namespace docuengine
```

### Stop Kubernetes

**Docker Desktop:**
- Settings → Kubernetes → Uncheck "Enable Kubernetes"

**Minikube:**
```bash
# Stop cluster
minikube stop

# Delete cluster
minikube delete
```

### Remove Docker Images

```bash
# Remove local images
docker rmi docuengine:local
docker rmi postgres:15-alpine
docker rmi redis:7-alpine
docker rmi qdrant/qdrant:latest
```

---

## 💡 Tips for Local Development

1. **Use docker-compose for rapid development:**
   ```bash
   docker-compose up -d
   ```
   - Faster iteration
   - Simpler debugging
   - Direct log access

2. **Use Kubernetes for production-like testing:**
   - Test autoscaling
   - Test health checks
   - Test service discovery

3. **Resource Limits:**
   - Start with low replicas (1-2)
   - Reduce memory limits if needed
   - Use Docker Desktop resource limits

4. **Persistent Data:**
   - Data survives pod restarts
   - Stored in PersistentVolumes
   - Clean with `kubectl delete pvc --all -n docuengine`

---

## 🎯 Next Steps

1. ✅ Run locally to learn and develop
2. ✅ Use Railway or Fly.io for first cloud deployment ($5-20/month)
3. ✅ Move to DigitalOcean for production ($40/month)
4. ✅ Use GCP/Azure free credits when ready for scale

---

## 📚 Additional Resources

- [Docker Desktop Kubernetes](https://docs.docker.com/desktop/kubernetes/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Lens IDE](https://k8slens.dev/) - Great Kubernetes UI

---

**You're now running a production-like Kubernetes cluster on your laptop for FREE!** 🎉

**Built by:** Philip Owusu
**Last Updated:** 2026-06-14
