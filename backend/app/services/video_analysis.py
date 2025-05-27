"""
Video Analysis Service
Handles video processing and AI analysis using LLaVA model.
"""

import os
import cv2
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
from huggingface_hub import InferenceClient
from PIL import Image
import base64
import io

logger = logging.getLogger(__name__)


class VideoAnalysisService:
    """Service for analyzing videos using AI models."""
    
    def __init__(self):
        """Initialize the video analysis service."""
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.llava_model = os.getenv('LLAVA_MODEL', 'llava-hf/llava-1.5-7b-hf')
        
        if not self.hf_api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable is required")
        
        # Initialize Hugging Face client with auto provider selection
        self.client = InferenceClient(
            api_key=self.hf_api_key,
            provider="auto"  # Automatically select the best available provider
        )
        
        logger.info(f"VideoAnalysisService initialized with model: {self.llava_model}")
    
    def extract_frames(self, video_path: str, fps: float = 1.0, max_frames: int = 60) -> List[str]:
        """
        Extract frames from video at specified FPS.
        
        Args:
            video_path: Path to the video file
            fps: Frames per second to extract (default: 1 frame per second)
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of base64-encoded frame images
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / video_fps
            
            logger.info(f"Video: {duration:.2f}s, {video_fps:.2f} FPS, {total_frames} total frames")
            
            # Calculate frame interval
            frame_interval = int(video_fps / fps)
            frames_to_extract = min(max_frames, int(duration * fps))
            
            logger.info(f"Extracting {frames_to_extract} frames at {fps} FPS (every {frame_interval} frames)")
            
            frames = []
            frame_count = 0
            extracted_count = 0
            
            while cap.isOpened() and extracted_count < frames_to_extract:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Extract frame at specified interval
                if frame_count % frame_interval == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Convert to PIL Image
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Resize for efficiency (max 512px on longest side)
                    pil_image.thumbnail((512, 512), Image.Resampling.LANCZOS)
                    
                    # Convert to base64
                    buffer = io.BytesIO()
                    pil_image.save(buffer, format='JPEG', quality=85)
                    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
                    frames.append(img_base64)
                    extracted_count += 1
                    
                    logger.debug(f"Extracted frame {extracted_count}/{frames_to_extract}")
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Successfully extracted {len(frames)} frames from video")
            return frames
            
        except Exception as e:
            logger.error(f"Error extracting frames from {video_path}: {str(e)}")
            raise
    
    def analyze_frame(self, frame_base64: str, prompt: str = None) -> Dict[str, Any]:
        """
        Analyze a single frame using LLaVA model.
        
        Args:
            frame_base64: Base64-encoded image
            prompt: Custom prompt for analysis
            
        Returns:
            Analysis result dictionary
        """
        if not prompt:
            prompt = """Analyze this image for any potential civil rights violations, police misconduct, or concerning behavior. 
            Look for:
            1. Use of excessive force
            2. Improper police procedures
            3. Violations of constitutional rights
            4. Any concerning interactions between officers and civilians
            5. Environmental context and circumstances
            
            Provide a detailed description of what you observe."""
        
        try:
            # Prepare the message for LLaVA (Hugging Face format)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{frame_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Call Hugging Face Inference API
            response = self.client.chat.completions.create(
                model=self.llava_model,
                messages=messages,
                max_tokens=500
            )
            
            analysis_text = response.choices[0].message.content
            
            # Extract key information and assign confidence score
            result = {
                'description': analysis_text,
                'confidence': self._calculate_confidence(analysis_text),
                'potential_violations': self._extract_violations(analysis_text),
                'timestamp': None,  # Will be set by caller
                'concerns_detected': self._detect_concerns(analysis_text)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {str(e)}")
            return {
                'description': f"Analysis failed: {str(e)}",
                'confidence': 0.0,
                'potential_violations': [],
                'timestamp': None,
                'concerns_detected': False,
                'error': str(e)
            }
    
    def analyze_video(self, video_path: str, case_id: str = None) -> Dict[str, Any]:
        """
        Analyze entire video by processing key frames.
        
        Args:
            video_path: Path to the video file
            case_id: Optional case ID for context
            
        Returns:
            Complete video analysis results
        """
        try:
            logger.info(f"Starting video analysis for: {video_path}")
            
            # Extract frames
            frames = self.extract_frames(video_path, fps=1.0, max_frames=30)
            
            if not frames:
                raise ValueError("No frames could be extracted from video")
            
            # Analyze each frame
            frame_analyses = []
            total_frames = len(frames)
            
            for i, frame_base64 in enumerate(frames):
                logger.info(f"Analyzing frame {i+1}/{total_frames}")
                
                analysis = self.analyze_frame(frame_base64)
                analysis['frame_number'] = i
                analysis['timestamp'] = i  # Approximate timestamp (1 frame per second)
                
                frame_analyses.append(analysis)
            
            # Generate summary
            summary = self._generate_summary(frame_analyses)
            
            result = {
                'video_path': video_path,
                'case_id': case_id,
                'total_frames_analyzed': len(frame_analyses),
                'frame_analyses': frame_analyses,
                'summary': summary,
                'overall_confidence': summary.get('average_confidence', 0.0),
                'violations_detected': summary.get('violations_detected', []),
                'concerns_found': summary.get('concerns_found', False),
                'analysis_timestamp': None  # Will be set by caller
            }
            
            logger.info(f"Video analysis completed. Analyzed {len(frame_analyses)} frames")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing video {video_path}: {str(e)}")
            raise
    
    def _calculate_confidence(self, analysis_text: str) -> float:
        """Calculate confidence score based on analysis text."""
        # Simple heuristic - more detailed analysis = higher confidence
        confidence_indicators = [
            'clearly', 'obviously', 'definitely', 'certainly',
            'appears to', 'seems to', 'likely', 'probable'
        ]
        
        uncertainty_indicators = [
            'unclear', 'difficult to determine', 'cannot see',
            'possibly', 'maybe', 'might be', 'could be'
        ]
        
        text_lower = analysis_text.lower()
        confidence_score = 0.5  # Base confidence
        
        for indicator in confidence_indicators:
            if indicator in text_lower:
                confidence_score += 0.1
        
        for indicator in uncertainty_indicators:
            if indicator in text_lower:
                confidence_score -= 0.1
        
        return max(0.0, min(1.0, confidence_score))
    
    def _extract_violations(self, analysis_text: str) -> List[str]:
        """Extract potential violations from analysis text."""
        violations = []
        violation_keywords = {
            'excessive force': ['excessive force', 'unnecessary force', 'brutal', 'violent'],
            'improper procedure': ['improper', 'incorrect procedure', 'protocol violation'],
            'constitutional violation': ['constitutional', 'rights violation', 'civil rights'],
            'misconduct': ['misconduct', 'inappropriate behavior', 'unprofessional']
        }
        
        text_lower = analysis_text.lower()
        
        for violation_type, keywords in violation_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    violations.append(violation_type)
                    break
        
        return list(set(violations))  # Remove duplicates
    
    def _detect_concerns(self, analysis_text: str) -> bool:
        """Detect if there are any concerns in the analysis."""
        concern_keywords = [
            'concerning', 'problematic', 'violation', 'excessive',
            'inappropriate', 'misconduct', 'force', 'aggressive'
        ]
        
        text_lower = analysis_text.lower()
        return any(keyword in text_lower for keyword in concern_keywords)
    
    def _generate_summary(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary from all frame analyses."""
        if not frame_analyses:
            return {
                'average_confidence': 0.0,
                'violations_detected': [],
                'concerns_found': False,
                'key_findings': []
            }
        
        # Calculate average confidence
        confidences = [analysis.get('confidence', 0.0) for analysis in frame_analyses]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Collect all violations
        all_violations = []
        for analysis in frame_analyses:
            all_violations.extend(analysis.get('potential_violations', []))
        
        unique_violations = list(set(all_violations))
        
        # Check if any concerns were found
        concerns_found = any(analysis.get('concerns_detected', False) for analysis in frame_analyses)
        
        # Extract key findings (high-confidence analyses)
        key_findings = []
        for analysis in frame_analyses:
            if analysis.get('confidence', 0.0) > 0.7 and analysis.get('concerns_detected', False):
                key_findings.append({
                    'frame': analysis.get('frame_number'),
                    'timestamp': analysis.get('timestamp'),
                    'description': analysis.get('description', ''),
                    'confidence': analysis.get('confidence', 0.0)
                })
        
        return {
            'average_confidence': round(avg_confidence, 2),
            'violations_detected': unique_violations,
            'concerns_found': concerns_found,
            'key_findings': key_findings,
            'total_concerning_frames': len(key_findings)
        } 