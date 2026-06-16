# Kubernetes Quick Reference Card

## 🚀 Quick Start Commands

### One-Line Cluster Creation
```bash
eksctl create cluster --name docuengine-cluster --region us-east-1 --nodes 2 --node-type t3.medium
```

### One-Line Application Deployment
```bash
kubectl apply -f k8s/
```

---

## 📦 Essential Commands

### Cluster Management
```bash
# View cluster info
kubectl cluster-info

# Get nodes
kubectl get nodes

# Describe node
kubectl describe node <node-name>

# Update kubeconfig
aws eks update-kubeconfig --name docuengine-cluster --region us-east-1
```

### Pod Management
```bash
# List all pods
kubectl get pods -n docuengine

# List all pods with more details
kubectl get pods -n docuengine -o wide

# Describe pod
kubectl describe pod <pod-name> -n docuengine

# View pod logs
kubectl logs <pod-name> -n docuengine

# Follow logs (live)
kubectl logs -f <pod-name> -n docuengine

# Execute command in pod
kubectl exec -it <pod-name> -n docuengine -- bash

# Port forward
kubectl port-forward <pod-name> 8000:8000 -n docuengine
```

### Deployment Management
```bash
# Get deployments
kubectl get deployments -n docuengine

# Describe deployment
kubectl describe deployment docuengine-app -n docuengine

# Scale deployment
kubectl scale deployment docuengine-app --replicas=5 -n docuengine

# Restart deployment (rolling restart)
kubectl rollout restart deployment/docuengine-app -n docuengine

# Check rollout status
kubectl rollout status deployment/docuengine-app -n docuengine

# Rollback deployment
kubectl rollout undo deployment/docuengine-app -n docuengine

# Update image
kubectl set image deployment/docuengine-app app=new-image:tag -n docuengine
```

### Service Management
```bash
# List services
kubectl get svc -n docuengine

# Describe service
kubectl describe svc docuengine-service -n docuengine

# Get service URL (LoadBalancer)
kubectl get svc docuengine-service -n docuengine -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

### ConfigMap & Secrets
```bash
# View configmap
kubectl get configmap docuengine-config -n docuengine -o yaml

# Edit configmap
kubectl edit configmap docuengine-config -n docuengine

# View secret keys (names only)
kubectl get secret docuengine-secrets -n docuengine -o jsonpath='{.data}'

# Decode secret value
kubectl get secret docuengine-secrets -n docuengine -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Create secret from literal
kubectl create secret generic my-secret --from-literal=key=value -n docuengine
```

### Troubleshooting
```bash
# Get events
kubectl get events -n docuengine --sort-by='.lastTimestamp'

# View all resources
kubectl get all -n docuengine

# Check pod resource usage
kubectl top pods -n docuengine

# Check node resource usage
kubectl top nodes

# Describe problematic pod
kubectl describe pod <pod-name> -n docuengine

# Get pod YAML
kubectl get pod <pod-name> -n docuengine -o yaml
```

---

## 🔧 Database Operations

### PostgreSQL
```bash
# Connect to PostgreSQL
kubectl exec -it postgres-0 -n docuengine -- psql -U docuser -d document_intelligence

# Run SQL from command line
kubectl exec -it postgres-0 -n docuengine -- psql -U docuser -d document_intelligence -c "SELECT version();"

# Backup database
kubectl exec postgres-0 -n docuengine -- pg_dump -U docuser document_intelligence > backup.sql

# Restore database
kubectl exec -i postgres-0 -n docuengine -- psql -U docuser document_intelligence < backup.sql

# Run migrations
POD=$(kubectl get pods -n docuengine -l app=docuengine-app -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n docuengine $POD -- alembic upgrade head
```

### Redis
```bash
# Connect to Redis
kubectl exec -it redis-<pod-name> -n docuengine -- redis-cli

# Flush all data (careful!)
kubectl exec -it redis-<pod-name> -n docuengine -- redis-cli FLUSHALL

# Get Redis info
kubectl exec -it redis-<pod-name> -n docuengine -- redis-cli INFO
```

### Qdrant
```bash
# Check Qdrant status
kubectl exec -it qdrant-0 -n docuengine -- curl http://localhost:6333/

# Access Qdrant dashboard
kubectl port-forward qdrant-0 6333:6333 -n docuengine
# Open: http://localhost:6333/dashboard
```

---

## 📊 Monitoring

```bash
# Watch pods (auto-refresh)
kubectl get pods -n docuengine -w

# Watch all resources
watch kubectl get all -n docuengine

# Resource usage
kubectl top pods -n docuengine
kubectl top nodes

# HPA status
kubectl get hpa -n docuengine

# Ingress status
kubectl get ingress -n docuengine
kubectl describe ingress docuengine-ingress -n docuengine
```

---

## 🛠️ Advanced Operations

### Copy Files
```bash
# Copy file TO pod
kubectl cp /local/path/file.txt docuengine/<pod-name>:/app/file.txt -n docuengine

# Copy file FROM pod
kubectl cp docuengine/<pod-name>:/app/file.txt /local/path/file.txt -n docuengine
```

### Labels & Selectors
```bash
# Get pods by label
kubectl get pods -l app=docuengine-app -n docuengine

# Add label
kubectl label pod <pod-name> env=production -n docuengine

# Remove label
kubectl label pod <pod-name> env- -n docuengine
```

### Namespace Operations
```bash
# Create namespace
kubectl create namespace docuengine

# Delete namespace (WARNING: deletes everything in it!)
kubectl delete namespace docuengine

# Set default namespace
kubectl config set-context --current --namespace=docuengine
```

### Context Management
```bash
# View current context
kubectl config current-context

# List all contexts
kubectl config get-contexts

# Switch context
kubectl config use-context <context-name>
```

---

## 🔥 Emergency Commands

### Force Delete Pod
```bash
kubectl delete pod <pod-name> --force --grace-period=0 -n docuengine
```

### Drain Node (for maintenance)
```bash
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
```

### Cordon Node (prevent scheduling)
```bash
kubectl cordon <node-name>
```

### Uncordon Node
```bash
kubectl uncordon <node-name>
```

### Delete All Pods in Namespace
```bash
kubectl delete pods --all -n docuengine
```

---

## 🎯 Debugging Workflows

### Pod Won't Start
```bash
# 1. Check pod status
kubectl get pod <pod-name> -n docuengine

# 2. Describe pod for events
kubectl describe pod <pod-name> -n docuengine

# 3. Check logs
kubectl logs <pod-name> -n docuengine

# 4. Check previous container logs (if crashed)
kubectl logs <pod-name> -n docuengine --previous
```

### Service Not Reachable
```bash
# 1. Check service
kubectl get svc -n docuengine

# 2. Check endpoints
kubectl get endpoints -n docuengine

# 3. Test from another pod
kubectl run test --image=busybox -it --rm -n docuengine -- wget -O- http://docuengine-service
```

### Database Connection Issues
```bash
# 1. Check if database pod is running
kubectl get pods -l app=postgres -n docuengine

# 2. Test connection from app pod
POD=$(kubectl get pods -n docuengine -l app=docuengine-app -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD -n docuengine -- env | grep DATABASE

# 3. Test database directly
kubectl exec -it postgres-0 -n docuengine -- psql -U docuser -d document_intelligence -c "SELECT 1;"
```

---

## 📝 YAML Shortcuts

### Quick Deploy from YAML
```bash
# Apply single file
kubectl apply -f deployment.yaml

# Apply all files in directory
kubectl apply -f k8s/

# Apply from URL
kubectl apply -f https://example.com/manifest.yaml

# Dry run (test without applying)
kubectl apply -f deployment.yaml --dry-run=client

# Show diff before applying
kubectl diff -f deployment.yaml
```

### Generate YAML
```bash
# Generate deployment YAML
kubectl create deployment my-app --image=nginx --dry-run=client -o yaml

# Generate service YAML
kubectl create service clusterip my-service --tcp=80:80 --dry-run=client -o yaml
```

---

## 🎨 Formatting Output

```bash
# JSON output
kubectl get pods -n docuengine -o json

# YAML output
kubectl get pods -n docuengine -o yaml

# Wide output (more columns)
kubectl get pods -n docuengine -o wide

# Custom columns
kubectl get pods -n docuengine -o custom-columns=NAME:.metadata.name,STATUS:.status.phase

# JSONPath
kubectl get pods -n docuengine -o jsonpath='{.items[*].metadata.name}'
```

---

## 🔐 Security

### Create Service Account
```bash
kubectl create serviceaccount my-sa -n docuengine
```

### Create Role
```bash
kubectl create role pod-reader --verb=get,list,watch --resource=pods -n docuengine
```

### Create RoleBinding
```bash
kubectl create rolebinding pod-reader-binding --role=pod-reader --serviceaccount=docuengine:my-sa -n docuengine
```

### View RBAC
```bash
# Can I?
kubectl auth can-i create pods -n docuengine

# Who can?
kubectl auth who-can create pods -n docuengine
```

---

## 💾 Persistent Volumes

```bash
# List PVCs
kubectl get pvc -n docuengine

# Describe PVC
kubectl describe pvc <pvc-name> -n docuengine

# List PVs
kubectl get pv

# Resize PVC (if storage class allows)
kubectl patch pvc <pvc-name> -n docuengine -p '{"spec":{"resources":{"requests":{"storage":"50Gi"}}}}'
```

---

## 📚 Help & Documentation

```bash
# Get help for command
kubectl help
kubectl create --help
kubectl apply --help

# Explain resource
kubectl explain pod
kubectl explain deployment.spec
kubectl explain service.spec.type

# API resources
kubectl api-resources

# API versions
kubectl api-versions
```

---

## 🎯 Pro Tips

1. **Use aliases:**
```bash
alias k=kubectl
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployments'
alias kdp='kubectl describe pod'
alias kl='kubectl logs'
```

2. **Use k9s (Terminal UI for Kubernetes):**
```bash
brew install k9s
k9s -n docuengine
```

3. **Use kubectx/kubens (context switcher):**
```bash
brew install kubectx
kubens docuengine  # Switch to namespace
```

4. **Watch command:**
```bash
watch kubectl get pods -n docuengine
```

5. **Auto-completion:**
```bash
# Bash
source <(kubectl completion bash)
echo "source <(kubectl completion bash)" >> ~/.bashrc

# Zsh
source <(kubectl completion zsh)
echo "source <(kubectl completion zsh)" >> ~/.zshrc
```

---

**🔖 Bookmark this page for quick access to Kubernetes commands!**
