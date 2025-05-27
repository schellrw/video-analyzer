#!/usr/bin/env python3
"""
Test Video Analysis Script
Quick test script for local video analysis functionality.
"""

import os
import sys
import time
import requests
import json
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_local_video_analysis():
    """Test the local video analysis endpoint."""
    
    # Configuration
    API_BASE = "http://localhost:5000/api/analysis"
    
    print("🎬 Video Analysis Test Script")
    print("=" * 50)
    
    # Step 1: List available videos
    print("\n1. Checking for available videos...")
    try:
        response = requests.get(f"{API_BASE}/list-local-videos")
        if response.status_code == 200:
            data = response.json()
            videos = data.get('videos', [])
            
            if not videos:
                print("❌ No videos found in uploads directory")
                print(f"   Please add video files to: {data.get('uploads_dir', './uploads')}")
                return False
            
            print(f"✅ Found {len(videos)} video(s):")
            for i, video in enumerate(videos):
                print(f"   {i+1}. {video['filename']} ({video['size_mb']} MB)")
            
            # Use the first video for testing
            test_video = videos[0]
            video_path = test_video['path']
            
        else:
            print(f"❌ Failed to list videos: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Make sure it's running on localhost:5000")
        print("   Run: python run.py")
        return False
    except Exception as e:
        print(f"❌ Error listing videos: {e}")
        return False
    
    # Step 2: Start analysis
    print(f"\n2. Starting analysis for: {test_video['filename']}")
    try:
        payload = {
            "video_path": video_path,
            "case_id": "test-case-001"
        }
        
        response = requests.post(
            f"{API_BASE}/test-local",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 202:
            data = response.json()
            task_id = data['task_id']
            print(f"✅ Analysis started successfully!")
            print(f"   Task ID: {task_id}")
        else:
            print(f"❌ Failed to start analysis: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting analysis: {e}")
        return False
    
    # Step 3: Monitor progress
    print(f"\n3. Monitoring analysis progress...")
    max_wait_time = 300  # 5 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{API_BASE}/task/{task_id}")
            
            if response.status_code == 200:
                data = response.json()
                state = data.get('state')
                status = data.get('status')
                
                print(f"   Status: {state} - {status}")
                
                if state == 'SUCCESS':
                    print("✅ Analysis completed successfully!")
                    
                    # Display results
                    result = data.get('result', {})
                    analysis_results = result.get('analysis_results', {})
                    
                    print(f"\n📊 Analysis Results:")
                    print(f"   Frames analyzed: {analysis_results.get('total_frames_analyzed', 0)}")
                    print(f"   Overall confidence: {analysis_results.get('overall_confidence', 0):.2f}")
                    print(f"   Concerns found: {analysis_results.get('concerns_found', False)}")
                    
                    violations = analysis_results.get('violations_detected', [])
                    if violations:
                        print(f"   Violations detected: {', '.join(violations)}")
                    
                    # Show key findings
                    summary = analysis_results.get('summary', {})
                    key_findings = summary.get('key_findings', [])
                    
                    if key_findings:
                        print(f"\n🔍 Key Findings ({len(key_findings)} concerning frames):")
                        for finding in key_findings[:3]:  # Show first 3
                            print(f"   Frame {finding.get('frame', 'N/A')} (confidence: {finding.get('confidence', 0):.2f})")
                            print(f"   → {finding.get('description', 'No description')[:100]}...")
                    
                    return True
                    
                elif state == 'FAILURE':
                    print(f"❌ Analysis failed: {data.get('error', 'Unknown error')}")
                    return False
                    
                elif state == 'PROGRESS':
                    # Continue monitoring
                    time.sleep(5)
                    continue
                else:
                    print(f"   Unknown state: {state}")
                    time.sleep(5)
                    continue
                    
            else:
                print(f"❌ Error checking task status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error monitoring progress: {e}")
            return False
    
    print("⏰ Analysis timed out after 5 minutes")
    return False


def check_environment():
    """Check if the environment is properly set up."""
    print("🔧 Environment Check")
    print("=" * 30)
    
    # Check if uploads directory exists
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        print("✅ Uploads directory exists")
    else:
        print("⚠️  Creating uploads directory...")
        uploads_dir.mkdir(exist_ok=True)
    
    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
    else:
        print("❌ .env file not found")
        print("   Please create backend/.env with your HUGGINGFACE_API_KEY")
        return False
    
    # Check for required environment variables
    required_vars = ['HUGGINGFACE_API_KEY']
    missing_vars = []
    
    from dotenv import load_dotenv
    load_dotenv()
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ Required environment variables found")
    
    return True


if __name__ == "__main__":
    print("🚀 Video Analyzer - Local Testing")
    print("=" * 50)
    
    # Check environment first
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Run the test
    success = test_local_video_analysis()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed. Check the logs above for details.")
        sys.exit(1) 