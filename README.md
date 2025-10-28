Dance Movement Analysis API
A cloud-based AI/ML server that analyzes dance movements from short videos. Uses MediaPipe for real-time pose detection and OpenCV for video processing. Features FastAPI endpoints, Docker containerization, and cloud deployment.
🚀 Features

Real-time body keypoint detection
Skeleton overlay on output videos
Movement analytics (arm/leg angles, posture stability)
FastAPI REST endpoints
Streamlit web interface
Docker containerization
AWS EC2 deployment

🛠️ Tech Stack

Python, MediaPipe, OpenCV, NumPy
FastAPI, Uvicorn
Streamlit for web interface
Docker, Render.com
Pytest for unit testing

📁 Project Structure
app/
├── main.py                  # FastAPI application
├── streamlit_app.py        # Streamlit web interface
├── movement_analysis.py    # Core pose detection logic
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
└── supervisord.conf       # Process manager config


🐳 Docker Deployment
Build and Push
bashdocker build -t dance-app .
docker tag dance-app <your-dockerhub-username>/dance-app
docker push <your-dockerhub-username>/dance-app
Run Locally
bashdocker run -d -p 80:8501 -p 8000:8000 dance-app
☁️ AWS EC2 Deployment
Setup

Launch EC2 instance (t2.small minimum - 2GB RAM required)
Configure security group: Open ports 22 (SSH), 80 (HTTP), 8000 (API)
Connect via SSH:

bashssh -i your-key.pem ec2-user@YOUR-EC2-IP
Install Docker
bashsudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
Deploy
bashdocker pull <your-dockerhub-username>/dance-app
docker run -d --restart=always -p 80:8501 -p 8000:8000 dance-app
Access at: http://YOUR-EC2-IP
Update Deployment
Local:
bashdocker build -t dance-app .
docker push <your-dockerhub-username>/dance-app
EC2:
bashdocker stop dance-app && docker rm dance-app
docker pull <your-dockerhub-username>/dance-app
docker run -d --restart=always -p 80:8501 -p 8000:8000 dance-app
🔧 Troubleshooting
Connection issues: Use http:// not https://
Out of memory errors: Upgrade to t2.small or larger (t2.micro's 1GB RAM is insufficient)
Check logs: docker logs -f dance-app
📊 API Endpoints

Streamlit UI: http://YOUR-IP
API docs: http://YOUR-IP:8000/docs
Health check: http://YOUR-IP:8000/health


