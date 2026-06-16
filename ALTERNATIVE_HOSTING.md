# Alternative Hosting Options for Document Intelligence Platform

## 🎯 Overview

This guide covers alternative hosting options to AWS, ranging from **completely free** to **budget-friendly** solutions.

---

## 📊 Comparison Table

| Platform | Cost/Month | Kubernetes | Difficulty | Best For |
|----------|-----------|------------|------------|----------|
| **Local (Minikube/kind)** | $0 | ✅ | Easy | Development/Testing |
| **Docker Desktop** | $0 | ✅ | Very Easy | Local Development |
| **Google Cloud (GKE)** | $75-150 | ✅ | Medium | Production, $300 free credit |
| **Azure (AKS)** | $70-140 | ✅ | Medium | Production, $200 free credit |
| **DigitalOcean (DOKS)** | $40-80 | ✅ | Easy | Small Production |
| **Linode (LKE)** | $30-70 | ✅ | Easy | Budget Production |
| **Render** | $25-60 | ❌ | Very Easy | Simple Deployments |
| **Railway** | $20-50 | ❌ | Very Easy | Startups/MVPs |
| **Fly.io** | $20-40 | ❌ | Easy | Edge Computing |
| **Heroku** | $25-50 | ❌ | Very Easy | Quick Prototypes |

---

## 🆓 Option 1: Local Development (100% FREE)

Perfect for testing and development without any cloud costs.

### A. Using Docker Desktop (Recommended for Beginners)

**Setup:**
```bash
# 1. Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# 2. Enable Kubernetes in Docker Desktop
# Docker Desktop → Settings → Kubernetes → Enable Kubernetes

# 3. Verify
kubectl config use-context docker-desktop
kubectl get nodes

# 4. Deploy locally
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/qdrant-statefulset.yaml

# 5. Deploy app (using local image)
docker build -t docuengine:local .
kubectl apply -f k8s/app-deployment-local.yaml

# 6. Access app
kubectl port-forward -n docuengine svc/docuengine-service 8000:80
# Open: http://localhost:8000
```

**Pros:**
- ✅ Completely free
- ✅ No internet required
- ✅ Fast iteration
- ✅ Full Kubernetes features

**Cons:**
- ❌ Limited resources (your laptop)
- ❌ Not accessible from internet
- ❌ Data lost on restart (unless using volumes)

### B. Using Minikube

**Setup:**
```bash
# Install Minikube
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows
choco install minikube

# Start Minikube
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Deploy application
kubectl apply -f k8s/

# Access app
minikube service docuengine-service -n docuengine
```

### C. Using kind (Kubernetes in Docker)

**Setup:**
```bash
# Install kind
brew install kind  # macOS
# Or: curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64

# Create cluster
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 8080
    protocol: TCP
- role: worker
- role: worker
EOF

# Deploy application
kubectl apply -f k8s/

# Access via port-forward
kubectl port-forward -n docuengine svc/docuengine-service 8000:80
```

---

## 🌐 Option 2: Google Cloud Platform (GKE)

**FREE $300 credit for 90 days!**

### Cost Estimate
- GKE Cluster: ~$75/month
- 2x e2-medium nodes: ~$50/month
- Load Balancer: ~$20/month
- Storage: ~$10/month
- **Total: ~$155/month** (FREE for first 90 days)

### Setup

```bash
# 1. Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# 2. Initialize and login
gcloud init
gcloud auth login

# 3. Set project
gcloud config set project YOUR_PROJECT_ID

# 4. Create GKE cluster
gcloud container clusters create docuengine-cluster \
  --zone us-central1-a \
  --num-nodes 2 \
  --machine-type e2-medium \
  --disk-size 20 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 4

# 5. Get credentials
gcloud container clusters get-credentials docuengine-cluster --zone us-central1-a

# 6. Create container registry
gcloud artifacts repositories create docuengine \
  --repository-format=docker \
  --location=us-central1

# 7. Build and push image
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/docuengine/app:latest

# 8. Deploy application
kubectl apply -f k8s/
```

**Get Free Credit:**
1. Go to https://cloud.google.com/free
2. Sign up with credit card (won't be charged)
3. Get $300 credit for 90 days

---

## 🔵 Option 3: Microsoft Azure (AKS)

**FREE $200 credit for 30 days!**

### Cost Estimate
- AKS Cluster: Free (control plane)
- 2x Standard_B2s VMs: ~$60/month
- Load Balancer: ~$20/month
- Storage: ~$10/month
- **Total: ~$90/month** (FREE for first 30 days)

### Setup

```bash
# 1. Install Azure CLI
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# 2. Login
az login

# 3. Create resource group
az group create --name docuengine-rg --location eastus

# 4. Create AKS cluster
az aks create \
  --resource-group docuengine-rg \
  --name docuengine-cluster \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys

# 5. Get credentials
az aks get-credentials --resource-group docuengine-rg --name docuengine-cluster

# 6. Create container registry
az acr create --resource-group docuengine-rg --name docuengineacr --sku Basic

# 7. Attach ACR to AKS
az aks update --name docuengine-cluster --resource-group docuengine-rg --attach-acr docuengineacr

# 8. Build and push image
az acr build --registry docuengineacr --image docuengine:latest .

# 9. Deploy application
kubectl apply -f k8s/
```

**Get Free Credit:**
1. Go to https://azure.microsoft.com/free/
2. Sign up with credit card
3. Get $200 credit for 30 days

---

## 🌊 Option 4: DigitalOcean Kubernetes (DOKS)

**$200 credit for 60 days with referral!**

### Cost Estimate
- 2x Basic Droplets (2GB): ~$24/month
- Load Balancer: ~$12/month
- Volumes (50GB): ~$5/month
- **Total: ~$41/month**

### Setup

```bash
# 1. Install doctl CLI
brew install doctl  # macOS

# 2. Authenticate
doctl auth init

# 3. Create cluster
doctl kubernetes cluster create docuengine-cluster \
  --region nyc1 \
  --version latest \
  --node-pool "name=worker-pool;size=s-2vcpu-2gb;count=2"

# 4. Get credentials
doctl kubernetes cluster kubeconfig save docuengine-cluster

# 5. Create container registry
doctl registry create docuengine-registry

# 6. Login to registry
doctl registry login

# 7. Build and push image
docker build -t registry.digitalocean.com/docuengine-registry/app:latest .
docker push registry.digitalocean.com/docuengine-registry/app:latest

# 8. Deploy application
kubectl apply -f k8s/
```

**Get Free Credit:**
Use referral link: https://m.do.co/c/[referral-code] for $200 credit

**Why DigitalOcean?**
- ✅ Simplest Kubernetes setup
- ✅ Transparent pricing
- ✅ Great documentation
- ✅ Built-in monitoring
- ✅ No surprise charges

---

## 🟢 Option 5: Linode Kubernetes Engine (LKE)

**$100 credit for 60 days!**

### Cost Estimate
- 2x Linode 2GB: ~$20/month
- NodeBalancer: ~$10/month
- Volumes (50GB): ~$5/month
- **Total: ~$35/month**

### Setup

```bash
# 1. Install Linode CLI
pip3 install linode-cli

# 2. Configure
linode-cli configure

# 3. Create cluster
linode-cli lke cluster-create \
  --label docuengine-cluster \
  --region us-east \
  --k8s_version 1.28 \
  --node_pools.type g6-standard-2 \
  --node_pools.count 2

# 4. Get kubeconfig
linode-cli lke kubeconfig-view [cluster-id] --text | base64 -d > kubeconfig.yaml
export KUBECONFIG=kubeconfig.yaml

# 5. Deploy application
kubectl apply -f k8s/
```

**Get Free Credit:**
Sign up at https://www.linode.com/ with promo code

---

## 🚂 Option 6: Railway (No Kubernetes, Simple)

**$5/month free tier!**

Perfect for MVPs and simple deployments.

### Cost Estimate
- Hobby Plan: $5/month
- Pro Plan: $20/month (if you need more)

### Setup

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Create new project
railway init

# 4. Add PostgreSQL
railway add postgresql

# 5. Add Redis
railway add redis

# 6. Deploy application
railway up

# Railway automatically:
# - Builds your Docker image
# - Sets up domains
# - Manages secrets
# - Provides SSL
```

**Create `railway.json`:**
```json
{
  "build": {
    "builder": "dockerfile",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "numReplicas": 2,
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "on-failure"
  }
}
```

**Why Railway?**
- ✅ Simplest deployment
- ✅ No Kubernetes knowledge needed
- ✅ Automatic SSL
- ✅ Built-in databases
- ✅ $5/month free tier

---

## ✈️ Option 7: Fly.io

**Free tier available!**

### Cost Estimate
- Free tier: 3 VMs (256MB each)
- Paid: ~$20-40/month for production

### Setup

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Login
flyctl auth login

# 3. Launch app
flyctl launch

# 4. Create Postgres
flyctl postgres create

# 5. Attach database
flyctl postgres attach <db-name>

# 6. Deploy
flyctl deploy
```

**Create `fly.toml`:**
```toml
app = "docuengine"
primary_region = "sjc"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1
```

---

## 🎨 Option 8: Render

**Free tier available!**

### Cost Estimate
- Free: Limited resources
- Starter: $7/month per service
- Total: ~$25-50/month

### Setup

1. **Go to https://render.com**
2. **Connect GitHub repo**
3. **Create services:**
   - Web Service (FastAPI app)
   - PostgreSQL
   - Redis
4. **Deploy automatically**

**Create `render.yaml`:**
```yaml
services:
  - type: web
    name: docuengine-api
    env: docker
    dockerfilePath: ./Dockerfile
    plan: starter
    healthCheckPath: /health
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: docuengine-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: docuengine-redis
          type: redis
          property: connectionString

databases:
  - name: docuengine-db
    plan: starter
    databaseName: document_intelligence
    user: docuser

  - name: docuengine-redis
    plan: starter
```

---

## 🏆 Recommendation by Use Case

### For Learning/Development (FREE)
**Use:** Docker Desktop or Minikube
- No costs
- Full features
- Easy to reset

### For MVP/Startup ($20-40/month)
**Use:** Railway or Fly.io
- Simple setup
- Scales easily
- Great free tier

### For Small Production ($40-80/month)
**Use:** DigitalOcean or Linode
- Real Kubernetes
- Predictable pricing
- Good support

### For Enterprise/Scale ($75-150/month)
**Use:** GCP or Azure
- Advanced features
- Global reach
- Free credits available

---

## 💡 Money-Saving Tips

1. **Start with Free Tiers:**
   - Use GCP's $300 credit (90 days)
   - Then Azure's $200 credit (30 days)
   - Then DigitalOcean's $200 credit (60 days)
   - **Total: 180 days of FREE production hosting!**

2. **Use Spot/Preemptible Instances:**
   - 60-90% cheaper
   - Good for non-critical workloads

3. **Auto-shutdown Dev Environments:**
   ```bash
   # Stop cluster at night
   kubectl scale deployment --all --replicas=0 -n docuengine

   # Start in morning
   kubectl scale deployment --all --replicas=3 -n docuengine
   ```

4. **Use Docker Compose Locally:**
   - Development: `docker-compose up`
   - Production: Deploy to cloud

5. **Optimize Resources:**
   - Start small (1-2 nodes)
   - Scale only when needed
   - Use smaller instance types

---

## 🚀 Quick Start Recommendation

**I recommend starting with this progression:**

1. **Week 1-2: Local Development**
   ```bash
   docker-compose up -d
   ```
   - Free
   - Learn the application
   - Develop features

2. **Week 3-4: Railway ($5/month)**
   ```bash
   railway up
   ```
   - Get it on the internet
   - Share with users
   - Test in production

3. **Month 2-3: DigitalOcean ($40/month)**
   ```bash
   doctl kubernetes cluster create ...
   ```
   - Real Kubernetes experience
   - Scalable
   - Portfolio-worthy

4. **Month 4+: GCP/Azure (with free credits)**
   - Enterprise experience
   - Advanced features
   - Resume-worthy

---

## 📝 Next Steps

1. **Resolve AWS billing** (contact AWS support)
2. **Choose an alternative** from above
3. **Follow the setup guide** for your choice
4. **Deploy and test**
5. **Document your experience**

---

## 🆘 Need Help?

- **DigitalOcean:** https://www.digitalocean.com/community/tutorials
- **Railway:** https://docs.railway.app/
- **Fly.io:** https://fly.io/docs/
- **GCP:** https://cloud.google.com/kubernetes-engine/docs
- **Azure:** https://docs.microsoft.com/en-us/azure/aks/

---

**Built by:** Philip Owusu
**Last Updated:** 2026-06-14
