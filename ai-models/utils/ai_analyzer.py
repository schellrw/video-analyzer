# ai_analyzer.py - AI analysis using HuggingFace models
import torch
from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
import whisper
import numpy as np
from typing import List, Dict, Any
import logging
from PIL import Image
import io
import base64
import cv2

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Initialize models
        self._load_vision_model()
        self._load_whisper_model()
        
        # Analysis prompts for different aspects
        self.analysis_prompts = {
            'general': "Describe in detail what is happening in this image. Focus on actions, people, objects, and any interactions between them.",
            'police_activity': "Analyze this image for police activity. Describe: 1) Officer actions and positioning 2) Subject/arrestee behavior 3) Use of force or restraints 4) Weapons or equipment visible 5) Environmental context",
            'violation_detection': "Look for potential violations in this image: excessive force, improper restraint techniques, weapon misuse, unprofessional conduct, or civil rights violations. Be specific about what you observe.",
            'body_language': "Analyze body language and positioning in this image. Describe stress indicators, compliance/resistance, officer aggression, and power dynamics between people."
        }
    
    def _load_vision_model(self):
        """Load LLaVA vision-language model"""
        try:
            model_name = "llava-hf/llava-v1.6-mistral-7b-hf"
            
            self.vision_processor = LlavaNextProcessor.from_pretrained(model_name)
            self.vision_model = LlavaNextForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            logger.info("Vision model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading vision model: {e}")
            raise
    
    def _load_whisper_model(self):
        """Load Whisper speech-to-text model"""
        try:
            # Use medium model for balance of speed and accuracy
            self.whisper_model = whisper.load_model("medium")
            logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio file using Whisper"""
        try:
            # Transcribe with word-level timestamps
            result = self.whisper_model.transcribe(
                audio_path,
                word_timestamps=True,
                language="en"  # Assume English for now
            )
            
            # Extract segments with timestamps
            segments = []
            for segment in result.get('segments', []):
                segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip(),
                    'confidence': segment.get('avg_logprob', 0),
                    'words': segment.get('words', [])
                })
            
            transcript_data = {
                'text': result['text'],
                'language': result.get('language', 'en'),
                'segments': segments,
                'duration': max([seg['end'] for seg in segments]) if segments else 0
            }
            
            logger.info(f"Transcribed audio: {len(segments)} segments, {len(result['text'])} characters")
            return transcript_data
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def analyze_frames(self, frames: List[Dict]) -> List[Dict]:
        """Analyze video frames using vision model"""
        try:
            analysis_results = []
            
            for frame_data in frames:
                frame_array = frame_data['frame_data']
                timestamp = frame_data['timestamp']
                
                # Convert numpy array to PIL Image
                pil_image = Image.fromarray(frame_array)
                
                # Analyze frame for different aspects
                frame_analysis = {
                    'timestamp': timestamp,
                    'frame_index': frame_data['frame_index'],
                    'general_description': self._analyze_single_frame(pil_image, 'general'),
                    'police_activity': self._analyze_single_frame(pil_image, 'police_activity'),
                    'violation_check': self._analyze_single_frame(pil_image, 'violation_detection'),
                    'body_language': self._analyze_single_frame(pil_image, 'body_language'),
                    'objects_detected': self._detect_objects(pil_image),
                    'scene_confidence': self._calculate_scene_confidence(pil_image)
                }
                
                analysis_results.append(frame_analysis)
                
                # Log progress
                if len(analysis_results) % 10 == 0:
                    logger.info(f"Analyzed {len(analysis_results)} frames")
            
            logger.info(f"Completed analysis of {len(frames)} frames")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing frames: {e}")
            raise
    
    def _analyze_single_frame(self, image: Image.Image, analysis_type: str) -> str:
        """Analyze single frame with specific prompt"""
        try:
            prompt = self.analysis_prompts.get(analysis_type, self.analysis_prompts['general'])
            
            # Prepare inputs
            inputs = self.vision_processor(prompt, image, return_tensors="pt")
            
            # Move to device
            if torch.cuda.is_available():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.vision_model.generate(
                    **inputs,
                    max_new_tokens=256,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.vision_processor.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.vision_processor.decode(outputs[0], skip_special_tokens=True)
            
            # Extract generated text (remove the prompt)
            generated_text = response.split("ASSISTANT:")[-1].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error analyzing single frame: {e}")
            return f"Analysis failed: {str(e)}"
    
    def _detect_objects(self, image: Image.Image) -> List[Dict]:
        """Detect specific objects relevant to police encounters"""
        try:
            # This is a simplified object detection
            # In production, you might use YOLO or similar for specific object detection
            
            objects_prompt = """List any of these objects visible in the image:
            - Weapons (guns, tasers, batons, knives)
            - Restraints (handcuffs, zip ties)
            - Vehicles (police cars, motorcycles)
            - Protective equipment (vests, helmets)
            - Recording devices (body cameras, phones)
            - Medical equipment
            - Crowd control items
            Format as a simple list."""
            
            detection_result = self._analyze_single_frame(image, 'general')
            
            # Parse the result to extract object information
            # This is simplified - in production you'd use proper object detection
            objects = []
            object_keywords = {
                'weapon': ['gun', 'pistol', 'taser', 'baton', 'knife', 'firearm'],
                'restraint': ['handcuff', 'zip tie', 'restraint', 'cuff'],
                'vehicle': ['police car', 'patrol car', 'motorcycle', 'cruiser'],
                'equipment': ['vest', 'helmet', 'body cam', 'radio', 'badge']
            }
            
            detection_lower = detection_result.lower()
            for category, keywords in object_keywords.items():
                for keyword in keywords:
                    if keyword in detection_lower:
                        objects.append({
                            'category': category,
                            'object': keyword,
                            'confidence': 0.8  # Placeholder confidence
                        })
            
            return objects
            
        except Exception as e:
            logger.error(f"Error detecting objects: {e}")
            return []
    
    def _calculate_scene_confidence(self, image: Image.Image) -> float:
        """Calculate confidence score for scene analysis"""
        try:
            # Simple heuristic based on image quality and clarity
            # Convert to numpy for analysis
            img_array = np.array(image)
            
            # Calculate image metrics
            brightness = np.mean(img_array)
            contrast = np.std(img_array)
            
            # Normalize confidence score
            # Higher contrast and moderate brightness indicate clearer images
            confidence = min(1.0, (contrast / 255.0) * (1.0 - abs(brightness - 128) / 128.0))
            
            return max(0.1, confidence)  # Minimum confidence of 0.1
            
        except Exception as e:
            logger.error(f"Error calculating scene confidence: {e}")
            return 0.5
    
    def analyze_text_for_violations(self, text: str) -> List[Dict]:
        """Analyze transcript text for potential violations"""
        try:
            violation_indicators = {
                'racial_slurs': [
                    'racial slur patterns',  # You'd implement actual pattern matching
                ],
                'threats': [
                    'kill', 'hurt', 'beat', 'destroy', 'harm', 'shoot'
                ],
                'profanity': [
                    'excessive profanity patterns'
                ],
                'commands': [
                    'stop resisting', 'get down', 'hands up', 'don\'t move'
                ],
                'medical_concerns': [
                    'can\'t breathe', 'help', 'pain', 'hurt', 'medical', 'ambulance'
                ],
                'miranda_rights': [
                    'right to remain silent', 'right to attorney', 'miranda'
                ]
            }
            
            violations = []
            text_lower = text.lower()
            
            for category, indicators in violation_indicators.items():
                for indicator in indicators:
                    if indicator in text_lower:
                        violations.append({
                            'category': category,
                            'indicator': indicator,
                            'severity': self._assess_violation_severity(category),
                            'context': self._extract_context(text, indicator)
                        })
            
            return violations
            
        except Exception as e:
            logger.error(f"Error analyzing text for violations: {e}")
            return []
    
    def _assess_violation_severity(self, category: str) -> str:
        """Assess severity level of detected violation"""
        severity_map = {
            'racial_slurs': 'high',
            'threats': 'high',
            'profanity': 'medium',
            'commands': 'low',
            'medical_concerns': 'high',
            'miranda_rights': 'medium'
        }
        return severity_map.get(category, 'medium')
    
    def _extract_context(self, text: str, indicator: str, context_length: int = 50) -> str:
        """Extract context around violation indicator"""
        try:
            text_lower = text.lower()
            indicator_pos = text_lower.find(indicator)
            
            if indicator_pos == -1:
                return ""
            
            start = max(0, indicator_pos - context_length)
            end = min(len(text), indicator_pos + len(indicator) + context_length)
            
            context = text[start:end].strip()
            return context
            
        except Exception as e:
            logger.error(f"Error extracting context: {e}")
            return ""