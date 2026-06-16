# Deployment Guide - Document Intelligence Platform

## Table of Contents
- [Local Development with Docker](#local-development-with-docker)
- [AWS EKS Deployment](#aws-eks-deployment)
- [Infrastructure Setup](#infrastructure-setup)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring and Observability](#monitoring-and-observability)

---

## Local Development with Docker

### Prerequisites
- Docker Desktop or Docker Engine (20.10+)
- Docker Compose (v2.0+)
- 8GB RAM minimum

### Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd docuengine
```

2. **Create environment file:**
```bash
cp .env.example .env
# Edit .env and set your LLM API keys
```

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Run database migrations:**
```bash
docker-compose exec app alembic upgrade head
```

5. **Access the application:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Qdrant UI: http://localhost:6333/dashboard

### Services
- **app**: FastAPI application (port 8000)
- **postgres**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **qdrant**: Vector database (ports 6333, 6334)

### Useful Commands

```bash
# View logs
docker-compose logs -f app

# Rebuild and restart
docker-compose up --build -d

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Execute commands in container
docker-compose exec app python -m pytest
```

---

## AWS EKS Deployment

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│            AWS Cloud (us-east-1)            │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │  Application Load Balancer (ALB)      │ │
│  │  - SSL/TLS Termination                │ │
│  │  - Health Checks                      │ │
│  └─────────────┬─────────────────────────┘ │
│                │                             │
│  ┌─────────────▼─────────────────────────┐ │
│  │     EKS Cluster (Kubernetes)          │ │
│  │                                        │ │
│  │  ┌────────────────────────────────┐   │ │
│  │  │  FastAPI Pods (HPA: 3-10)      │   │ │
│  │  └────────────────────────────────┘   │ │
│  │  ┌────────────────────────────────┐   │ │
│  │  │  PostgreSQL StatefulSet         │   │ │
│  │  └────────────────────────────────┘   │ │
│  │  ┌────────────────────────────────┐   │ │
│  │  │  Redis Deployment               │   │ │
│  │  └────────────────────────────────┘   │ │
│  │  ┌────────────────────────────────┐   │ │
│  │  │  Qdrant StatefulSet            │   │ │
│  │  └────────────────────────────────┘   │ │
│  └────────────────────────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │  EBS Volumes (gp3)                  │  │
│  │  - PostgreSQL: 20GB                 │  │
│  │  - Redis: 5GB                       │  │
│  │  - Qdrant: 50GB                     │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │  S3 Bucket                          │  │
│  │  - Document Storage                 │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │  AWS Secrets Manager                │  │
│  │  - LLM API Keys                     │  │
│  │  - Database Credentials             │  │
│  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Prerequisites

- AWS CLI configured
- kubectl installed
- eksctl installed
- Helm 3 installed
- Docker installed
- AWS account with appropriate permissions

### Step 1: Create EKS Cluster

```bash
# Create EKS cluster
eksctl create cluster \
  --name docuengine-cluster \
  --region us-east-1 \
  --node-type t3.large \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed \
  --with-oidc

# Verify cluster
kubectl get nodes
```

### Step 2: Configure AWS Load Balancer Controller

```bash
# Add EKS repo
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Install AWS Load Balancer Controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=docuengine-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

### Step 3: Install EBS CSI Driver

```bash
# Create IAM policy for EBS CSI Driver
aws iam create-policy \
  --policy-name AmazonEKS_EBS_CSI_Driver_Policy \
  --policy-document file://ebs-csi-policy.json

# Create service account
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster docuengine-cluster \
  --attach-policy-arn arn:aws:iam::AWS_ACCOUNT_ID:policy/AmazonEKS_EBS_CSI_Driver_Policy \
  --approve

# Install EBS CSI Driver
kubectl apply -k "github.com/kubernetes-sigs/aws-ebs-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.25"
```

### Step 4: Create ECR Repository and Push Image

```bash
# Create ECR repository
aws ecr create-repository --repository-name docuengine --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t docuengine:latest .
docker tag docuengine:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/docuengine:latest

# Push to ECR
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/docuengine:latest
```

### Step 5: Configure Secrets

**Option 1: Using AWS Secrets Manager (Recommended)**

```bash
# Create secret in AWS Secrets Manager
aws secretsmanager create-secret \
  --name docuengine/prod/llm-keys \
  --secret-string '{
    "LLM_PROVIDER":"openai",
    "OPENAI_API_KEY":"sk-...",
    "SECRET_KEY":"your-secret-key",
    "DB_PASSWORD":"secure-password"
  }'

# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace
```

**Option 2: Using Kubernetes Secrets (For Testing)**

```bash
# Update k8s/secrets.yaml with your values
kubectl apply -f k8s/secrets.yaml
```

### Step 6: Deploy Application

```bash
# Update image in k8s/app-deployment.yaml with your ECR image URL

# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/qdrant-statefulset.yaml
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get pods -n docuengine
kubectl get svc -n docuengine
kubectl get ingress -n docuengine
```

### Step 7: Run Database Migrations

```bash
# Get app pod name
POD_NAME=$(kubectl get pods -n docuengine -l app=docuengine-app -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -n docuengine $POD_NAME -- alembic upgrade head
```

### Step 8: Access Application

```bash
# Get ALB DNS
kubectl get ingress -n docuengine docuengine-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Test health endpoint
curl http://<ALB_DNS>/health
```

---

## Infrastructure Setup

### Create S3 Bucket

```bash
# Create S3 bucket for document storage
aws s3 mb s3://document-intelligence-docs --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket document-intelligence-docs \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket document-intelligence-docs \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

### Create IAM Role for EKS Pods

```bash
# Create trust policy
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/<OIDC_ID>"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "oidc.eks.us-east-1.amazonaws.com/id/<OIDC_ID>:sub": "system:serviceaccount:docuengine:docuengine-sa"
      }
    }
  }]
}
EOF

# Create role
aws iam create-role \
  --role-name DocuengineEKSRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name DocuengineEKSRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name DocuengineEKSRole \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```

---

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to EKS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build and push image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: docuengine
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

      - name: Deploy to EKS
        run: |
          aws eks update-kubeconfig --name docuengine-cluster --region us-east-1
          kubectl set image deployment/docuengine-app app=${{ steps.login-ecr.outputs.registry }}/docuengine:${{ github.sha }} -n docuengine
          kubectl rollout status deployment/docuengine-app -n docuengine
```

---

## Monitoring and Observability

### Install Prometheus and Grafana

```bash
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Get Grafana password
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward to access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

### Application Logging with CloudWatch

```bash
# Install Fluent Bit
kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/quickstart/cwagent-fluent-bit-quickstart.yaml
```

---

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n docuengine
kubectl describe pod <POD_NAME> -n docuengine
kubectl logs <POD_NAME> -n docuengine
```

### Check Service Endpoints
```bash
kubectl get svc -n docuengine
kubectl get endpoints -n docuengine
```

### Check Ingress
```bash
kubectl describe ingress docuengine-ingress -n docuengine
```

### Database Connection Issues
```bash
kubectl exec -it -n docuengine <APP_POD> -- env | grep DATABASE
kubectl exec -it -n docuengine postgres-0 -- psql -U docuser -d document_intelligence
```

---

## Scaling

### Manual Scaling
```bash
kubectl scale deployment docuengine-app --replicas=5 -n docuengine
```

### Auto-scaling
The HPA is configured to scale between 3-10 replicas based on CPU (70%) and memory (80%) usage.

---

## Backup and Disaster Recovery

### PostgreSQL Backup
```bash
kubectl exec -n docuengine postgres-0 -- pg_dump -U docuser document_intelligence > backup.sql
```

### Restore
```bash
kubectl exec -i -n docuengine postgres-0 -- psql -U docuser document_intelligence < backup.sql
```

---

## Cost Optimization

- Use Spot Instances for non-critical workloads
- Right-size your node groups
- Implement cluster autoscaler
- Use gp3 volumes instead of gp2
- Enable EBS volume snapshots

---

## Security Best Practices

1. **Use AWS Secrets Manager** for sensitive data
2. **Enable Pod Security Policies**
3. **Use Network Policies** to restrict traffic
4. **Implement RBAC** for cluster access
5. **Enable audit logging** for Kubernetes API
6. **Use private subnets** for databases
7. **Enable encryption** for EBS volumes and S3
8. **Regular security patches** for nodes and containers

---

**Built by:** Philip Owusu
**Version:** 2.0.0
**Last Updated:** 2026-06-14
