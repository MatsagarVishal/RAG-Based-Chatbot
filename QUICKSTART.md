# 🚀 Quick Start - EC2 Deployment

## Prerequisites
- AWS Account
- AWS CLI configured
- Groq API Key

## 5-Minute Deployment

### 1. Create S3 Bucket
```bash
aws s3 mb s3://rag-chatbot-storage-$(date +%s)
```

### 2. Launch EC2 Instance
- Instance: t3.medium
- AMI: Ubuntu 22.04 LTS
- Storage: 20 GB
- Security Group: Allow ports 22, 8000

### 3. SSH and Deploy
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Run automated setup
curl -O https://raw.githubusercontent.com/your-repo/rag-chatbot/main/ec2-setup.sh
chmod +x ec2-setup.sh
./ec2-setup.sh
```

### 4. Configure Environment
```bash
cd rag-chatbot
nano .env
```

Add:
```env
GROQ_API_KEY=your_key_here
STORAGE_BACKEND=s3
S3_BUCKET_NAME=rag-chatbot-storage-<your-id>
AWS_REGION=us-east-1
```

### 5. Start Application
```bash
docker-compose up -d
```

### 6. Test
```bash
# Health check
curl http://localhost:8000/health

# Crawl a website
curl -X POST http://localhost:8000/api/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Ask a question
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"kb_id": "example_com", "question": "What is this about?"}'
```

## Access Your API
```
http://<EC2_PUBLIC_IP>:8000
```

## Useful Commands
```bash
# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Update
git pull && docker-compose up -d --build
```

## Cost
~$33-40/month for t3.medium instance

## Support
See full documentation:
- [EC2 Deployment Guide](./ec2_deployment_guide.md)
- [AWS Deployment Assessment](./aws_deployment_assessment.md)
