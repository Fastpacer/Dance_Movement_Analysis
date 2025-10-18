import streamlit as st
import cv2
import tempfile
import os
import time
import sys
from movement_analysis import DanceMovementAnalyzer

# Set page configuration
st.set_page_config(
    page_title="Dance Movement Analyzer",
    page_icon="💃",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">💃 Dance Movement Analyzer</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Upload Video")
    uploaded_file = st.file_uploader(
        "Choose a dance video", 
        type=['mp4', 'mov', 'avi', 'mkv'],
        help="Upload a short dance video for movement analysis"
    )
    
    st.header("Analysis Settings")
    show_metrics = st.checkbox("Display Real-time Metrics", value=True)
    
    # Refresh button
    if st.button("🔄 Refresh Video Display"):
        st.rerun()
    
    st.header("Tips")
    st.info("""
    For best results:
    - Use videos with clear full-body visibility
    - Good lighting conditions
    - 5-30 second clips work best
    - MP4 format recommended
    """)
    
    st.markdown("---")
    st.markdown("**Note:** If video doesn't display, use the download button and play in your system video player.")

# Main content
if uploaded_file is not None:
    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(uploaded_file.read())
        input_path = tmp_file.name
    
    # Create output path
    output_filename = f"analyzed_{uploaded_file.name}"
    output_path = os.path.join("uploads", output_filename)
    os.makedirs("uploads", exist_ok=True)
    
    # Initialize analyzer
    analyzer = DanceMovementAnalyzer()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Video Processing")
        
        try:
            with st.spinner("🔄 Analyzing dance movements... This may take a few moments."):
                start_time = time.time()
                output_path, analysis_summary = analyzer.process_video(input_path, output_path)
                processing_time = time.time() - start_time
            
            # Check if output was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                st.markdown('<div class="success-box">✅ Analysis completed successfully!</div>', unsafe_allow_html=True)
                st.success(f"Processing time: {processing_time:.2f} seconds")
                
                # Display file info
                file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                st.info(f"Output file created: {output_filename} ({file_size:.2f} MB)")
                
                # Display processed video - FIXED: Read as bytes for better compatibility
                st.subheader("🎬 Processed Video with Pose Detection")
                
                try:
                    with open(output_path, "rb") as video_file:
                        video_bytes = video_file.read()
                    st.video(video_bytes)
                except Exception as e:
                    st.markdown('<div class="info-box">📹 Video processed successfully! Use download button below to view.</div>', unsafe_allow_html=True)
                
                # Download button
                st.download_button(
                    label="📥 Download Processed Video",
                    data=video_bytes if 'video_bytes' in locals() else open(output_path, "rb").read(),
                    file_name=output_filename,
                    mime="video/mp4",
                    key="download_processed"
                )
                
            else:
                st.markdown('<div class="error-box">❌ Video processing completed but output file was not created properly.</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.markdown('<div class="error-box">❌ Error processing video</div>', unsafe_allow_html=True)
            st.error(f"Error details: {str(e)}")
            st.info("💡 Try a different video format or check the video file integrity.")
    
    with col2:
        st.subheader("Analysis Results")
        
        if 'error' not in analysis_summary and analysis_summary.get('frames_with_detection', 0) > 0:
            # Display metrics
            st.markdown("### 📊 Movement Metrics")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Left Arm Angle", f"{analysis_summary['average_left_arm_angle']:.1f}°")
                st.metric("Left Leg Angle", f"{analysis_summary['average_left_leg_angle']:.1f}°")
            
            with col2:
                st.metric("Right Arm Angle", f"{analysis_summary['average_right_arm_angle']:.1f}°")
                st.metric("Right Leg Angle", f"{analysis_summary['average_right_leg_angle']:.1f}°")
            
            # Additional metrics
            stability_score = analysis_summary['average_stability']
            st.metric(
                "Posture Stability", 
                f"{stability_score:.2f}",
                delta="Good" if stability_score > 0.7 else "Needs Improvement",
                delta_color="normal"
            )
            
            st.metric("Total Frames", analysis_summary['total_frames'])
            st.metric("Pose Detected Frames", analysis_summary['frames_with_detection'])
            
            # Detection rate
            detection_rate = (analysis_summary['frames_with_detection'] / analysis_summary['total_frames']) * 100
            
            # Insights
            st.markdown("### 💡 Insights")
            if detection_rate > 80:
                st.success("Excellent pose detection throughout the video!")
            elif detection_rate > 50:
                st.info("Good pose detection. Some frames may have missed detection.")
            else:
                st.warning("Low pose detection rate. Try a video with better visibility.")
                
            # Movement quality assessment
            st.markdown("### 🎯 Movement Quality")
            avg_arm_movement = (analysis_summary['average_left_arm_angle'] + analysis_summary['average_right_arm_angle']) / 2
            avg_leg_movement = (analysis_summary['average_left_leg_angle'] + analysis_summary['average_right_leg_angle']) / 2
            
            if avg_arm_movement > 90 or avg_leg_movement > 90:
                st.info("Dynamic movement detected with wide range of motion")
            else:
                st.info("Controlled movement with moderate range")
                
        else:
            st.error("No human poses detected in the video. Please try another video with clear full-body visibility.")
            st.info("""
            **Tips for better detection:**
            - Ensure full body is visible
            - Good lighting conditions
            - Avoid crowded backgrounds
            - Steady camera movement
            """)
    
    # Cleanup
    analyzer.release()
    os.unlink(input_path)

else:
    # Welcome message
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Welcome to the Dance Movement Analyzer! 🎭
        
        **Upload a dance video to get started:**
        
        1. Click **Browse files** in the sidebar
        2. Select a dance video (MP4 recommended)
        3. Wait for processing to complete
        4. View your analyzed video with pose overlay
        5. Download the results
        
        **What we analyze:**
        - Body pose and keypoints using MediaPipe
        - Arm and leg angles in real-time
        - Posture stability and alignment
        - Movement patterns and quality
        
        **Features:**
        - Real-time skeleton overlay
        - Movement metrics display
        - Pose tracking visualization
        - Downloadable results
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 How It Works
        
        **Technology Stack:**
        - Python + MediaPipe for pose detection
        - OpenCV for video processing
        - Streamlit for web interface
        
        **Output Includes:**
        - Video with skeleton overlay
        - Real-time angle measurements
        - Posture stability score
        - Movement analysis insights
        
        **Perfect For:**
        - Dance practice analysis
        - Movement quality assessment
        - Performance tracking
        - Training feedback
        """)
        
        st.markdown("---")
        st.markdown("""
        **Note:** If the processed video doesn't display automatically, 
        use the **download button** to get the full-quality output file 
        and play it in your system's video player.
        """)

# Footer
st.markdown("---")
st.markdown(
    "**Dance Movement Analysis Project** | "
    "Built with ❤️ using Streamlit, MediaPipe, and OpenCV | "
    "Callus Company Inc. Competency Assessment"
)