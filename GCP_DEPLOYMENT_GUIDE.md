# Google Cloud Platform (GKE) Deployment Guide

## 🎯 Complete Guide to Deploy on Google Kubernetes Engine

**Benefits of GCP:**
- ✅ **$300 FREE credit** for 90 days
- ✅ Google invented Kubernetes (best platform for it)
- ✅ Excellent documentation
- ✅ Free tier continues after trial
- ✅ Global infrastructure

**Estimated Cost:** ~$120/month (FREE with credit)

---

## 📋 Prerequisites

- Credit card (for verification, won't be charged during free trial)
- Terminal/Command Line
- 30-45 minutes of time

---

## Step 1: Create Google Cloud Account & Get $300 Credit

### 1.1 Sign Up for Free Trial

1. **Go to:** https://cloud.google.com/free
2. **Click:** "Get started for free"
3. **Sign in** with your Google account (or create one)
4. **Select your country** and agree to terms
5. **Enter payment info** (required but won't be charged)
6. **Get $300 credit!** ✅

**Important Notes:**
- ✅ You won't be charged automatically after trial
- ✅ Credit expires in 90 days
- ✅ You must manually upgrade to paid to be charged
- ✅ Alerts notify you when approaching limit

### 1.2 Create a New Project

1. **Go to:** https://console.cloud.google.com
2. **Click:** Select a project → New Project
3. **Project name:** `docuengine` (or whatever you prefer)
4. **Click:** Create
5. **Select** your new project from the dropdown

**Note your Project ID:** You'll need this later (looks like: `docuengine-123456`)

---

## Step 2: Install Google Cloud CLI

### macOS
```bash
# Using Homebrew (recommended)
brew install google-cloud-sdk

# Or download installer
# https://cloud.google.com/sdk/docs/install
```

### Linux
```bash
# Download and install
curl https://sdk.cloud.google.com | bash

# Restart shell
exec -l $SHELL

# Initialize
gcloud init
```

### Windows
```powershell
# Download installer from:
# https://cloud.google.com/sdk/docs/install

# Or using Chocolatey
choco install gcloudsdk
```

### Verify Installation
```bash
gcloud version

# Expected output:
# Google Cloud SDK 450.0.0
# ...
```

---

## Step 3: Initialize and Configure GCloud

```bash
# Initialize gcloud
gcloud init

# Follow prompts:
# 1. Log in to your Google account
# 2. Select your project (docuengine)
# 3. Select default region (us-central1)

# Verify configuration
gcloud config list

# Set project explicitly (if needed)
gcloud config set project YOUR_PROJECT_ID

# Set default region
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
```

---

## Step 4: Enable Required APIs

```bash
# Enable Kubernetes Engine API
gcloud services enable container.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Artifact Registry API (newer, recommended)
gcloud services enable artifactregistry.googleapis.com

# Enable Compute Engine API
gcloud services enable compute.googleapis.com

# This takes 1-2 minutes
```

---

## Step 5: Install kubectl (if not already installed)

```bash
# Install kubectl via gcloud
gcloud components install kubectl

# Verify installation
kubectl version --client
```

---

## Step 6: Create GKE Cluster

### Option A: Quick Start (Autopilot - Recommended for Beginners)

**Autopilot = Google manages everything, you just deploy**

```bash
# Create Autopilot cluster (simplest, most cost-effective)
gcloud container clusters create-auto docuengine-cluster \
  --region=us-central1 \
  --project=$(gcloud config get-value project)

# This takes 5-10 minutes
# Output shows cluster creation progress
```

**Autopilot Benefits:**
- ✅ Auto-scales nodes
- ✅ Auto-updates
- ✅ Pay only for pods (not nodes)
- ✅ Cheaper than standard
- ✅ Less management

### Option B: Standard Cluster (More Control)

```bash
# Create standard cluster
gcloud container clusters create docuengine-cluster \
  --zone=us-central1-a \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --disk-size=20 \
  --disk-type=pd-standard \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=4 \
  --enable-autorepair \
  --enable-autoupgrade \
  --project=$(gcloud config get-value project)

# This takes 5-10 minutes
```

### Verify Cluster Creation

```bash
# Get cluster credentials
gcloud container clusters get-credentials docuengine-cluster \
  --region=us-central1  # or --zone=us-central1-a for standard

# Verify cluster
kubectl get nodes

# Expected output:
# NAME                                    STATUS   ROLES    AGE   VERSION
# gke-docuengine-cluster-...              Ready    <none>   2m    v1.28.x
```

---

## Step 7: Set Up Container Registry

### Option A: Artifact Registry (Recommended - Modern)

```bash
# Create Artifact Registry repository
gcloud artifacts repositories create docuengine \
  --repository-format=docker \
  --location=us-central1 \
  --description="Document Intelligence Platform"

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### Option B: Container Registry (Legacy but simpler)

```bash
# Configure Docker authentication
gcloud auth configure-docker

# GCR is automatically enabled
```

---

## Step 8: Build and Push Docker Image

### Get Your Project ID
```bash
# Get project ID
PROJECT_ID=$(gcloud config get-value project)
echo "Your Project ID: $PROJECT_ID"
```

### Build and Push to Artifact Registry (Recommended)

```bash
# Navigate to project directory
cd /Users/philipowusu/Development/docuengine

# Build image
docker build -t docuengine:latest .

# Tag for Artifact Registry
docker tag docuengine:latest \
  us-central1-docker.pkg.dev/$PROJECT_ID/docuengine/app:latest

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/$PROJECT_ID/docuengine/app:latest
```

### OR Build and Push to Container Registry

```bash
# Tag for GCR
docker tag docuengine:latest gcr.io/$PROJECT_ID/docuengine:latest

# Push to GCR
docker push gcr.io/$PROJECT_ID/docuengine:latest
```

### OR Use Google Cloud Build (No Local Docker Needed!)

```bash
# Build in the cloud (no local Docker required)
gcloud builds submit --tag gcr.io/$PROJECT_ID/docuengine:latest

# This builds your image in Google Cloud
# Great for slow local machines or CI/CD
```

---

## Step 9: Update Kubernetes Manifests for GCP

### Create GCP-specific secrets

```bash
# Create secrets file
cat > k8s/secrets-gcp.yaml <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: docuengine-secrets
  namespace: docuengine
type: Opaque
stringData:
  DB_PASSWORD: "$(openssl rand -base64 32)"
  DATABASE_URL: "postgresql://docuser:CHANGE_ME@postgres-service:5432/document_intelligence"
  SECRET_KEY: "$(openssl rand -base64 32)"

  # Add your LLM API key here
  LLM_PROVIDER: "openai"
  OPENAI_API_KEY: "sk-your-key-here"  # CHANGE THIS
  GEMINI_API_KEY: ""
  ANTHROPIC_API_KEY: ""

  # GCP specific (optional)
  GOOGLE_APPLICATION_CREDENTIALS: ""
EOF

# IMPORTANT: Edit the file and add your OpenAI key
nano k8s/secrets-gcp.yaml  # or use your preferred editor
```

### Update App Deployment with GCP Image

```bash
# Get your project ID
PROJECT_ID=$(gcloud config get-value project)

# Update deployment to use your GCR image
cat > k8s/app-deployment-gcp.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docuengine-app
  namespace: docuengine
spec:
  replicas: 2
  selector:
    matchLabels:
      app: docuengine-app
  template:
    metadata:
      labels:
        app: docuengine-app
    spec:
      containers:
      - name: app
        image: gcr.io/$PROJECT_ID/docuengine:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - configMapRef:
            name: docuengine-config
        - secretRef:
            name: docuengine-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: docuengine-service
  namespace: docuengine
spec:
  type: LoadBalancer
  selector:
    app: docuengine-app
  ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
EOF
```

---

## Step 10: Deploy Application to GKE

```bash
# Apply all manifests in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets-gcp.yaml

# Deploy databases
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/qdrant-statefulset.yaml

# Wait for databases to be ready (3-5 minutes)
echo "Waiting for databases to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n docuengine --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n docuengine --timeout=300s
kubectl wait --for=condition=ready pod -l app=qdrant -n docuengine --timeout=300s

echo "Databases ready! Deploying application..."

# Deploy application
kubectl apply -f k8s/app-deployment-gcp.yaml

# Wait for app to be ready
kubectl wait --for=condition=ready pod -l app=docuengine-app -n docuengine --timeout=300s

# Deploy auto-scaling
kubectl apply -f k8s/hpa.yaml
```

---

## Step 11: Run Database Migrations

```bash
# Get app pod name
POD_NAME=$(kubectl get pods -n docuengine -l app=docuengine-app -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -n docuengine $POD_NAME -- alembic upgrade head

echo "Migrations complete!"
```

---

## Step 12: Get Your Application URL

```bash
# Get the LoadBalancer IP (takes 2-3 minutes to provision)
echo "Waiting for LoadBalancer IP..."
kubectl get svc docuengine-service -n docuengine -w

# Or get it directly
EXTERNAL_IP=$(kubectl get svc docuengine-service -n docuengine -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Your application is available at:"
echo "http://$EXTERNAL_IP"
echo "API Docs: http://$EXTERNAL_IP/docs"

# Test the API
curl http://$EXTERNAL_IP/health
```

---

## Step 13: Set Up Domain (Optional)

### Create DNS Record

1. **Go to Cloud DNS** (or use your domain provider)
2. **Create A Record:**
   - Name: `api.yourdomain.com`
   - Type: `A`
   - IP: `[Your LoadBalancer IP]`
   - TTL: `300`

### Update Service with Domain

```bash
# No changes needed - LoadBalancer works with any domain pointed to its IP
```

---

## 🎛️ Google Cloud Console Dashboard

### Access GKE Dashboard

1. **Go to:** https://console.cloud.google.com/kubernetes
2. **Select:** your cluster
3. **View:**
   - Workloads (pods, deployments)
   - Services & Ingress
   - Applications
   - Storage
   - Logs

### View Logs

```bash
# Via command line
kubectl logs -n docuengine -l app=docuengine-app --tail=100

# Or in Cloud Console:
# Navigation Menu → Kubernetes Engine → Workloads → Select pod → Logs
```

---

## 💰 Monitor Your Spending

### Check Current Costs

```bash
# Via gcloud
gcloud billing accounts list

# View budget
gcloud billing budgets list --billing-account=YOUR_BILLING_ACCOUNT_ID
```

### Set Up Budget Alerts

1. **Go to:** https://console.cloud.google.com/billing
2. **Click:** Budgets & alerts
3. **Create budget:**
   - Name: `Monthly Budget`
   - Amount: `$100`
   - Alerts at: 50%, 75%, 90%, 100%

### View Free Trial Status

1. **Go to:** https://console.cloud.google.com/billing
2. **See:** Free trial credits remaining
3. **Days left:** Countdown shown

---

## 🔧 Useful GCP/GKE Commands

### Cluster Management

```bash
# List clusters
gcloud container clusters list

# Get cluster info
gcloud container clusters describe docuengine-cluster --region=us-central1

# Resize cluster (for standard clusters)
gcloud container clusters resize docuengine-cluster \
  --num-nodes=3 \
  --zone=us-central1-a

# Upgrade cluster
gcloud container clusters upgrade docuengine-cluster --region=us-central1

# Delete cluster (careful!)
gcloud container clusters delete docuengine-cluster --region=us-central1
```

### View Logs in Cloud Logging

```bash
# Recent logs for your app
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=docuengine" \
  --limit 50 \
  --format json

# Or use Cloud Console:
# Navigation Menu → Logging → Logs Explorer
```

### SSH into Node

```bash
# List nodes
kubectl get nodes

# SSH into node
gcloud compute ssh [NODE_NAME] --zone=us-central1-a
```

---

## 📊 Monitoring with Google Cloud

### Enable GKE Monitoring

```bash
# GKE Autopilot has monitoring enabled by default

# For standard clusters, enable if needed:
gcloud container clusters update docuengine-cluster \
  --enable-cloud-logging \
  --enable-cloud-monitoring \
  --zone=us-central1-a
```

### Access Monitoring Dashboard

1. **Go to:** https://console.cloud.google.com/monitoring
2. **View:**
   - Metrics Explorer
   - Dashboards
   - Uptime checks
   - Alerting

### Create Uptime Check

1. **Monitoring → Uptime checks → Create Uptime Check**
2. **Settings:**
   - Protocol: HTTP
   - Resource Type: URL
   - Hostname: Your LoadBalancer IP
   - Path: `/health`
   - Check frequency: 1 minute

---

## 🔒 Security Best Practices

### Use Google Secret Manager (Recommended)

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Create secrets
echo -n "your-openai-key" | \
  gcloud secrets create openai-api-key --data-file=-

# Grant GKE access
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:YOUR_PROJECT_ID.svc.id.goog[docuengine/default]" \
  --role="roles/secretmanager.secretAccessor"
```

### Enable Binary Authorization

```bash
# Ensure only verified images run
gcloud container clusters update docuengine-cluster \
  --enable-binauthz \
  --region=us-central1
```

### Enable Workload Identity (Best Practice)

```bash
# Create service account
gcloud iam service-accounts create docuengine-sa

# Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:docuengine-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# Bind to Kubernetes service account
gcloud iam service-accounts add-iam-policy-binding \
  docuengine-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:YOUR_PROJECT_ID.svc.id.goog[docuengine/default]"
```

---

## 🚀 Scaling Your Application

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment docuengine-app --replicas=5 -n docuengine

# For standard cluster, scale nodes
gcloud container clusters resize docuengine-cluster \
  --num-nodes=4 \
  --zone=us-central1-a
```

### Auto-scaling (Already Configured via HPA)

```bash
# View HPA status
kubectl get hpa -n docuengine

# Adjust HPA
kubectl edit hpa docuengine-hpa -n docuengine
```

---

## 🐛 Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n docuengine

# Describe pod
kubectl describe pod <pod-name> -n docuengine

# Check events
kubectl get events -n docuengine --sort-by='.lastTimestamp'
```

### Image Pull Errors

```bash
# Verify image exists
gcloud container images list --repository=gcr.io/$PROJECT_ID

# Check if GKE can pull
gcloud container images describe gcr.io/$PROJECT_ID/docuengine:latest
```

### LoadBalancer Not Getting IP

```bash
# Check service
kubectl describe svc docuengine-service -n docuengine

# Check firewall rules
gcloud compute firewall-rules list

# Usually takes 2-3 minutes, be patient!
```

### Database Connection Issues

```bash
# Check if postgres is running
kubectl get pods -n docuengine -l app=postgres

# Test connection
kubectl exec -it postgres-0 -n docuengine -- \
  psql -U docuser -d document_intelligence -c "SELECT 1;"
```

---

## 💾 Backup and Disaster Recovery

### Backup PostgreSQL

```bash
# Backup to file
kubectl exec postgres-0 -n docuengine -- \
  pg_dump -U docuser document_intelligence > backup.sql

# Upload to Google Cloud Storage
gsutil mb gs://docuengine-backups/
gsutil cp backup.sql gs://docuengine-backups/backup-$(date +%Y%m%d).sql
```

### Automated Backups with CronJob

```bash
# Create backup CronJob (optional)
cat > k8s/backup-cronjob.yaml <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: docuengine
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -U docuser -h postgres-service document_intelligence > /backup/backup-\$(date +%Y%m%d).sql
              # Upload to GCS here
          restartPolicy: OnFailure
EOF

kubectl apply -f k8s/backup-cronjob.yaml
```

---

## 🧹 Clean Up (When Done Testing)

### Delete Application

```bash
# Delete namespace (removes all resources)
kubectl delete namespace docuengine
```

### Delete Cluster

```bash
# Delete GKE cluster
gcloud container clusters delete docuengine-cluster --region=us-central1

# Confirm deletion when prompted
```

### Delete Container Images

```bash
# Delete from Artifact Registry
gcloud artifacts docker images delete \
  us-central1-docker.pkg.dev/$PROJECT_ID/docuengine/app:latest

# Or delete entire repository
gcloud artifacts repositories delete docuengine \
  --location=us-central1
```

### Delete Project (Nuclear Option)

```bash
# This deletes EVERYTHING in the project
gcloud projects delete $PROJECT_ID
```

---

## 💡 Cost Optimization Tips

1. **Use Autopilot** - Pay only for pods, not nodes
2. **Use Preemptible Nodes** - 80% cheaper for dev/test
3. **Enable Cluster Autoscaler** - Scale down when not needed
4. **Use Committed Use Discounts** - 57% discount for 1-year commit
5. **Stop/Start Clusters** for dev:
   ```bash
   # Resize to 0 nodes (stops incurring costs)
   gcloud container clusters resize docuengine-cluster --num-nodes=0

   # Resize back when needed
   gcloud container clusters resize docuengine-cluster --num-nodes=2
   ```

6. **Monitor with Budgets** - Set alerts at 50%, 75%, 90%

---

## 📊 Expected Costs Breakdown

**Autopilot Cluster:**
- Control plane: FREE (included)
- Pods: ~$70/month (2 replicas)
- Load Balancer: ~$20/month
- Storage (70GB): ~$7/month
- Networking: ~$10/month
- **Total: ~$107/month**

**Standard Cluster:**
- Control plane: $0.10/hour = ~$73/month
- 2× e2-medium nodes: ~$48/month
- Load Balancer: ~$20/month
- Storage: ~$7/month
- **Total: ~$148/month**

**With $300 credit:** FREE for 2-3 months!

---

## 🎯 Next Steps

1. ✅ Deploy and test on GKE
2. ✅ Set up monitoring and alerts
3. ✅ Configure custom domain
4. ✅ Set up CI/CD with Cloud Build
5. ✅ Implement backups
6. ✅ Add SSL/TLS

---

## 📚 Additional Resources

- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [GCP Free Tier](https://cloud.google.com/free)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)

---

**Congratulations!** 🎉 You now have your Document Intelligence Platform running on Google Kubernetes Engine with $300 in free credits!

**Built by:** Philip Owusu
**Last Updated:** 2026-06-15
