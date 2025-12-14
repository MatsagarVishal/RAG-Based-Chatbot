#!/bin/bash

# EC2 Setup Script for RAG Chatbot
# This script automates the setup of the RAG chatbot on an Amazon EC2 instance

set -e

echo "🚀 Starting EC2 Setup for RAG Chatbot..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed successfully"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed successfully"
else
    echo "✅ Docker Compose already installed"
fi

# Install Git
echo "📚 Installing Git..."
if ! command -v git &> /dev/null; then
    sudo apt-get install -y git
    echo "✅ Git installed successfully"
else
    echo "✅ Git already installed"
fi

# Install AWS CLI (for S3 access)
echo "☁️ Installing AWS CLI..."
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    sudo apt-get install -y unzip
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
    echo "✅ AWS CLI installed successfully"
else
    echo "✅ AWS CLI already installed"
fi

# Create application directory
echo "📁 Creating application directory..."
APP_DIR="/home/ubuntu/rag-chatbot"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone repository (if not already present)
if [ ! -d ".git" ]; then
    echo "📥 Cloning repository..."
    echo "Please enter your repository URL:"
    read REPO_URL
    git clone $REPO_URL .
fi

# Create .env file
echo "⚙️ Creating environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration:"
    echo "   - GROQ_API_KEY"
    echo "   - STORAGE_BACKEND (local or s3)"
    echo "   - S3_BUCKET_NAME (if using S3)"
    echo ""
    echo "Opening .env file for editing..."
    nano .env
fi

# Create storage directory (for local storage)
mkdir -p storage/data

# Configure AWS credentials (if using S3)
echo ""
echo "Do you want to configure AWS credentials? (y/n)"
read CONFIGURE_AWS
if [ "$CONFIGURE_AWS" = "y" ]; then
    aws configure
fi

# Build and start Docker containers
echo "🏗️ Building Docker image..."
docker-compose build

echo "🚀 Starting application..."
docker-compose up -d

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check health
echo "🏥 Checking application health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is healthy!"
else
    echo "⚠️ Application health check failed. Checking logs..."
    docker-compose logs --tail=50
fi

# Display status
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ EC2 Setup Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📍 Application URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Restart app:      docker-compose restart"
echo "   Stop app:         docker-compose down"
echo "   Update app:       git pull && docker-compose up -d --build"
echo ""
echo "📊 Check status:     docker-compose ps"
echo "🏥 Health check:     curl http://localhost:8000/health"
echo ""
echo "═══════════════════════════════════════════════════════════"
