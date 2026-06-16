#!/bin/bash

set -e  # Exit on error

echo "🚀 Document Intelligence Platform - GCP Deployment Script"
echo "=========================================================="
echo ""

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
echo "📋 Project ID: $PROJECT_ID"
echo ""

# Step 1: Build and push Docker image
echo "🔨 Step 1: Building and pushing Docker image..."
echo "This will take 2-5 minutes..."
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/docuengine/app:latest
echo "✅ Image built and pushed successfully!"
echo ""

# Step 2: Update deployment file with project ID
echo "📝 Step 2: Updating deployment configuration..."
sed "s/PROJECT_ID/$PROJECT_ID/g" k8s/app-deployment-gcp.yaml > k8s/app-deployment-gcp-final.yaml
echo "✅ Configuration updated!"
echo ""

# Step 3: Create namespace
echo "📦 Step 3: Creating Kubernetes namespace..."
kubectl apply -f k8s/namespace.yaml
echo "✅ Namespace created!"
echo ""

# Step 4: Check if secrets file is configured
echo "🔐 Step 4: Checking secrets configuration..."
if grep -q "your-secure-password-here" k8s/secrets-gcp.yaml || grep -q "sk-your-openai-key-here" k8s/secrets-gcp.yaml; then
    echo "⚠️  WARNING: Please update k8s/secrets-gcp.yaml with your actual credentials!"
    echo ""
    echo "You need to edit the following:"
    echo "  1. DB_PASSWORD (create a secure password)"
    echo "  2. SECRET_KEY (generate a random string)"
    echo "  3. LLM_PROVIDER (choose: openai, gemini, or anthropic)"
    echo "  4. API key for your chosen LLM provider"
    echo ""
    echo "After updating, run: kubectl apply -f k8s/secrets-gcp.yaml"
    echo ""
    read -p "Press Enter after you've updated the secrets file..."
fi

kubectl apply -f k8s/secrets-gcp.yaml
echo "✅ Secrets created!"
echo ""

# Step 5: Apply configmap
echo "⚙️  Step 5: Applying configuration..."
kubectl apply -f k8s/configmap.yaml
echo "✅ ConfigMap applied!"
echo ""

# Step 6: Deploy databases
echo "💾 Step 6: Deploying databases (PostgreSQL, Redis, Qdrant)..."
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/qdrant-statefulset.yaml
echo "⏳ Waiting for databases to be ready (this may take 2-3 minutes)..."
kubectl wait --for=condition=ready pod -l app=postgres -n docuengine --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n docuengine --timeout=300s
kubectl wait --for=condition=ready pod -l app=qdrant -n docuengine --timeout=300s
echo "✅ All databases are ready!"
echo ""

# Step 7: Deploy application
echo "🚀 Step 7: Deploying application..."
kubectl apply -f k8s/app-deployment-gcp-final.yaml
echo "⏳ Waiting for application to be ready..."
kubectl wait --for=condition=ready pod -l app=docuengine-app -n docuengine --timeout=300s
echo "✅ Application deployed successfully!"
echo ""

# Step 8: Run database migrations
echo "🔄 Step 8: Running database migrations..."
POD_NAME=$(kubectl get pods -n docuengine -l app=docuengine-app -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n docuengine $POD_NAME -- alembic upgrade head
echo "✅ Migrations completed!"
echo ""

# Step 9: Get LoadBalancer IP
echo "🌐 Step 9: Getting LoadBalancer IP..."
echo "⏳ Waiting for LoadBalancer to provision (this may take 2-3 minutes)..."
sleep 30
EXTERNAL_IP=""
while [ -z $EXTERNAL_IP ]; do
    echo "Waiting for external IP..."
    EXTERNAL_IP=$(kubectl get svc docuengine-service -n docuengine -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    [ -z "$EXTERNAL_IP" ] && sleep 10
done
echo ""
echo "🎉 Deployment Complete!"
echo "=========================================================="
echo ""
echo "🌐 Your application is accessible at:"
echo "   http://$EXTERNAL_IP"
echo ""
echo "📚 API Documentation:"
echo "   http://$EXTERNAL_IP/docs"
echo ""
echo "🔍 Health Check:"
echo "   http://$EXTERNAL_IP/health"
echo ""
echo "📊 View pods:"
echo "   kubectl get pods -n docuengine"
echo ""
echo "📝 View logs:"
echo "   kubectl logs -f -l app=docuengine-app -n docuengine"
echo ""
echo "=========================================================="
