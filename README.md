# Dance Movement Analysis API

A cloud-based AI/ML server that analyzes dance movements from short videos. Uses MediaPipe for real-time pose detection and OpenCV for video processing. Features FastAPI endpoints, Docker containerization, and cloud deployment.

## 🧪 Testing
Comprehensive test suite ensures code reliability:
```bash
# From project root
python -m pytest -v Dance_Movement_Analysis/tests/test_analysis.py
```

### Test Coverage (9/9 Tests Passed ✅)
1. **Movement Analysis**
   - Basic angle calculations (90° test case)
   - Straight angle detection (180° test case)
   - Left/Right arm angle validation
   - Leg movement tracking
   - Posture stability metrics

2. **Error Handling**
   - Invalid keypoint detection
   - Empty landmark processing
   - Movement speed calculations

Last test run: 9 passed in 7.14s

## 🚀 Features
- Real-time body keypoint detection
- Skeleton overlay on output videos
- Movement analytics (arm/leg angles, posture stability)
- FastAPI REST endpoints
- Streamlit web interface
- Docker containerization
- AWS EC2 deployment

## 🛠️ Tech Stack
- Python, MediaPipe, OpenCV, NumPy
- FastAPI, Uvicorn
- Streamlit for web interface
- Docker, Render.com
- Pytest for unit testing

## 📁 Project Structure
```
app/
├── main.py                  # FastAPI application
├── streamlit_app.py         # Streamlit web interface
├── movement_analysis.py     # Core pose detection logic
├── tests/
│   └── test_analysis.py    # Unit tests
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── supervisord.conf        # Process manager config
```

## 🐳 Docker Deployment

### Build and Push to Docker Hub
```bash
# Build the Docker image
docker build -t dance-app .

# Tag for Docker Hub (replace with your username)
docker tag dance-app <your-dockerhub-username>/dance-app

# Push to Docker Hub
docker push <your-dockerhub-username>/dance-app
```

### Run Locally
```bash
docker run -d -p 80:8501 -p 8000:8000 dance-app
```

## ☁️ AWS EC2 Deployment

### 1. EC2 Instance Setup
Launch Instance:
- Instance type: t2.small minimum (2GB RAM required for video processing)
- AMI: Amazon Linux 2023 or Ubuntu 22.04
- Create and download SSH key pair (.pem file)

Configure Security Group:
| Port | Protocol | Source | Purpose |
|------|----------|---------|----------|
| 22 | TCP | Your IP | SSH access |
| 80 | TCP | 0.0.0.0/0 | Streamlit web UI |
| 8000 | TCP | 0.0.0.0/0 | FastAPI backend |

### 2. Connect to EC2
```bash
# Set permissions on your key file
chmod 400 your-key-file.pem

# SSH into your instance
ssh -i your-key-file.pem ec2-user@YOUR-EC2-PUBLIC-IP
```

### 3. Install Docker on EC2
```bash
# Update packages
sudo yum update -y

# Install Docker
sudo yum install docker -y

# Start Docker service
sudo service docker start

# Add user to docker group
sudo usermod -a -G docker ec2-user

# Log out and back in
exit
ssh -i your-key-file.pem ec2-user@YOUR-EC2-PUBLIC-IP
```

### 4. Deploy Application
```bash
# Pull your image
docker pull <your-dockerhub-username>/dance-app

# Run container
docker run -d \
  --restart=always \
  -p 80:8501 \
  -p 8000:8000 \
  --name dance-app \
  <your-dockerhub-username>/dance-app

# Verify running status
docker ps
```

Access your application:
- Streamlit UI: http://YOUR-EC2-PUBLIC-IP
- FastAPI docs: http://YOUR-EC2-PUBLIC-IP:8000/docs
⚠️ Important: Use http:// not https://

### 5. Update Deployment
On your local machine:
```bash
# Rebuild and push
docker build -t dance-app .
docker tag dance-app <your-dockerhub-username>/dance-app
docker push <your-dockerhub-username>/dance-app
```

On EC2:
```bash
# Update container
docker stop dance-app
docker rm dance-app
docker pull <your-dockerhub-username>/dance-app
docker run -d --restart=always -p 80:8501 -p 8000:8000 --name dance-app <your-dockerhub-username>/dance-app
```

## 🔧 Troubleshooting

### Connection Refused Error
- Use http:// not https://
- Verify Security Group has port 80 open
- Check container status: `docker ps`

### Out of Memory Errors
Symptom: Container crashes with SIGKILL
Solution: Upgrade to t2.small (2GB RAM)

### Video Upload Fails
- Use smaller videos (< 50MB, < 30 seconds)
- Check logs: `docker logs -f dance-app`
- Ensure sufficient memory

### Check Application Status
```bash
# View logs
docker logs -f dance-app

# Check resources
docker stats dance-app

# Restart if needed
docker restart dance-app
```

## 📊 API Endpoints
Base URL: http://YOUR-EC2-IP

| Endpoint | URL | Description |
|----------|-----|-------------|
| Streamlit UI | http://YOUR-IP | Web interface |
| API Docs | http://YOUR-IP:8000/docs | Interactive API docs |
| Health Check | http://YOUR-IP:8000/health | Service status |
| Analyze Video | POST http://YOUR-IP:8000/analyze | Upload video |



