# 🚀 AWS ECR Deployment Guide

## Prerequisites Completed ✅
- AWS CLI installed
- Docker image tagged: `910148268069.dkr.ecr.us-east-1.amazonaws.com/tripplanner:latest`

---

## Step-by-Step Deployment

### Step 1: Configure AWS Credentials

```bash
aws configure
```

**Enter when prompted:**
- AWS Access Key ID: [Your IAM access key]
- AWS Secret Access Key: [Your IAM secret key]
- Default region: `us-east-1`
- Default output format: `json`

### Step 2: Authenticate Docker with ECR

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 910148268069.dkr.ecr.us-east-1.amazonaws.com
```

**Expected output:** `Login Succeeded`

### Step 3: Push Image to ECR

```bash
docker push 910148268069.dkr.ecr.us-east-1.amazonaws.com/tripplanner:latest
```

**This will:**
- Upload all image layers (~1.6GB)
- Push to your ECR repository
- Make the image available for deployment

---

## Verify Upload

```bash
# List images in ECR repository
aws ecr describe-images --repository-name tripplanner --region us-east-1
```

---

## Deploy Options After Push

### Option 1: AWS App Runner (Simplest)

```bash
aws apprunner create-service \
  --service-name tripplanner-service \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "910148268069.dkr.ecr.us-east-1.amazonaws.com/tripplanner:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8501",
        "RuntimeEnvironmentVariables": {
          "GOOGLE_API_KEY": "your_key",
          "AMADEUS_API_KEY": "your_key",
          "AMADEUS_API_SECRET": "your_secret"
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }' \
  --region us-east-1
```

### Option 2: AWS ECS Fargate

1. **Create Task Definition:**
```bash
aws ecs register-task-definition \
  --family tripplanner-task \
  --requires-compatibilities FARGATE \
  --network-mode awsvpc \
  --cpu 1024 \
  --memory 2048 \
  --container-definitions '[
    {
      "name": "tripplanner",
      "image": "910148268069.dkr.ecr.us-east-1.amazonaws.com/tripplanner:latest",
      "portMappings": [{"containerPort": 8501}],
      "environment": [
        {"name": "GOOGLE_API_KEY", "value": "your_key"},
        {"name": "AMADEUS_API_KEY", "value": "your_key"},
        {"name": "AMADEUS_API_SECRET", "value": "your_secret"}
      ]
    }
  ]'
```

2. **Create Service:**
```bash
aws ecs create-service \
  --cluster your-cluster-name \
  --service-name tripplanner-service \
  --task-definition tripplanner-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration '{
    "awsvpcConfiguration": {
      "subnets": ["subnet-xxxxx"],
      "securityGroups": ["sg-xxxxx"],
      "assignPublicIp": "ENABLED"
    }
  }'
```

### Option 3: AWS Elastic Beanstalk

1. **Create `Dockerrun.aws.json`:**
```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "910148268069.dkr.ecr.us-east-1.amazonaws.com/tripplanner:latest",
    "Update": "true"
  },
  "Ports": [{"ContainerPort": 8501}],
  "Environment": [
    {"Name": "GOOGLE_API_KEY", "Value": "your_key"},
    {"Name": "AMADEUS_API_KEY", "Value": "your_key"},
    {"Name": "AMADEUS_API_SECRET", "Value": "your_secret"}
  ]
}
```

2. **Deploy:**
```bash
eb init -p docker tripplanner
eb create tripplanner-env
```

---

## Environment Variables (IMPORTANT! 🔐)

**Never hardcode API keys!** Use AWS Secrets Manager or Parameter Store:

### Using AWS Secrets Manager:

```bash
# Store secrets
aws secretsmanager create-secret \
  --name tripplanner/google-api-key \
  --secret-string "your_google_api_key"

aws secretsmanager create-secret \
  --name tripplanner/amadeus-api-key \
  --secret-string "your_amadeus_api_key"

aws secretsmanager create-secret \
  --name tripplanner/amadeus-api-secret \
  --secret-string "your_amadeus_api_secret"
```

Then reference in task definition:
```json
"secrets": [
  {
    "name": "GOOGLE_API_KEY",
    "valueFrom": "arn:aws:secretsmanager:us-east-1:910148268069:secret:tripplanner/google-api-key"
  }
]
```

---

## Monitoring & Logs

### View Logs (CloudWatch):
```bash
aws logs tail /aws/apprunner/tripplanner-service --follow
```

### Check Service Status:
```bash
aws apprunner describe-service --service-arn <service-arn>
```

---

## Costs Estimation

- **App Runner**: ~$25-50/month (based on usage)
- **ECS Fargate**: ~$30-60/month (0.25 vCPU, 0.5GB RAM)
- **ECR Storage**: ~$0.10/GB/month

---

## Cleanup (To Avoid Charges)

```bash
# Delete App Runner service
aws apprunner delete-service --service-arn <service-arn>

# Delete ECR images
aws ecr batch-delete-image \
  --repository-name tripplanner \
  --image-ids imageTag=latest

# Delete repository
aws ecr delete-repository \
  --repository-name tripplanner \
  --force
```

---

## Troubleshooting

### Issue: Login Failed
```bash
# Check AWS credentials
aws sts get-caller-identity

# Reconfigure if needed
aws configure
```

### Issue: Push Permission Denied
```bash
# Verify ECR repository exists
aws ecr describe-repositories --repository-names tripplanner

# Create if doesn't exist
aws ecr create-repository --repository-name tripplanner
```

### Issue: Service Won't Start
```bash
# Check logs
aws logs tail /aws/ecs/tripplanner --follow

# Common causes:
# - Port 8501 not exposed
# - Environment variables missing
# - Container health check failing
```

---

## Security Best Practices

1. ✅ Use IAM roles for ECS tasks (don't use API keys in container)
2. ✅ Store secrets in AWS Secrets Manager
3. ✅ Use VPC with private subnets for containers
4. ✅ Enable ECR image scanning
5. ✅ Use least-privilege IAM policies
6. ✅ Enable CloudTrail for audit logging

---

## Next Steps

1. Configure AWS CLI with `aws configure`
2. Authenticate Docker: `aws ecr get-login-password ...`
3. Push image: `docker push ...`
4. Choose deployment option (App Runner recommended for simplicity)
5. Set up monitoring and logging
6. Configure auto-scaling (optional)

**Your image is ready to deploy! 🚀**
