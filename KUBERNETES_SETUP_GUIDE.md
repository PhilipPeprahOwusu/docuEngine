# Kubernetes Setup Guide - Complete Walkthrough

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Install Required Tools](#install-required-tools)
3. [Configure AWS Account](#configure-aws-account)
4. [Create EKS Cluster](#create-eks-cluster)
5. [Deploy Application](#deploy-application)
6. [Verify Deployment](#verify-deployment)
7. [Access Your Application](#access-your-application)
8. [Common Issues & Solutions](#common-issues--solutions)

---

## Prerequisites

Before starting, ensure you have:
- ✅ AWS Account with admin access
- ✅ Credit card for AWS (free tier available)
- ✅ Terminal/Command Line access
- ✅ At least 8GB RAM on your machine
- ✅ ~30-60 minutes of time

**Estimated AWS Costs:** ~$150-200/month for production setup

---

## Install Required Tools

### Step 1: Install AWS CLI

**macOS:**
```bash
# Using Homebrew
brew install awscli

# Verify installation
aws --version
```

**Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

**Windows:**
Download and run: https://awscli.amazonaws.com/AWSCLIV2.msi

### Step 2: Install kubectl

**macOS:**
```bash
brew install kubectl

# Verify installation
kubectl version --client
```

**Linux:**
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

**Windows:**
```powershell
# Using Chocolatey
choco install kubernetes-cli

# Or download from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
```

### Step 3: Install eksctl

**macOS:**
```bash
brew tap weaveworks/tap
brew install weaveworks/tap/eksctl

# Verify installation
eksctl version
```

**Linux:**
```bash
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Verify installation
eksctl version
```

**Windows:**
```powershell
# Using Chocolatey
choco install eksctl

# Verify installation
eksctl version
```

### Step 4: Install Docker

**macOS:**
- Download Docker Desktop: https://www.docker.com/products/docker-desktop

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

**Windows:**
- Download Docker Desktop: https://www.docker.com/products/docker-desktop

### Step 5: Install Helm (Optional but Recommended)

**macOS:**
```bash
brew install helm
```

**Linux:**
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Windows:**
```powershell
choco install kubernetes-helm
```

---

## Configure AWS Account

### Step 1: Create IAM User

1. **Login to AWS Console:** https://console.aws.amazon.com
2. **Navigate to IAM:** Services → IAM
3. **Create User:**
   - Click "Users" → "Add users"
   - Username: `eks-admin`
   - Access type: ✅ Programmatic access
   - Click "Next: Permissions"

4. **Attach Policies:**
   - Click "Attach existing policies directly"
   - Select these policies:
     - ✅ `AdministratorAccess` (for simplicity; use more restrictive in production)
   - Click "Next: Tags" → "Next: Review" → "Create user"

5. **Save Credentials:**
   - **IMPORTANT:** Download the CSV or copy:
     - Access Key ID
     - Secret Access Key
   - You won't be able to see the Secret Access Key again!

### Step 2: Configure AWS CLI

```bash
# Run AWS configure
aws configure

# You'll be prompted for:
AWS Access Key ID: [paste your Access Key ID]
AWS Secret Access Key: [paste your Secret Access Key]
Default region name: us-east-1
Default output format: json

# Verify configuration
aws sts get-caller-identity
```

You should see output like:
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/eks-admin"
}
```

---

## Create EKS Cluster

### Option A: Quick Setup (Recommended for Learning)

Create a simple cluster configuration file:

```bash
cat > eks-cluster-config.yaml <<EOF
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: docuengine-cluster
  region: us-east-1
  version: "1.28"

managedNodeGroups:
  - name: docuengine-nodes
    instanceType: t3.medium
    desiredCapacity: 2
    minSize: 1
    maxSize: 4
    volumeSize: 20
    ssh:
      allow: false
    labels:
      role: worker
    tags:
      Environment: production
      Application: docuengine

iam:
  withOIDC: true
EOF
```

Create the cluster:
```bash
# This takes 15-20 minutes
eksctl create cluster -f eks-cluster-config.yaml

# Output will show cluster creation progress
```

### Option B: Production Setup (Full Featured)

```bash
cat > eks-cluster-production.yaml <<EOF
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: docuengine-cluster
  region: us-east-1
  version: "1.28"

vpc:
  cidr: 10.0.0.0/16
  nat:
    gateway: HighlyAvailable

managedNodeGroups:
  - name: general-workloads
    instanceType: t3.large
    desiredCapacity: 3
    minSize: 2
    maxSize: 5
    volumeSize: 50
    privateNetworking: true
    labels:
      role: general
    tags:
      Environment: production

  - name: spot-workloads
    instanceTypes: ["t3.medium", "t3.large"]
    spot: true
    desiredCapacity: 2
    minSize: 0
    maxSize: 4
    labels:
      role: spot
    tags:
      Environment: production

addons:
  - name: vpc-cni
  - name: coredns
  - name: kube-proxy
  - name: aws-ebs-csi-driver

iam:
  withOIDC: true

cloudWatch:
  clusterLogging:
    enableTypes: ["*"]
EOF

# Create cluster
eksctl create cluster -f eks-cluster-production.yaml
```

### Verify Cluster Creation

```bash
# Check cluster status
eksctl get cluster --region us-east-1

# Configure kubectl
aws eks update-kubeconfig --name docuengine-cluster --region us-east-1

# Verify kubectl access
kubectl get nodes

# You should see something like:
# NAME                             STATUS   ROLES    AGE   VERSION
# ip-10-0-1-123.ec2.internal       Ready    <none>   5m    v1.28.x
# ip-10-0-2-456.ec2.internal       Ready    <none>   5m    v1.28.x
```

---

## Deploy Application

### Step 1: Install AWS Load Balancer Controller

```bash
# Add IAM policy
curl -o iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.6.0/docs/install/iam_policy.json

aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam-policy.json

# Create service account
eksctl create iamserviceaccount \
  --cluster=docuengine-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/AWSLoadBalancerControllerIAMPolicy \
  --approve \
  --region us-east-1

# Install controller with Helm
helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=docuengine-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller

# Verify installation
kubectl get deployment -n kube-system aws-load-balancer-controller
```

### Step 2: Build and Push Docker Image to ECR

```bash
# Get your AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=us-east-1

# Create ECR repository
aws ecr create-repository \
    --repository-name docuengine \
    --region $AWS_REGION

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build image (from your project root)
cd /Users/philipowusu/Development/docuengine
docker build -t docuengine:latest .

# Tag and push
docker tag docuengine:latest \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/docuengine:latest

docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/docuengine:latest
```

### Step 3: Create Secrets

```bash
# Get your AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Update k8s/secrets.yaml with your actual values
# Then apply secrets
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
```

**IMPORTANT:** Edit `k8s/secrets.yaml` and add your:
- Database password
- LLM API key (OpenAI/Gemini/Anthropic)
- AWS credentials (if using S3)
- Secret key for JWT

### Step 4: Update Deployment with Your ECR Image

```bash
# Edit k8s/app-deployment.yaml
# Replace <AWS_ACCOUNT_ID> and <AWS_REGION> with your values

# Or use sed to update automatically
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=us-east-1

sed -i.bak "s|<AWS_ACCOUNT_ID>|$AWS_ACCOUNT_ID|g" k8s/app-deployment.yaml
sed -i.bak "s|<AWS_REGION>|$AWS_REGION|g" k8s/app-deployment.yaml
sed -i.bak "s|<AWS_ACCOUNT_ID>|$AWS_ACCOUNT_ID|g" k8s/ingress.yaml
sed -i.bak "s|<AWS_REGION>|$AWS_REGION|g" k8s/ingress.yaml
```

### Step 5: Deploy All Components

```bash
# Apply all Kubernetes manifests in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy databases
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/qdrant-statefulset.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n docuengine --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n docuengine --timeout=300s
kubectl wait --for=condition=ready pod -l app=qdrant -n docuengine --timeout=300s

# Deploy application
kubectl apply -f k8s/app-deployment.yaml

# Wait for app to be ready
kubectl wait --for=condition=ready pod -l app=docuengine-app -n docuengine --timeout=300s

# Deploy auto-scaling and ingress
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml
```

### Step 6: Run Database Migrations

```bash
# Get the first app pod
POD_NAME=$(kubectl get pods -n docuengine -l app=docuengine-app -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -n docuengine $POD_NAME -- alembic upgrade head
```

---

## Verify Deployment

### Check All Pods

```bash
# View all pods
kubectl get pods -n docuengine

# Expected output:
# NAME                              READY   STATUS    RESTARTS   AGE
# docuengine-app-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
# docuengine-app-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
# docuengine-app-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
# postgres-0                        1/1     Running   0          5m
# qdrant-0                          1/1     Running   0          5m
# redis-xxxxxxxxxx-xxxxx            1/1     Running   0          5m
```

### Check Services

```bash
kubectl get svc -n docuengine

# Expected output:
# NAME                 TYPE           CLUSTER-IP       EXTERNAL-IP
# docuengine-service   LoadBalancer   10.100.x.x       xxxxx.elb.amazonaws.com
# postgres-service     ClusterIP      None             <none>
# qdrant-service       ClusterIP      None             <none>
# redis-service        ClusterIP      10.100.x.x       <none>
```

### Check Logs

```bash
# View app logs
kubectl logs -n docuengine -l app=docuengine-app --tail=50 -f

# View specific pod logs
kubectl logs -n docuengine $POD_NAME
```

---

## Access Your Application

### Get Load Balancer URL

```bash
# Get the ALB DNS name
kubectl get ingress -n docuengine docuengine-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Or get service URL
kubectl get svc -n docuengine docuengine-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

### Test the API

```bash
# Get the URL
LB_URL=$(kubectl get svc -n docuengine docuengine-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Test health endpoint
curl http://$LB_URL/health

# Expected response:
# {"status": "healthy"}

# Access API docs
echo "API Documentation: http://$LB_URL/docs"
```

### Set up DNS (Optional)

If you want a custom domain like `api.yourdomain.com`:

1. **Get Load Balancer DNS:**
```bash
kubectl get svc -n docuengine docuengine-service
```

2. **Create CNAME Record in Route53 or your DNS provider:**
   - Name: `api.yourdomain.com`
   - Type: `CNAME`
   - Value: `[your-load-balancer-dns]`

3. **Update Ingress with your domain:**
```bash
# Edit k8s/ingress.yaml
# Change: api.docuengine.example.com
# To: api.yourdomain.com

kubectl apply -f k8s/ingress.yaml
```

---

## Common Issues & Solutions

### Issue 1: Pods in "Pending" State

```bash
# Check what's wrong
kubectl describe pod <pod-name> -n docuengine

# Common causes:
# - Insufficient node capacity → Scale up nodes
# - PVC not bound → Check storage class

# Scale nodes
eksctl scale nodegroup --cluster=docuengine-cluster --nodes=3 --name=docuengine-nodes
```

### Issue 2: Image Pull Errors

```bash
# Verify ECR permissions
aws ecr get-login-password --region us-east-1

# Recreate service account with ECR access
eksctl create iamserviceaccount \
  --name docuengine-sa \
  --namespace docuengine \
  --cluster docuengine-cluster \
  --attach-policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly \
  --approve
```

### Issue 3: Database Connection Errors

```bash
# Check if PostgreSQL is running
kubectl get pods -n docuengine -l app=postgres

# Test database connection
kubectl exec -it -n docuengine postgres-0 -- psql -U docuser -d document_intelligence

# Check connection string in secrets
kubectl get secret docuengine-secrets -n docuengine -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

### Issue 4: Load Balancer Not Created

```bash
# Check AWS Load Balancer Controller
kubectl get deployment -n kube-system aws-load-balancer-controller

# Check controller logs
kubectl logs -n kube-system deployment/aws-load-balancer-controller

# Verify service annotations
kubectl describe svc docuengine-service -n docuengine
```

### Issue 5: Out of Resources

```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n docuengine

# Add more nodes
eksctl scale nodegroup \
  --cluster=docuengine-cluster \
  --nodes=5 \
  --name=docuengine-nodes
```

---

## Useful Commands Reference

```bash
# View all resources
kubectl get all -n docuengine

# Restart deployment
kubectl rollout restart deployment/docuengine-app -n docuengine

# Scale deployment
kubectl scale deployment docuengine-app --replicas=5 -n docuengine

# Port forward to local (for debugging)
kubectl port-forward -n docuengine svc/docuengine-service 8000:80

# Execute command in pod
kubectl exec -it -n docuengine <pod-name> -- bash

# View events
kubectl get events -n docuengine --sort-by='.lastTimestamp'

# Delete everything
kubectl delete namespace docuengine

# Delete cluster (WARNING: This deletes everything!)
eksctl delete cluster --name docuengine-cluster --region us-east-1
```

---

## Next Steps

1. ✅ **Set up monitoring:** Install Prometheus/Grafana (see DEPLOYMENT.md)
2. ✅ **Configure CI/CD:** Push to GitHub to trigger automated deployments
3. ✅ **Set up SSL/TLS:** Add ACM certificate to ingress
4. ✅ **Configure backups:** Set up automated database backups
5. ✅ **Add domain:** Configure Route53 for custom domain

---

## Cost Management

**Expected Monthly Costs:**
- EKS Cluster: $72 (0.10/hour)
- EC2 Nodes (2x t3.medium): ~$60
- Load Balancer: ~$20
- EBS Volumes: ~$10
- Data Transfer: ~$10
- **Total: ~$170/month**

**Save Money:**
- Use Spot instances for non-critical workloads
- Scale down during off-hours
- Use smaller instance types for dev/test
- Delete unused resources

---

## Clean Up (When Done Testing)

```bash
# Delete the application
kubectl delete namespace docuengine

# Delete the cluster
eksctl delete cluster --name docuengine-cluster --region us-east-1

# Delete ECR repository
aws ecr delete-repository --repository-name docuengine --force --region us-east-1

# Delete IAM policies (optional)
aws iam delete-policy --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/AWSLoadBalancerControllerIAMPolicy
```

---

**Congratulations!** 🎉 You now have a production-ready Kubernetes cluster running your Document Intelligence Platform on AWS!

**Questions?** Check:
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

**Built by:** Philip Owusu
**Last Updated:** 2026-06-14
