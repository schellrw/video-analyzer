"""
Video Analysis Service
Handles video processing and AI analysis using LLaVA model with optimizations.
"""

import os
import cv2
import logging
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import tempfile
from huggingface_hub import InferenceClient
from PIL import Image
import base64
import io
import json
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class VideoAnalysisService:
    """Service for analyzing videos using AI models with cost optimization."""
    
    def __init__(self, use_cache: bool = True):
        """Initialize the video analysis service."""
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.nebius_api_key = os.getenv('NEBIUS_API_KEY')  # New: Direct Nebius API key
        
        # Cost-effective model selection (in order of preference)
        self.model_options = [
            'Qwen/Qwen2-VL-7B-Instruct',     # Most cost-effective: $0.04/$0.12 per 1M tokens
            'Llava-hf/llava-1.5-7b-hf',      # Alternative: $0.04/$0.12 per 1M tokens  
            'Llava-hf/llava-1.5-13b-hf',     # Fallback: $0.04/$0.12 per 1M tokens
            'Qwen/Qwen2-VL-72B-Instruct'     # Expensive fallback: $0.13/$0.40 per 1M tokens
        ]
        
        # Use environment variable for model selection, default to most cost-effective
        self.llava_model = os.getenv('LLAVA_MODEL', self.model_options[0])
        
        self.inference_provider = os.getenv('INFERENCE_PROVIDER', 'nebius')  # New: Provider selection
        self.use_cache = use_cache
        
        # Determine which API key to use
        if self.nebius_api_key and self.inference_provider == 'nebius':
            # Use direct Nebius API key (recommended for better performance)
            api_key = self.nebius_api_key
            provider = None  # Direct connection
            logger.info("Using direct Nebius API key")
        elif self.hf_api_key and self.inference_provider == 'nebius':
            # Use HF token with Nebius provider routing
            api_key = self.hf_api_key
            provider = 'nebius'
            logger.info("Using Hugging Face token with nebius provider routing")
        elif self.hf_api_key:
            # Fallback to standard HF
            api_key = self.hf_api_key
            provider = None
            logger.info("Using standard Hugging Face API")
        else:
            raise ValueError("No valid API key found. Please set either NEBIUS_API_KEY or HUGGINGFACE_API_KEY")
        
        try:
            # Initialize the InferenceClient
            self.client = InferenceClient(token=api_key)
            logger.info(f"InferenceClient initialized successfully with provider: {provider or 'standard'}")
        except Exception as e:
            logger.error(f"Failed to initialize InferenceClient: {e}")
            raise
        
        logger.info(f"VideoAnalysisService initialized with model: {self.llava_model} (provider: {self.inference_provider})")
    
    def extract_smart_frames(self, video_path: str, max_frames: int = 30, 
                           strategy: str = 'uniform') -> List[Dict[str, Any]]:
        """
        Extract frames intelligently to optimize analysis cost.
        
        Args:
            video_path: Path to the video file
            max_frames: Maximum number of frames to extract
            strategy: 'uniform', 'motion_based', or 'keyframe'
            
        Returns:
            List of frame dictionaries with metadata
        """
        cap = None
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / video_fps
            
            logger.info(f"Video: {duration:.2f}s, {video_fps:.2f} FPS, {total_frames} total frames")
            
            # Limit max_frames for very large videos to prevent memory issues
            if total_frames > 50000:  # ~28 minutes at 30fps
                original_max_frames = max_frames
                max_frames = min(max_frames, 30)  # Cap at 30 frames for large videos
                logger.warning(f"Large video detected ({total_frames} frames). Limiting analysis to {max_frames} frames (requested: {original_max_frames})")
            
            frames_data = []
            
            if strategy == 'uniform':
                frames_data = self._extract_uniform_frames(cap, max_frames, video_fps, duration)
            elif strategy == 'motion_based':
                frames_data = self._extract_motion_based_frames(cap, max_frames, video_fps)
            elif strategy == 'keyframe':
                frames_data = self._extract_keyframes(cap, max_frames, video_fps)
            else:
                raise ValueError(f"Unknown extraction strategy: {strategy}")
            
            logger.info(f"Successfully extracted {len(frames_data)} frames using {strategy} strategy")
            return frames_data
            
        except Exception as e:
            logger.error(f"Error extracting frames from {video_path}: {str(e)}")
            raise
        finally:
            if cap is not None:
                cap.release()
                # Force garbage collection for large videos
                import gc
                gc.collect()
    
    def _extract_uniform_frames(self, cap, max_frames: int, video_fps: float, 
                               duration: float) -> List[Dict[str, Any]]:
        """Extract frames uniformly across the video duration."""
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(1, total_frames // max_frames)
        
        frames_data = []
        frame_count = 0
        extracted_count = 0
        
        logger.info(f"Extracting {max_frames} frames uniformly from {total_frames} total frames (interval: {frame_interval})")
        
        while cap.isOpened() and extracted_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                # Resize frame immediately to save memory
                height, width = frame.shape[:2]
                if width > 640:  # Resize large frames
                    scale = 640 / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                timestamp = frame_count / video_fps
                frame_data = self._process_frame(frame, frame_count, timestamp)
                if frame_data:
                    frames_data.append(frame_data)
                    extracted_count += 1
                
                # Clear memory
                del frame
            
            frame_count += 1
        
        return frames_data
    
    def _extract_motion_based_frames(self, cap, max_frames: int, 
                                   video_fps: float) -> List[Dict[str, Any]]:
        """Extract frames based on motion detection to capture key moments."""
        frames_data = []
        prev_frame = None
        frame_count = 0
        motion_scores = []
        
        # Get total frames to calculate skip interval for large videos
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # For very large videos, skip frames to avoid memory issues
        skip_interval = max(1, total_frames // (max_frames * 10))  # Sample 10x more than needed
        
        logger.info(f"Processing large video: {total_frames} frames, sampling every {skip_interval} frames")
        
        # First pass: calculate motion scores (with frame skipping)
        while cap.isOpened() and len(motion_scores) < (max_frames * 10):
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames for large videos
            if frame_count % skip_interval != 0:
                frame_count += 1
                continue
            
            # Resize frame immediately to save memory
            height, width = frame.shape[:2]
            if width > 640:  # Resize large frames
                scale = 640 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # Calculate frame difference
                diff = cv2.absdiff(prev_frame, gray)
                motion_score = cv2.sumElems(diff)[0]
                motion_scores.append((frame_count, motion_score, frame.copy()))
            
            prev_frame = gray.copy()
            frame_count += skip_interval
            
            # Clear memory
            del frame, gray
        
        # Sort by motion score and select top frames
        motion_scores.sort(key=lambda x: x[1], reverse=True)
        selected_frames = motion_scores[:max_frames]
        selected_frames.sort(key=lambda x: x[0])  # Sort by frame number
        
        # Process selected frames
        for frame_num, motion_score, frame in selected_frames:
            timestamp = frame_num / video_fps
            frame_data = self._process_frame(frame, frame_num, timestamp)
            if frame_data:
                frame_data['motion_score'] = motion_score
                frames_data.append(frame_data)
        
        # Clear memory
        del motion_scores
        
        return frames_data
    
    def _extract_keyframes(self, cap, max_frames: int, video_fps: float) -> List[Dict[str, Any]]:
        """Extract keyframes using scene change detection."""
        frames_data = []
        prev_hist = None
        frame_count = 0
        scene_changes = []
        
        # Get total frames to calculate skip interval for large videos
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        skip_interval = max(1, total_frames // (max_frames * 10))  # Sample 10x more than needed
        
        logger.info(f"Extracting keyframes from {total_frames} frames, sampling every {skip_interval} frames")
        
        while cap.isOpened() and len(scene_changes) < (max_frames * 10):
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames for large videos
            if frame_count % skip_interval != 0:
                frame_count += 1
                continue
            
            # Resize frame immediately to save memory
            height, width = frame.shape[:2]
            if width > 640:  # Resize large frames
                scale = 640 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Calculate histogram for scene change detection
            hist = cv2.calcHist([frame], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            
            if prev_hist is not None:
                # Compare histograms
                correlation = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                scene_change_score = 1 - correlation
                scene_changes.append((frame_count, scene_change_score, frame.copy()))
            
            prev_hist = hist.copy()
            frame_count += skip_interval
            
            # Clear memory
            del frame, hist
        
        # Sort by scene change score and select top frames
        scene_changes.sort(key=lambda x: x[1], reverse=True)
        selected_frames = scene_changes[:max_frames]
        selected_frames.sort(key=lambda x: x[0])  # Sort by frame number
        
        # Process selected frames
        for frame_num, change_score, frame in selected_frames:
            timestamp = frame_num / video_fps
            frame_data = self._process_frame(frame, frame_num, timestamp)
            if frame_data:
                frame_data['scene_change_score'] = change_score
                frames_data.append(frame_data)
        
        # Clear memory
        del scene_changes
        
        return frames_data
    
    def _process_frame(self, frame, frame_number: int, timestamp: float) -> Optional[Dict[str, Any]]:
        """Process a single frame and convert to base64."""
        try:
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
            
            return {
                'frame_number': frame_number,
                'timestamp': timestamp,
                'timestamp_formatted': self._format_timestamp(timestamp),
                'base64_image': img_base64,
                'image_size': len(img_base64)
            }
        except Exception as e:
            logger.error(f"Error processing frame {frame_number}: {str(e)}")
            return None
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp as MM:SS.mmm"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"
    
    def analyze_frame_with_cache(self, frame_data: Dict[str, Any], 
                                prompt: str = None) -> Dict[str, Any]:
        """
        Analyze a single frame with caching to avoid duplicate API calls.
        """
        # Create cache key from frame content
        frame_hash = hashlib.md5(frame_data['base64_image'].encode()).hexdigest()
        cache_key = f"{frame_hash}_{hashlib.md5((prompt or '').encode()).hexdigest()}"
        
        # Check cache first
        if self.use_cache and cache_key in self.analysis_cache:
            logger.debug(f"Using cached analysis for frame {frame_data['frame_number']}")
            cached_result = self.analysis_cache[cache_key].copy()
            cached_result.update({
                'frame_number': frame_data['frame_number'],
                'timestamp': frame_data['timestamp'],
                'timestamp_formatted': frame_data['timestamp_formatted'],
                'cached': True
            })
            return cached_result
        
        # Perform analysis
        result = self.analyze_frame(frame_data['base64_image'], prompt)
        result.update({
            'frame_number': frame_data['frame_number'],
            'timestamp': frame_data['timestamp'],
            'timestamp_formatted': frame_data['timestamp_formatted'],
            'cached': False
        })
        
        # Cache the result (without frame-specific metadata)
        if self.use_cache:
            cache_result = {k: v for k, v in result.items() 
                          if k not in ['frame_number', 'timestamp', 'timestamp_formatted', 'cached']}
            self.analysis_cache[cache_key] = cache_result
        
        return result
    
    def analyze_frame(self, frame_base64: str, prompt: str = None) -> Dict[str, Any]:
        """
        Analyze a single frame using LLaVA model.
        """
        if not prompt:
            prompt = """Analyze this image for any potential civil rights violations, police misconduct, or concerning behavior. 
            Look for:
            1. Use of excessive force or violence
            2. Improper police procedures or protocol violations
            3. Violations of constitutional rights
            4. Concerning interactions between officers and civilians
            5. Environmental context and circumstances
            6. Weapons usage and appropriateness
            7. Officer positioning and tactics
            8. Civilian compliance and behavior
            
            Provide a detailed, objective description of what you observe. Be specific about actions, positions, and interactions."""
        
        try:
            start_time = time.time()
            
            # Prepare the message for LLaVA
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
            processing_time = time.time() - start_time
            
            # Enhanced analysis with better scoring
            result = {
                'description': analysis_text,
                'confidence': self._calculate_enhanced_confidence(analysis_text),
                'potential_violations': self._extract_violations(analysis_text),
                'severity_level': self._assess_severity(analysis_text),
                'concerns_detected': self._detect_concerns(analysis_text),
                'key_objects': self._extract_key_objects(analysis_text),
                'officer_actions': self._extract_officer_actions(analysis_text),
                'civilian_actions': self._extract_civilian_actions(analysis_text),
                'processing_time': processing_time,
                'api_cost_estimate': self._estimate_api_cost(len(analysis_text))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {str(e)}")
            return {
                'description': f"Analysis failed: {str(e)}",
                'confidence': 0.0,
                'potential_violations': [],
                'severity_level': 'unknown',
                'concerns_detected': False,
                'key_objects': [],
                'officer_actions': [],
                'civilian_actions': [],
                'processing_time': 0.0,
                'api_cost_estimate': 0.0,
                'error': str(e)
            }
    
    def analyze_video_optimized(self, video_path: str, case_id: str = None,
                               max_frames: int = 30, strategy: str = 'uniform') -> Dict[str, Any]:
        """
        Analyze entire video with cost optimization and smart sampling.
        """
        try:
            start_time = time.time()
            logger.info(f"Starting optimized video analysis for: {video_path}")
            
            # Extract frames using smart sampling
            frames_data = self.extract_smart_frames(video_path, max_frames, strategy)
            
            if not frames_data:
                raise ValueError("No frames could be extracted from video")
            
            # Analyze each frame with caching
            frame_analyses = []
            total_frames = len(frames_data)
            total_api_cost = 0.0
            
            for i, frame_data in enumerate(frames_data):
                logger.info(f"Analyzing frame {i+1}/{total_frames} at {frame_data['timestamp_formatted']}")
                
                analysis = self.analyze_frame_with_cache(frame_data)
                frame_analyses.append(analysis)
                total_api_cost += analysis.get('api_cost_estimate', 0.0)
            
            # Generate enhanced summary
            summary = self._generate_enhanced_summary(frame_analyses)
            processing_time = time.time() - start_time
            
            # Create violation timeline
            violation_timeline = self._create_violation_timeline(frame_analyses)
            
            result = {
                'video_path': video_path,
                'case_id': case_id,
                'extraction_strategy': strategy,
                'total_frames_analyzed': len(frame_analyses),
                'processing_time': processing_time,
                'total_api_cost_estimate': total_api_cost,
                'frame_analyses': frame_analyses,
                'summary': summary,
                'violation_timeline': violation_timeline,
                'overall_confidence': summary.get('average_confidence', 0.0),
                'violations_detected': summary.get('violations_detected', []),
                'concerns_found': summary.get('concerns_found', False),
                'severity_assessment': summary.get('severity_assessment', 'low'),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'recommendations': self._generate_recommendations(summary, frame_analyses)
            }
            
            logger.info(f"Video analysis completed in {processing_time:.2f}s. Cost: ${total_api_cost:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing video {video_path}: {str(e)}")
            raise
    
    def _calculate_enhanced_confidence(self, analysis_text: str) -> float:
        """Enhanced confidence calculation with multiple factors."""
        confidence_indicators = {
            'high': ['clearly', 'obviously', 'definitely', 'certainly', 'evident', 'visible'],
            'medium': ['appears to', 'seems to', 'likely', 'probable', 'suggests'],
            'low': ['unclear', 'difficult to determine', 'cannot see', 'possibly', 'maybe', 'might be', 'could be']
        }
        
        text_lower = analysis_text.lower()
        confidence_score = 0.5  # Base confidence
        
        # Length factor (longer descriptions often indicate more certainty)
        length_factor = min(0.2, len(analysis_text) / 1000)
        confidence_score += length_factor
        
        # Keyword analysis
        for level, keywords in confidence_indicators.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if level == 'high':
                        confidence_score += 0.15
                    elif level == 'medium':
                        confidence_score += 0.05
                    elif level == 'low':
                        confidence_score -= 0.1
        
        # Specificity factor (specific details indicate higher confidence)
        specific_terms = ['officer', 'weapon', 'handcuffs', 'badge', 'uniform', 'vehicle', 'ground', 'hands']
        specificity_score = sum(1 for term in specific_terms if term in text_lower) * 0.02
        confidence_score += specificity_score
        
        return max(0.0, min(1.0, confidence_score))
    
    def _extract_violations(self, analysis_text: str) -> List[str]:
        """Extract potential violations with enhanced detection."""
        violations = []
        violation_keywords = {
            'excessive_force': ['excessive force', 'unnecessary force', 'brutal', 'violent', 'beating', 'striking'],
            'improper_procedure': ['improper', 'incorrect procedure', 'protocol violation', 'unauthorized'],
            'constitutional_violation': ['constitutional', 'rights violation', 'civil rights', 'fourth amendment'],
            'misconduct': ['misconduct', 'inappropriate behavior', 'unprofessional', 'abuse'],
            'weapon_misuse': ['weapon', 'gun', 'taser', 'baton', 'pepper spray', 'firearm'],
            'restraint_issues': ['handcuffs', 'restraint', 'chokehold', 'neck', 'breathing']
        }
        
        text_lower = analysis_text.lower()
        
        for violation_type, keywords in violation_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    violations.append(violation_type.replace('_', ' '))
                    break
        
        return list(set(violations))
    
    def _assess_severity(self, analysis_text: str) -> str:
        """Assess the severity level of potential violations."""
        text_lower = analysis_text.lower()
        
        high_severity_terms = ['excessive force', 'weapon', 'violence', 'injury', 'blood', 'unconscious']
        medium_severity_terms = ['restraint', 'handcuffs', 'aggressive', 'shouting', 'pushing']
        
        if any(term in text_lower for term in high_severity_terms):
            return 'high'
        elif any(term in text_lower for term in medium_severity_terms):
            return 'medium'
        else:
            return 'low'
    
    def _detect_concerns(self, analysis_text: str) -> bool:
        """Enhanced concern detection."""
        concern_keywords = [
            'concerning', 'problematic', 'violation', 'excessive',
            'inappropriate', 'misconduct', 'force', 'aggressive',
            'weapon', 'violence', 'injury', 'restraint'
        ]
        
        text_lower = analysis_text.lower()
        return any(keyword in text_lower for keyword in concern_keywords)
    
    def _extract_key_objects(self, analysis_text: str) -> List[str]:
        """Extract key objects mentioned in the analysis."""
        objects = []
        object_keywords = ['weapon', 'gun', 'taser', 'baton', 'handcuffs', 'vehicle', 'badge', 'uniform']
        
        text_lower = analysis_text.lower()
        for obj in object_keywords:
            if obj in text_lower:
                objects.append(obj)
        
        return objects
    
    def _extract_officer_actions(self, analysis_text: str) -> List[str]:
        """Extract officer actions from the analysis."""
        actions = []
        action_keywords = ['restraining', 'arresting', 'handcuffing', 'searching', 'pursuing', 'drawing weapon']
        
        text_lower = analysis_text.lower()
        for action in action_keywords:
            if action in text_lower:
                actions.append(action)
        
        return actions
    
    def _extract_civilian_actions(self, analysis_text: str) -> List[str]:
        """Extract civilian actions from the analysis."""
        actions = []
        action_keywords = ['complying', 'resisting', 'running', 'hands up', 'on ground', 'cooperative']
        
        text_lower = analysis_text.lower()
        for action in action_keywords:
            if action in text_lower:
                actions.append(action)
        
        return actions
    
    def _estimate_api_cost(self, response_length: int) -> float:
        """Estimate API cost based on response length (rough estimate)."""
        # Rough estimate: $0.0001 per 1000 characters
        return (response_length / 1000) * 0.0001
    
    def _generate_enhanced_summary(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate enhanced summary with detailed statistics."""
        if not frame_analyses:
            return {
                'average_confidence': 0.0,
                'violations_detected': [],
                'concerns_found': False,
                'key_findings': [],
                'severity_assessment': 'low'
            }
        
        # Calculate statistics
        confidences = [analysis.get('confidence', 0.0) for analysis in frame_analyses]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Collect all violations
        all_violations = []
        for analysis in frame_analyses:
            all_violations.extend(analysis.get('potential_violations', []))
        unique_violations = list(set(all_violations))
        
        # Severity assessment
        severity_levels = [analysis.get('severity_level', 'low') for analysis in frame_analyses]
        max_severity = 'low'
        if 'high' in severity_levels:
            max_severity = 'high'
        elif 'medium' in severity_levels:
            max_severity = 'medium'
        
        # Check concerns
        concerns_found = any(analysis.get('concerns_detected', False) for analysis in frame_analyses)
        
        # Extract key findings (high-confidence concerning frames)
        key_findings = []
        for analysis in frame_analyses:
            if (analysis.get('confidence', 0.0) > 0.7 and 
                analysis.get('concerns_detected', False)):
                key_findings.append({
                    'frame': analysis.get('frame_number'),
                    'timestamp': analysis.get('timestamp'),
                    'timestamp_formatted': analysis.get('timestamp_formatted'),
                    'description': analysis.get('description', ''),
                    'confidence': analysis.get('confidence', 0.0),
                    'severity': analysis.get('severity_level', 'low'),
                    'violations': analysis.get('potential_violations', [])
                })
        
        # Sort key findings by severity and confidence
        key_findings.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}[x['severity']],
            x['confidence']
        ), reverse=True)
        
        return {
            'average_confidence': round(avg_confidence, 2),
            'violations_detected': unique_violations,
            'concerns_found': concerns_found,
            'key_findings': key_findings,
            'total_concerning_frames': len(key_findings),
            'severity_assessment': max_severity,
            'confidence_distribution': {
                'high': len([c for c in confidences if c > 0.7]),
                'medium': len([c for c in confidences if 0.4 <= c <= 0.7]),
                'low': len([c for c in confidences if c < 0.4])
            }
        }
    
    def _create_violation_timeline(self, frame_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a timeline of violations for quick navigation."""
        timeline = []
        
        for analysis in frame_analyses:
            if analysis.get('concerns_detected', False):
                timeline.append({
                    'timestamp': analysis.get('timestamp'),
                    'timestamp_formatted': analysis.get('timestamp_formatted'),
                    'frame_number': analysis.get('frame_number'),
                    'severity': analysis.get('severity_level', 'low'),
                    'confidence': analysis.get('confidence', 0.0),
                    'violations': analysis.get('potential_violations', []),
                    'description': analysis.get('description', '')[:200] + '...' if len(analysis.get('description', '')) > 200 else analysis.get('description', ''),
                    'priority': self._calculate_priority(analysis)
                })
        
        # Sort by priority (severity + confidence)
        timeline.sort(key=lambda x: x['priority'], reverse=True)
        return timeline
    
    def _calculate_priority(self, analysis: Dict[str, Any]) -> float:
        """Calculate priority score for timeline sorting."""
        severity_weights = {'high': 3.0, 'medium': 2.0, 'low': 1.0}
        severity_score = severity_weights.get(analysis.get('severity_level', 'low'), 1.0)
        confidence_score = analysis.get('confidence', 0.0)
        return severity_score * confidence_score
    
    def _generate_recommendations(self, summary: Dict[str, Any], 
                                frame_analyses: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for manual review."""
        recommendations = []
        
        if summary.get('severity_assessment') == 'high':
            recommendations.append("Immediate manual review recommended due to high-severity findings")
        
        if summary.get('average_confidence') < 0.5:
            recommendations.append("Low confidence scores suggest manual verification needed")
        
        if len(summary.get('key_findings', [])) > 5:
            recommendations.append("Multiple concerning incidents detected - comprehensive review advised")
        
        violation_types = summary.get('violations_detected', [])
        if 'excessive force' in violation_types:
            recommendations.append("Potential excessive force detected - priority review required")
        
        if 'weapon misuse' in violation_types:
            recommendations.append("Weapon usage detected - verify compliance with department policy")
        
        # Timeline-based recommendations
        concerning_frames = [a for a in frame_analyses if a.get('concerns_detected', False)]
        if len(concerning_frames) > len(frame_analyses) * 0.3:
            recommendations.append("High percentage of concerning frames - full video review recommended")
        
        return recommendations

# Legacy compatibility methods
    def extract_frames(self, video_path: str, fps: float = 1.0, max_frames: int = 60) -> List[str]:
        """Legacy method for backward compatibility."""
        frames_data = self.extract_smart_frames(video_path, max_frames, 'uniform')
        return [frame['base64_image'] for frame in frames_data]
    
    def analyze_video(self, video_path: str, case_id: str = None) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return self.analyze_video_optimized(video_path, case_id, max_frames=30, strategy='uniform') 