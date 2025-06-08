"""
Audio Analysis Service for Video Analyzer Platform

Provides comprehensive audio analysis including:
- Whisper-based transcription with hallucination detection
- Audio quality assessment and noise detection
- Speaker diarization and emotion analysis
- Integration with video timeline for synchronized analysis
"""

import os
import logging
import tempfile
import numpy as np
import librosa
import whisper
import torch
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import moviepy.editor as mp
from scipy import signal
from scipy.stats import entropy
import re
import time

logger = logging.getLogger(__name__)

@dataclass
class AudioSegment:
    """Represents a segment of audio with metadata"""
    start_time: float
    end_time: float
    duration: float
    audio_data: np.ndarray
    sample_rate: int
    rms_energy: float
    spectral_centroid: float
    zero_crossing_rate: float
    is_speech: bool
    confidence: float

@dataclass
class TranscriptionSegment:
    """Represents a transcribed segment with confidence metrics"""
    start_time: float
    end_time: float
    text: str
    confidence: float
    language: str
    is_hallucination: bool
    hallucination_indicators: List[str]
    speaker_id: Optional[str] = None
    emotion: Optional[str] = None

@dataclass
class AudioAnalysisResult:
    """Complete audio analysis result"""
    transcription_segments: List[TranscriptionSegment]
    audio_quality_metrics: Dict[str, Any]
    speech_timeline: List[Dict[str, Any]]
    noise_segments: List[Dict[str, Any]]
    total_speech_duration: float
    total_silence_duration: float
    average_confidence: float
    detected_languages: List[str]
    processing_time: float

class AudioAnalysisService:
    """Service for comprehensive audio analysis with Whisper integration"""
    
    def __init__(self):
        self.whisper_model = None
        self.model_size = "base"  # Start with base model for speed
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Hallucination detection parameters
        self.hallucination_patterns = [
            # YouTube/social media patterns (keep these)
            r'\b(thank you|thanks)\b.*\b(watching|listening)\b',
            r'\bsubscribe\b.*\bchannel\b',
            r'\blike\b.*\bcomment\b',
            
            # Music patterns (but be more specific)
            r'\b(background|ambient)\s+music\b.*\b(playing|in the background)\b',
            r'^\s*[♪♫🎵🎶]+\s*$',  # Only pure music symbols
            r'^\s*\[.*music.*\]\s*$',  # Bracketed music descriptions
            
            # Very obvious noise patterns
            r'^\s*\(.*static.*\)\s*$',      # Parenthetical static descriptions
            r'^\s*\[.*static.*\]\s*$',      # Bracketed static descriptions
            r'^\s*\(.*silence.*\)\s*$',     # Parenthetical silence descriptions
            r'^\s*\[.*silence.*\]\s*$',     # Bracketed silence descriptions
            
            # Removed overly broad patterns that might catch valid speech:
            # - r'\bmusic\b.*\bplaying\b'  (might catch "music playing in car")
            # - r'\b(silence|quiet|nothing)\b'  (might catch "it's quiet" or "nothing happened")
            # - r'\b(static|noise|hum)\b'  (might catch "static on radio" or "noise outside")
        ]
        
        # Audio quality thresholds
        self.min_speech_energy = 0.005  # More sensitive (was 0.01)
        self.min_segment_duration = 0.5  # Keep short
        self.max_silence_gap = 2.0
        self.confidence_threshold = 0.4  # Less aggressive (was 0.6) for bodycam quality audio
        
    def _load_whisper_model(self, model_size: str = None) -> whisper.Whisper:
        """Load Whisper model with specified size"""
        if model_size:
            self.model_size = model_size
            
        if self.whisper_model is None or model_size:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.whisper_model = whisper.load_model(self.model_size, device=self.device)
            
        return self.whisper_model
    
    def extract_audio_from_video(self, video_path: str, output_path: str = None) -> str:
        """Extract audio from video file"""
        try:
            if output_path is None:
                output_path = tempfile.mktemp(suffix=".wav")
                
            logger.info(f"Extracting audio from {video_path}")
            video = mp.VideoFileClip(video_path)
            audio = video.audio
            
            if audio is None:
                raise ValueError("No audio track found in video")
                
            audio.write_audiofile(output_path, verbose=False, logger=None)
            video.close()
            audio.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            raise
    
    def analyze_audio_quality(self, audio_path: str) -> Dict[str, Any]:
        """Analyze audio quality and detect noise characteristics"""
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            
            # Basic metrics
            duration = len(y) / sr
            rms_energy = np.sqrt(np.mean(y**2))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            
            # MFCC features for speech detection
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Detect silence segments
            silence_threshold = np.percentile(np.abs(y), 20)
            silence_mask = np.abs(y) < silence_threshold
            
            # Calculate noise floor
            noise_floor = np.percentile(np.abs(y), 10)
            
            # Signal-to-noise ratio estimation
            signal_power = np.mean(y**2)
            noise_power = noise_floor**2
            snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float('inf')
            
            return {
                'duration': duration,
                'sample_rate': sr,
                'rms_energy': float(rms_energy),
                'mean_spectral_centroid': float(np.mean(spectral_centroids)),
                'mean_spectral_rolloff': float(np.mean(spectral_rolloff)),
                'mean_zero_crossing_rate': float(np.mean(zero_crossing_rate)),
                'silence_percentage': float(np.sum(silence_mask) / len(y) * 100),
                'noise_floor': float(noise_floor),
                'estimated_snr': float(snr),
                'has_speech_characteristics': self._has_speech_characteristics(mfccs),
                'audio_quality_score': self._calculate_quality_score(rms_energy, snr, spectral_centroids)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audio quality: {str(e)}")
            return {}
    
    def _has_speech_characteristics(self, mfccs: np.ndarray) -> bool:
        """Determine if audio has speech-like characteristics"""
        # Speech typically has specific MFCC patterns
        mfcc_variance = np.var(mfccs, axis=1)
        mfcc_mean = np.mean(mfccs, axis=1)
        
        # Speech indicators
        has_formant_structure = np.any(mfcc_variance[1:4] > 0.5)  # Formant regions
        has_dynamic_range = np.std(mfcc_mean) > 0.3
        
        return has_formant_structure and has_dynamic_range
    
    def _calculate_quality_score(self, rms_energy: float, snr: float, spectral_centroids: np.ndarray) -> float:
        """Calculate overall audio quality score (0-1) with improved methodology"""
        try:
            # Energy score (0-1) - more realistic thresholds
            # Typical speech RMS energy ranges from 0.01 to 0.3
            energy_score = min(max(rms_energy / 0.2, 0.1), 1.0)  # Better normalization
            
            # SNR score (0-1) - handle edge cases better
            if snr == float('inf') or snr > 30:
                snr_score = 1.0
            elif snr < 0:
                snr_score = 0.1  # Minimum score for very poor SNR
            else:
                snr_score = min(max(snr / 25, 0.1), 1.0)  # Normalize to 25dB max
            
            # Spectral consistency score - improved calculation
            if len(spectral_centroids) > 1:
                spectral_mean = np.mean(spectral_centroids)
                spectral_std = np.std(spectral_centroids)
                
                # Normalize by mean to get coefficient of variation
                if spectral_mean > 0:
                    cv = spectral_std / spectral_mean
                    # Good speech has CV between 0.1-0.3, beyond that indicates noise or silence
                    if cv < 0.1:
                        consistency_score = 0.6  # Too consistent (might be silence/noise)
                    elif cv > 0.5:
                        consistency_score = 0.4  # Too variable (noise)
                    else:
                        consistency_score = 1.0 - abs(cv - 0.2) * 2  # Optimal around 0.2
                else:
                    consistency_score = 0.1
            else:
                consistency_score = 0.5
            
            # Frequency content score - check if spectral content is in speech range
            if len(spectral_centroids) > 0:
                mean_centroid = np.mean(spectral_centroids)
                # Human speech typically has spectral centroid 500-2000 Hz
                if 500 <= mean_centroid <= 3000:
                    freq_score = 1.0
                elif 200 <= mean_centroid <= 5000:
                    freq_score = 0.7
                else:
                    freq_score = 0.3
            else:
                freq_score = 0.1
            
            # Weighted combination with emphasis on SNR and frequency content for speech
            final_score = (
                energy_score * 0.25 + 
                snr_score * 0.35 + 
                consistency_score * 0.20 + 
                freq_score * 0.20
            )
            
            # Ensure minimum quality floor and reasonable range
            return max(0.05, min(1.0, final_score))
            
        except Exception as e:
            logger.error(f"Error calculating audio quality score: {e}")
            return 0.1  # Fallback score
    
    def segment_audio_by_activity(self, audio_path: str, min_segment_duration: float = 1.0) -> List[AudioSegment]:
        """Segment audio based on speech activity detection"""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            
            # Voice Activity Detection using energy and spectral features
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.010 * sr)    # 10ms hop
            
            # Calculate frame-wise features with proper alignment
            # Ensure both features have same number of frames
            num_frames = 1 + int((len(y) - frame_length) / hop_length)
            
            # Energy-based VAD
            frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
            frame_energy = np.sum(frames**2, axis=0)
            
            # Spectral centroid-based VAD (ensure same frame count)
            spectral_centroids = librosa.feature.spectral_centroid(
                y=y, sr=sr, hop_length=hop_length, n_fft=frame_length
            )[0]
            
            # Ensure arrays have same length by truncating to minimum
            min_len = min(len(frame_energy), len(spectral_centroids))
            frame_energy = frame_energy[:min_len]
            spectral_centroids = spectral_centroids[:min_len]
            
            # Much more sensitive thresholds for bodycam footage
            # Use percentile-based thresholds instead of absolute values
            energy_threshold = np.percentile(frame_energy, 15)  # More sensitive (was 20)
            centroid_threshold = np.percentile(spectral_centroids, 20)  # More sensitive (was 25)
            
            # Zero crossing rate for additional validation
            zcr = librosa.feature.zero_crossing_rate(y, frame_length=frame_length, hop_length=hop_length)[0]
            zcr = zcr[:min_len]  # Ensure same length
            zcr_threshold = np.percentile(zcr, 40)  # More sensitive (was 60)
            
            # Much more permissive speech detection - use OR instead of AND for some criteria
            speech_frames = (
                (frame_energy > energy_threshold) &  # Basic energy requirement
                (
                    (spectral_centroids > centroid_threshold) |  # OR speech-like spectrum
                    (zcr > zcr_threshold) |  # OR high zero-crossing (consonants)
                    (frame_energy > np.percentile(frame_energy, 30))  # OR higher energy
                )
            )
            
            # If still no speech detected, use very lenient criteria
            if not np.any(speech_frames):
                logger.warning("No speech detected with normal criteria, using very lenient detection")
                # Use just energy above median with any spectral activity
                speech_frames = (
                    (frame_energy > np.percentile(frame_energy, 50)) &
                    (spectral_centroids > np.percentile(spectral_centroids, 10))
                )
            
            # If STILL nothing detected, use adaptive threshold
            if not np.any(speech_frames):
                logger.warning("Still no speech detected, using adaptive threshold")
                # Find frames with any significant energy variation
                energy_std = np.std(frame_energy)
                energy_mean = np.mean(frame_energy)
                adaptive_threshold = energy_mean + (energy_std * 0.5)  # Half standard deviation above mean
                
                speech_frames = frame_energy > adaptive_threshold
            
            # Convert frame indices to time
            frame_times = librosa.frames_to_time(np.arange(len(speech_frames)), sr=sr, hop_length=hop_length)
            
            # Find speech segments with more aggressive grouping
            segments = []
            in_speech = False
            start_time = 0
            min_gap = 0.3  # Smaller gap requirement (was implicit 1 frame)
            
            for i, (time, is_speech) in enumerate(zip(frame_times, speech_frames)):
                if is_speech and not in_speech:
                    start_time = time
                    in_speech = True
                elif not is_speech and in_speech:
                    # Check if gap to next speech is small
                    next_speech_idx = None
                    for j in range(i, min(i + int(min_gap / 0.01), len(speech_frames))):
                        if speech_frames[j]:
                            next_speech_idx = j
                            break
                    
                    # If next speech is close, continue current segment
                    if next_speech_idx is not None:
                        continue
                    
                    duration = time - start_time
                    if duration >= min_segment_duration:
                        # Extract segment audio
                        start_sample = int(start_time * sr)
                        end_sample = int(time * sr)
                        segment_audio = y[start_sample:end_sample]
                        
                        if len(segment_audio) > 0:  # Ensure non-empty segment
                            # Calculate segment features
                            rms_energy = np.sqrt(np.mean(segment_audio**2))
                            seg_centroids = librosa.feature.spectral_centroid(y=segment_audio, sr=sr)[0]
                            zcr_seg = librosa.feature.zero_crossing_rate(segment_audio)[0]
                            
                            segments.append(AudioSegment(
                                start_time=start_time,
                                end_time=time,
                                duration=duration,
                                audio_data=segment_audio,
                                sample_rate=sr,
                                rms_energy=float(rms_energy),
                                spectral_centroid=float(np.mean(seg_centroids)),
                                zero_crossing_rate=float(np.mean(zcr_seg)),
                                is_speech=True,
                                confidence=min(rms_energy * 3, 1.0)  # More generous confidence
                            ))
                    in_speech = False
            
            # Handle case where audio ends in speech
            if in_speech:
                end_time = len(y) / sr
                duration = end_time - start_time
                if duration >= min_segment_duration:
                    start_sample = int(start_time * sr)
                    segment_audio = y[start_sample:]
                    
                    if len(segment_audio) > 0:
                        rms_energy = np.sqrt(np.mean(segment_audio**2))
                        seg_centroids = librosa.feature.spectral_centroid(y=segment_audio, sr=sr)[0]
                        zcr_seg = librosa.feature.zero_crossing_rate(segment_audio)[0]
                        
                        segments.append(AudioSegment(
                            start_time=start_time,
                            end_time=end_time,
                            duration=duration,
                            audio_data=segment_audio,
                            sample_rate=sr,
                            rms_energy=float(rms_energy),
                            spectral_centroid=float(np.mean(seg_centroids)),
                            zero_crossing_rate=float(np.mean(zcr_seg)),
                            is_speech=True,
                            confidence=min(rms_energy * 3, 1.0)
                        ))
            
            logger.info(f"Detected {len(segments)} speech segments from audio using enhanced VAD")
            return segments
            
        except Exception as e:
            logger.error(f"Error segmenting audio: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def detect_hallucinations(self, text: str, confidence: float, segment_duration: float) -> Tuple[bool, List[str]]:
        """Detect potential Whisper hallucinations"""
        indicators = []
        is_hallucination = False
        
        # Pattern-based detection
        for pattern in self.hallucination_patterns:
            if re.search(pattern, text.lower()):
                indicators.append(f"Suspicious pattern: {pattern}")
                is_hallucination = True
        
        # Confidence-based detection
        if confidence < self.confidence_threshold:
            indicators.append(f"Low confidence: {confidence:.2f}")
            is_hallucination = True
        
        # Repetition detection
        words = text.split()
        if len(words) > 3:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            max_repetition = max(word_counts.values()) if word_counts else 0
            if max_repetition > len(words) * 0.3:
                indicators.append("Excessive word repetition")
                is_hallucination = True
        
        # Length vs duration mismatch
        expected_words_per_second = 2.5  # Average speaking rate
        expected_words = segment_duration * expected_words_per_second
        actual_words = len(words)
        
        if actual_words > expected_words * 2:
            indicators.append("Unrealistic speaking rate")
            is_hallucination = True
        
        # Generic/filler content detection
        generic_phrases = ['um', 'uh', 'you know', 'like', 'so', 'well']
        generic_count = sum(1 for phrase in generic_phrases if phrase in text.lower())
        if generic_count > len(words) * 0.5:
            indicators.append("Excessive filler words")
            is_hallucination = True
        
        return is_hallucination, indicators
    
    def transcribe_audio_segments(self, audio_segments: List[AudioSegment], model_size: str = "base") -> List[TranscriptionSegment]:
        """Transcribe audio segments using Whisper with hallucination detection"""
        model = self._load_whisper_model(model_size)
        transcription_segments = []
        
        for i, segment in enumerate(audio_segments):
            try:
                # Create temporary file for segment with better cleanup
                import tempfile
                import soundfile as sf
                import os
                
                # Use a more robust temporary file approach
                temp_fd, temp_path = tempfile.mkstemp(suffix=".wav", prefix="whisper_segment_")
                
                try:
                    # Close the file descriptor and write with soundfile
                    os.close(temp_fd)
                    sf.write(temp_path, segment.audio_data, segment.sample_rate)
                    
                    # Transcribe with Whisper - more restrictive settings to reduce hallucinations
                    result = model.transcribe(
                        temp_path,
                        language="en",  # Force English to prevent Korean/Japanese hallucinations
                        task="transcribe",
                        verbose=False,
                        condition_on_previous_text=False,  # Reduce hallucinations
                        temperature=0.0,  # Deterministic output
                        compression_ratio_threshold=2.4,
                        logprob_threshold=-0.5,  # More restrictive than default -1.0
                        no_speech_threshold=0.8,  # Higher threshold to avoid noise (was 0.6)
                        initial_prompt="This is a police bodycam recording with clear English speech."  # Context hint
                    )
                    
                except Exception as transcribe_error:
                    logger.error(f"Error during transcription of segment {i}: {str(transcribe_error)}")
                    continue
                    
                finally:
                    # Ensure cleanup even if transcription fails
                    try:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                    except Exception as cleanup_error:
                        logger.warning(f"Could not cleanup temp file {temp_path}: {str(cleanup_error)}")
                
                # Extract transcription details
                text = result.get('text', '').strip()
                language = result.get('language', 'en')
                
                # Skip empty transcriptions
                if not text:
                    continue
                
                # Calculate confidence from segments if available
                confidence = 0.0
                if 'segments' in result and result['segments']:
                    confidences = []
                    for seg in result['segments']:
                        if 'avg_logprob' in seg:
                            # Convert log probability to confidence (more conservative)
                            conf = min(np.exp(seg['avg_logprob']), 1.0)
                            confidences.append(conf)
                    confidence = np.mean(confidences) if confidences else 0.0
                else:
                    # Fallback confidence based on audio quality
                    confidence = min(segment.confidence, 0.8)  # Cap at 0.8 for VAD-based confidence
                
                # Enhanced hallucination detection
                is_hallucination, indicators = self.detect_hallucinations(
                    text, confidence, segment.duration
                )
                
                # Additional checks for English-forced transcriptions
                if language != 'en' and language != 'english':
                    indicators.append(f"Non-English language detected: {language}")
                    is_hallucination = True
                
                # Check for very short segments with long text (often hallucinations)
                words_per_second = len(text.split()) / segment.duration
                if words_per_second > 4.0:  # More restrictive than before
                    indicators.append(f"Unrealistic speech rate: {words_per_second:.1f} words/sec")
                    is_hallucination = True
                
                # Create transcription segment
                transcription_segments.append(TranscriptionSegment(
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    text=text,
                    confidence=confidence,
                    language=language,
                    is_hallucination=is_hallucination,
                    hallucination_indicators=indicators
                ))
                
                # Log results for debugging
                if is_hallucination:
                    logger.warning(f"Segment {i} ({segment.start_time:.1f}s) flagged as hallucination: {text[:50]}... (reasons: {', '.join(indicators)})")
                else:
                    logger.info(f"Segment {i} ({segment.start_time:.1f}s) transcribed: {text[:50]}... (confidence: {confidence:.2f})")
                
            except Exception as e:
                logger.error(f"Error transcribing segment {i} at {segment.start_time}-{segment.end_time}: {str(e)}")
                continue
        
        logger.info(f"Transcribed {len(transcription_segments)} segments, {len([s for s in transcription_segments if not s.is_hallucination])} valid")
        return transcription_segments
    
    def analyze_video_audio(self, video_path: str, model_size: str = "base") -> AudioAnalysisResult:
        """
        Complete audio analysis pipeline for video files
        """
        start_time = time.time()
        
        try:
            logger.info(f"Extracting audio from {video_path}")
            
            # Step 1: Extract audio from video
            audio_path = self.extract_audio_from_video(video_path)
            
            # Step 2: Analyze audio quality
            quality_metrics = self.analyze_audio_quality(audio_path)
            
            # Step 3: Segment audio by speech activity
            audio_segments = self.segment_audio_by_activity(audio_path, min_segment_duration=0.5)
            
            # Step 4: Fallback if no segments detected - use whole audio approach
            if not audio_segments:
                logger.warning("No speech segments detected with VAD, trying Whisper on full audio")
                audio_segments = self._create_fixed_segments(audio_path, segment_duration=30.0)
            
            # Step 5: Transcribe segments
            transcription_segments = self.transcribe_audio_segments(audio_segments, model_size)
            
            # Step 6: Create analysis timeline and noise segments
            speech_timeline = self._create_speech_timeline(audio_segments)
            noise_segments = self._identify_noise_segments(audio_path, audio_segments)
            
            # Step 7: Calculate summary statistics
            total_speech_duration = sum(seg.duration for seg in audio_segments)
            total_silence_duration = quality_metrics.get('duration', 0) - total_speech_duration
            
            valid_transcriptions = [seg for seg in transcription_segments if not seg.is_hallucination]
            average_confidence = np.mean([seg.confidence for seg in valid_transcriptions]) if valid_transcriptions else 0.0
            detected_languages = list(set(seg.language for seg in valid_transcriptions))
            
            processing_time = time.time() - start_time
            
            return AudioAnalysisResult(
                transcription_segments=transcription_segments,
                audio_quality_metrics=quality_metrics,
                speech_timeline=speech_timeline,
                noise_segments=noise_segments,
                total_speech_duration=total_speech_duration,
                total_silence_duration=total_silence_duration,
                average_confidence=average_confidence,
                detected_languages=detected_languages,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in audio analysis: {str(e)}")
            raise
        finally:
            # Cleanup temporary audio file
            if 'audio_path' in locals() and audio_path and os.path.exists(audio_path):
                try:
                    os.unlink(audio_path)
                except:
                    pass
    
    def _create_fixed_segments(self, audio_path: str, segment_duration: float = 15.0) -> List[AudioSegment]:
        """Create fixed-duration segments as fallback when VAD fails"""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            
            segments = []
            current_time = 0
            
            # Use shorter segments for better transcription quality
            while current_time < duration:
                end_time = min(current_time + segment_duration, duration)
                start_sample = int(current_time * sr)
                end_sample = int(end_time * sr)
                
                segment_audio = y[start_sample:end_sample]
                
                if len(segment_audio) > sr * 0.5:  # At least 0.5 seconds
                    # Calculate basic features for filtering
                    rms_energy = np.sqrt(np.mean(segment_audio**2))
                    
                    # More selective - only include segments with reasonable energy
                    # But be more generous than before
                    energy_threshold = np.percentile(np.abs(y), 15)  # Use percentile of whole audio
                    
                    if rms_energy > energy_threshold:
                        # Additional quality check - spectral content
                        spectral_centroids = librosa.feature.spectral_centroid(y=segment_audio, sr=sr)[0]
                        mean_centroid = np.mean(spectral_centroids)
                        
                        # Include if has reasonable spectral content (not just pure noise)
                        if mean_centroid > 200:  # Hz - basic speech frequency range
                            segments.append(AudioSegment(
                                start_time=current_time,
                                end_time=end_time,
                                duration=end_time - current_time,
                                audio_data=segment_audio,
                                sample_rate=sr,
                                rms_energy=float(rms_energy),
                                spectral_centroid=float(mean_centroid),
                                zero_crossing_rate=0.0,  # Simplified
                                is_speech=True,  # Assume speech for transcription
                                confidence=min(rms_energy * 2, 0.7)  # Conservative confidence
                            ))
                
                current_time += segment_duration
            
            logger.info(f"Created {len(segments)} fixed segments as VAD fallback (filtered from {int(duration/segment_duration)} total)")
            return segments
            
        except Exception as e:
            logger.error(f"Error creating fixed segments: {str(e)}")
            return []
    
    def _create_speech_timeline(self, audio_segments: List[AudioSegment]) -> List[Dict[str, Any]]:
        """Create timeline of speech activity"""
        timeline = []
        for segment in audio_segments:
            timeline.append({
                'start_time': segment.start_time,
                'end_time': segment.end_time,
                'duration': segment.duration,
                'rms_energy': segment.rms_energy,
                'spectral_centroid': segment.spectral_centroid,
                'confidence': segment.confidence,
                'is_speech': segment.is_speech
            })
        return timeline
    
    def _identify_noise_segments(self, audio_path: str, speech_segments: List[AudioSegment]) -> List[Dict[str, Any]]:
        """Identify noise/silence segments between speech"""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            total_duration = len(y) / sr
            
            noise_segments = []
            
            if not speech_segments:
                # Entire audio is noise/silence
                noise_segments.append({
                    'start_time': 0.0,
                    'end_time': total_duration,
                    'duration': total_duration,
                    'type': 'silence_or_noise'
                })
                return noise_segments
            
            # Sort speech segments by start time
            speech_segments_sorted = sorted(speech_segments, key=lambda x: x.start_time)
            
            # Check for noise at beginning
            if speech_segments_sorted[0].start_time > 0.5:
                noise_segments.append({
                    'start_time': 0.0,
                    'end_time': speech_segments_sorted[0].start_time,
                    'duration': speech_segments_sorted[0].start_time,
                    'type': 'silence_or_noise'
                })
            
            # Check for gaps between speech segments
            for i in range(len(speech_segments_sorted) - 1):
                gap_start = speech_segments_sorted[i].end_time
                gap_end = speech_segments_sorted[i + 1].start_time
                gap_duration = gap_end - gap_start
                
                if gap_duration > 0.5:  # Significant gap
                    noise_segments.append({
                        'start_time': gap_start,
                        'end_time': gap_end,
                        'duration': gap_duration,
                        'type': 'silence_or_noise'
                    })
            
            # Check for noise at end
            last_speech_end = speech_segments_sorted[-1].end_time
            if total_duration - last_speech_end > 0.5:
                noise_segments.append({
                    'start_time': last_speech_end,
                    'end_time': total_duration,
                    'duration': total_duration - last_speech_end,
                    'type': 'silence_or_noise'
                })
            
            return noise_segments
            
        except Exception as e:
            logger.error(f"Error identifying noise segments: {str(e)}")
            return []
    
    def format_transcript_for_report(self, transcription_segments: List[TranscriptionSegment], 
                                   include_timestamps: bool = True, 
                                   include_confidence: bool = False) -> str:
        """Format transcription segments for inclusion in reports"""
        if not transcription_segments:
            return "No speech detected in audio."
        
        # Filter out hallucinations
        valid_segments = [seg for seg in transcription_segments if not seg.is_hallucination]
        
        if not valid_segments:
            return "No reliable speech transcription available (potential hallucinations filtered out)."
        
        formatted_lines = []
        
        for segment in valid_segments:
            line_parts = []
            
            if include_timestamps:
                start_min = int(segment.start_time // 60)
                start_sec = int(segment.start_time % 60)
                end_min = int(segment.end_time // 60)
                end_sec = int(segment.end_time % 60)
                timestamp = f"[{start_min:02d}:{start_sec:02d}-{end_min:02d}:{end_sec:02d}]"
                line_parts.append(timestamp)
            
            line_parts.append(segment.text)
            
            if include_confidence:
                line_parts.append(f"(confidence: {segment.confidence:.2f})")
            
            formatted_lines.append(" ".join(line_parts))
        
        return "\n".join(formatted_lines) 