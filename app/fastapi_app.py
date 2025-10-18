from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
from movement_analysis import DanceMovementAnalyzer
import json

app = FastAPI(
    title="Dance Movement Analysis API",
    description="AI/ML server for analyzing dance movements from videos",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "Dance Movement Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST /analyze - Upload video for analysis",
            "health": "GET /health - API health check"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Dance Movement Analysis API"}

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    """
    Analyze dance movement from uploaded video file.
    
    Returns:
    - Processed video with skeleton overlay
    - Movement analysis data
    """
    
    # Validate file type
    if not file.content_type.startswith("video/"):
        raise HTTPException(400, "File must be a video")
    
    # Generate unique file names
    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_input.mp4")
    output_path = os.path.join(UPLOAD_DIR, f"{file_id}_output.mp4")
    
    try:
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process video
        analyzer = DanceMovementAnalyzer()
        try:
            output_path, analysis_summary = analyzer.process_video(input_path, output_path)
            
            # Return analysis results
            return {
                "status": "success",
                "analysis_id": file_id,
                "analysis": analysis_summary,
                "download_url": f"/download/{file_id}_output.mp4"
            }
            
        except Exception as e:
            raise HTTPException(500, f"Video processing failed: {str(e)}")
        finally:
            analyzer.release()
            
    except Exception as e:
        raise HTTPException(500, f"Server error: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download processed video file.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")
    
    return FileResponse(
        file_path,
        media_type='video/mp4',
        filename=f"analyzed_{filename}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)