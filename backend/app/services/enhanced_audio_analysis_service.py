"""
Enhanced Audio Analysis Service with Speaker Diarization
Extends the base audio analysis with speaker identification for bodycam footage.
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
import re
from datetime import datetime
import soundfile as sf
import time

# For speaker diarization
try:
    from pyannote.audio import Pipeline
    from pyannote.core import Segment
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    logging.warning("pyannote.audio not available. Speaker diarization will be disabled.")

from .audio_analysis_service import (
    AudioAnalysisService, 
    AudioSegment, 
    TranscriptionSegment, 
    AudioAnalysisResult
)

logger = logging.getLogger(__name__)

@dataclass
class SpeakerSegment:
    """Represents a speaker segment with identification"""
    start_time: float
    end_time: float
    speaker_id: str
    speaker_label: str  # "Officer with Camera", "Officer 1", "Suspect", etc.
    confidence: float

@dataclass
class EnhancedTranscriptionSegment(TranscriptionSegment):
    """Enhanced transcription segment with speaker information"""
    speaker_id: Optional[str] = None
    speaker_label: Optional[str] = None
    speaker_confidence: Optional[float] = None

@dataclass
class EnhancedAudioAnalysisResult(AudioAnalysisResult):
    """Enhanced audio analysis result with speaker diarization"""
    speaker_segments: List[SpeakerSegment] = None
    speaker_timeline: List[Dict[str, Any]] = None
    identified_speakers: Dict[str, str] = None
    speaker_statistics: Dict[str, Any] = None

class EnhancedAudioAnalysisService(AudioAnalysisService):
    """Enhanced service with speaker diarization for bodycam footage"""
    
    def __init__(self):
        super().__init__()
        self.diarization_pipeline = None
        self.speaker_labels = {
            'primary_officer': 'Officer with Camera',
            'officer_1': 'Officer 1', 
            'officer_2': 'Officer 2',
            'officer_3': 'Officer 3',
            'suspect': 'Suspect',
            'civilian_1': 'Civilian 1',
            'civilian_2': 'Civilian 2',
            'unknown': 'Unknown Speaker'
        }
        
        # Initialize speaker diarization if available
        if PYANNOTE_AVAILABLE:
            self._initialize_diarization_pipeline()
        
    def _initialize_diarization_pipeline(self):
        """Initialize the speaker diarization pipeline"""
        try:
            # Use a simpler pipeline that doesn't require HuggingFace token
            # This is a basic version - for production, you'd want the full pipeline
            logger.info("Initializing speaker diarization pipeline...")
            # For now, we'll use a simple voice activity detection approach
            # In production, you would use:
            # self.diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
            logger.info("Speaker diarization initialized (basic mode)")
        except Exception as e:
            logger.warning(f"Could not initialize speaker diarization: {e}")
            self.diarization_pipeline = None
    
    def analyze_video_audio_with_speakers(self, video_path: str, model_size: str = "base") -> EnhancedAudioAnalysisResult:
        """
        Complete audio analysis with speaker diarization for bodycam footage
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting enhanced audio analysis with speaker diarization for {video_path}")
            
            # Step 1: Run base audio analysis
            base_result = super().analyze_video_audio(video_path, model_size)
            
            # Step 2: Extract audio for speaker diarization
            audio_path = self.extract_audio_from_video(video_path)
            
            # Step 3: Perform speaker diarization
            speaker_segments = self._perform_speaker_diarization(audio_path)
            
            # Step 4: Match speakers to transcription segments
            enhanced_segments = self._match_speakers_to_transcription(
                base_result.transcription_segments, 
                speaker_segments
            )
            
            # Step 5: Generate speaker labels for bodycam context
            identified_speakers = self._identify_bodycam_speakers(speaker_segments, enhanced_segments)
            
            # Step 6: Create speaker timeline and statistics
            speaker_timeline = self._create_speaker_timeline(speaker_segments, identified_speakers)
            speaker_statistics = self._calculate_speaker_statistics(speaker_segments, identified_speakers)
            
            processing_time = time.time() - start_time
            
            # Create enhanced result
            enhanced_result = EnhancedAudioAnalysisResult(
                transcription_segments=enhanced_segments,
                audio_quality_metrics=base_result.audio_quality_metrics,
                speech_timeline=base_result.speech_timeline,
                noise_segments=base_result.noise_segments,
                total_speech_duration=base_result.total_speech_duration,
                total_silence_duration=base_result.total_silence_duration,
                average_confidence=base_result.average_confidence,
                detected_languages=base_result.detected_languages,
                processing_time=processing_time,
                speaker_segments=speaker_segments,
                speaker_timeline=speaker_timeline,
                identified_speakers=identified_speakers,
                speaker_statistics=speaker_statistics
            )
            
            logger.info(f"Enhanced audio analysis completed in {processing_time:.2f}s")
            logger.info(f"Identified {len(identified_speakers)} speakers: {list(identified_speakers.values())}")
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in enhanced audio analysis: {str(e)}")
            # Fall back to base analysis if speaker diarization fails
            base_result = super().analyze_video_audio(video_path, model_size)
            return self._convert_to_enhanced_result(base_result)
        finally:
            # Cleanup
            if 'audio_path' in locals() and audio_path and os.path.exists(audio_path):
                try:
                    os.unlink(audio_path)
                except:
                    pass
    
    def _perform_speaker_diarization(self, audio_path: str) -> List[SpeakerSegment]:
        """Perform speaker diarization on audio file"""
        speaker_segments = []
        
        try:
            if not PYANNOTE_AVAILABLE or self.diarization_pipeline is None:
                # Fallback: Use voice activity and simple clustering
                return self._simple_speaker_detection(audio_path)
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)  # 16kHz for diarization
            
            # For now, implement a simple approach based on audio characteristics
            # In production, you would use the full pyannote pipeline
            return self._simple_speaker_detection(audio_path)
            
        except Exception as e:
            logger.error(f"Error in speaker diarization: {e}")
            return self._simple_speaker_detection(audio_path)
    
    def _simple_speaker_detection(self, audio_path: str) -> List[SpeakerSegment]:
        """Simple speaker detection based on audio characteristics"""
        speaker_segments = []
        
        try:
            y, sr = librosa.load(audio_path, sr=None)
            
            # Use MFCC features for simple speaker clustering
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Simple approach: detect major audio changes that might indicate speaker changes
            # This is a placeholder - real implementation would use proper clustering
            
            # For bodycam footage, assume primary speaker is the officer wearing the camera
            # Secondary speakers are other voices at different distances/characteristics
            
            # Segment by energy and spectral characteristics
            hop_length = 512
            frame_times = librosa.frames_to_time(np.arange(mfccs.shape[1]), sr=sr, hop_length=hop_length)
            
            # Simple energy-based segmentation
            energy = np.sum(mfccs**2, axis=0)
            
            # Find voice activity regions
            energy_threshold = np.percentile(energy, 70)
            voice_active = energy > energy_threshold
            
            # Create segments for voice activity
            in_speech = False
            start_time = 0
            current_speaker = "SPEAKER_00"  # Default to primary speaker
            
            for i, (time_point, is_active) in enumerate(zip(frame_times, voice_active)):
                if is_active and not in_speech:
                    start_time = time_point
                    in_speech = True
                elif not is_active and in_speech:
                    if time_point - start_time > 1.0:  # Minimum 1 second segments
                        # Simple heuristic: if segment is loud and clear, likely primary officer
                        # If quieter or different characteristics, likely other speaker
                        segment_energy = np.mean(energy[max(0, i-10):i])
                        segment_mfcc_var = np.var(mfccs[:, max(0, i-10):i])
                        
                        # Determine speaker based on audio characteristics
                        if segment_energy > np.percentile(energy, 80) and segment_mfcc_var < np.percentile(np.var(mfccs, axis=1), 60):
                            speaker_id = "SPEAKER_00"  # Primary officer (camera wearer)
                            confidence = 0.8
                        else:
                            speaker_id = "SPEAKER_01"  # Other speaker
                            confidence = 0.6
                        
                        speaker_segments.append(SpeakerSegment(
                            start_time=start_time,
                            end_time=time_point,
                            speaker_id=speaker_id,
                            speaker_label=self.speaker_labels.get('primary_officer' if speaker_id == "SPEAKER_00" else 'officer_1'),
                            confidence=confidence
                        ))
                    
                    in_speech = False
            
            # Handle case where audio ends in speech
            if in_speech and len(frame_times) > 0:
                end_time = frame_times[-1]
                if end_time - start_time > 1.0:
                    speaker_segments.append(SpeakerSegment(
                        start_time=start_time,
                        end_time=end_time,
                        speaker_id="SPEAKER_00",
                        speaker_label=self.speaker_labels['primary_officer'],
                        confidence=0.7
                    ))
            
            logger.info(f"Simple speaker detection found {len(speaker_segments)} speaker segments")
            return speaker_segments
            
        except Exception as e:
            logger.error(f"Error in simple speaker detection: {e}")
            return []
    
    def _match_speakers_to_transcription(self, transcription_segments: List[TranscriptionSegment], 
                                        speaker_segments: List[SpeakerSegment]) -> List[EnhancedTranscriptionSegment]:
        """Match speaker segments to transcription segments"""
        enhanced_segments = []
        
        for trans_seg in transcription_segments:
            # Find the speaker segment that overlaps most with this transcription segment
            best_speaker = None
            best_overlap = 0
            
            for speaker_seg in speaker_segments:
                # Calculate overlap
                overlap_start = max(trans_seg.start_time, speaker_seg.start_time)
                overlap_end = min(trans_seg.end_time, speaker_seg.end_time)
                overlap_duration = max(0, overlap_end - overlap_start)
                
                if overlap_duration > best_overlap:
                    best_overlap = overlap_duration
                    best_speaker = speaker_seg
            
            # Create enhanced segment
            enhanced_seg = EnhancedTranscriptionSegment(
                start_time=trans_seg.start_time,
                end_time=trans_seg.end_time,
                text=trans_seg.text,
                confidence=trans_seg.confidence,
                language=trans_seg.language,
                is_hallucination=trans_seg.is_hallucination,
                hallucination_indicators=trans_seg.hallucination_indicators,
                speaker_id=best_speaker.speaker_id if best_speaker else None,
                speaker_label=best_speaker.speaker_label if best_speaker else "Unknown Speaker",
                speaker_confidence=best_speaker.confidence if best_speaker else 0.0
            )
            
            enhanced_segments.append(enhanced_seg)
        
        return enhanced_segments
    
    def _identify_bodycam_speakers(self, speaker_segments: List[SpeakerSegment], 
                                  transcription_segments: List[EnhancedTranscriptionSegment]) -> Dict[str, str]:
        """Identify speakers in bodycam context"""
        identified_speakers = {}
        
        # Analyze transcription content to help identify speakers
        speaker_content = {}
        
        for trans_seg in transcription_segments:
            if trans_seg.speaker_id and not trans_seg.is_hallucination:
                if trans_seg.speaker_id not in speaker_content:
                    speaker_content[trans_seg.speaker_id] = []
                speaker_content[trans_seg.speaker_id].append(trans_seg.text.lower())
        
        # Analyze content to identify likely roles
        for speaker_id, content_list in speaker_content.items():
            content = " ".join(content_list)
            
            # Look for indicators of different speaker types
            officer_indicators = [
                'you need to', 'come out', 'hands up', 'stop moving', 'get down',
                'we need', 'put your hands', 'step back', 'calm down', 'dispatch',
                'backup', 'supervisor', 'officer', 'police', 'department'
            ]
            
            suspect_indicators = [
                'i need', 'help me', 'i want', 'my kids', 'i don\'t want',
                'leave me alone', 'get away', 'social worker', 'doctor',
                'hospital', 'i\'m not', 'why are you'
            ]
            
            officer_score = sum(1 for indicator in officer_indicators if indicator in content)
            suspect_score = sum(1 for indicator in suspect_indicators if indicator in content)
            
            # Determine speaker role
            if speaker_id == "SPEAKER_00":
                # Primary speaker is usually the officer wearing the camera
                identified_speakers[speaker_id] = self.speaker_labels['primary_officer']
            elif officer_score > suspect_score:
                # Other officers
                officer_num = len([s for s in identified_speakers.values() if 'Officer' in s])
                if officer_num == 0:
                    identified_speakers[speaker_id] = self.speaker_labels['officer_1']
                elif officer_num == 1:
                    identified_speakers[speaker_id] = self.speaker_labels['officer_2']
                else:
                    identified_speakers[speaker_id] = self.speaker_labels['officer_3']
            elif suspect_score > 0:
                # Likely suspect/civilian
                identified_speakers[speaker_id] = self.speaker_labels['suspect']
            else:
                # Unknown
                identified_speakers[speaker_id] = self.speaker_labels['unknown']
        
        return identified_speakers
    
    def _create_speaker_timeline(self, speaker_segments: List[SpeakerSegment], 
                                identified_speakers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create timeline of speaker activity"""
        timeline = []
        
        for segment in speaker_segments:
            speaker_label = identified_speakers.get(segment.speaker_id, segment.speaker_label)
            
            timeline.append({
                'start_time': segment.start_time,
                'end_time': segment.end_time,
                'duration': segment.end_time - segment.start_time,
                'speaker_id': segment.speaker_id,
                'speaker_label': speaker_label,
                'confidence': segment.confidence,
                'start_formatted': f"{int(segment.start_time // 60):02d}:{int(segment.start_time % 60):02d}",
                'end_formatted': f"{int(segment.end_time // 60):02d}:{int(segment.end_time % 60):02d}"
            })
        
        return sorted(timeline, key=lambda x: x['start_time'])
    
    def _calculate_speaker_statistics(self, speaker_segments: List[SpeakerSegment], 
                                     identified_speakers: Dict[str, str]) -> Dict[str, Any]:
        """Calculate statistics about speaker activity"""
        stats = {
            'total_speakers': len(identified_speakers),
            'speaker_talk_time': {},
            'speaker_talk_percentage': {},
            'most_active_speaker': None,
            'primary_officer_percentage': 0.0
        }
        
        total_speech_time = sum(seg.end_time - seg.start_time for seg in speaker_segments)
        
        # Calculate talk time for each speaker
        for speaker_id, speaker_label in identified_speakers.items():
            speaker_time = sum(
                seg.end_time - seg.start_time 
                for seg in speaker_segments 
                if seg.speaker_id == speaker_id
            )
            
            stats['speaker_talk_time'][speaker_label] = speaker_time
            stats['speaker_talk_percentage'][speaker_label] = (
                (speaker_time / total_speech_time * 100) if total_speech_time > 0 else 0
            )
            
            if speaker_label == self.speaker_labels['primary_officer']:
                stats['primary_officer_percentage'] = stats['speaker_talk_percentage'][speaker_label]
        
        # Find most active speaker
        if stats['speaker_talk_time']:
            stats['most_active_speaker'] = max(
                stats['speaker_talk_time'].items(), 
                key=lambda x: x[1]
            )[0]
        
        return stats
    
    def _convert_to_enhanced_result(self, base_result: AudioAnalysisResult) -> EnhancedAudioAnalysisResult:
        """Convert base result to enhanced result (fallback)"""
        # Convert base transcription segments to enhanced ones
        enhanced_segments = []
        for seg in base_result.transcription_segments:
            enhanced_seg = EnhancedTranscriptionSegment(
                start_time=seg.start_time,
                end_time=seg.end_time,
                text=seg.text,
                confidence=seg.confidence,
                language=seg.language,
                is_hallucination=seg.is_hallucination,
                hallucination_indicators=seg.hallucination_indicators,
                speaker_id=None,
                speaker_label="Unknown Speaker",
                speaker_confidence=0.0
            )
            enhanced_segments.append(enhanced_seg)
        
        return EnhancedAudioAnalysisResult(
            transcription_segments=enhanced_segments,
            audio_quality_metrics=base_result.audio_quality_metrics,
            speech_timeline=base_result.speech_timeline,
            noise_segments=base_result.noise_segments,
            total_speech_duration=base_result.total_speech_duration,
            total_silence_duration=base_result.total_silence_duration,
            average_confidence=base_result.average_confidence,
            detected_languages=base_result.detected_languages,
            processing_time=base_result.processing_time,
            speaker_segments=[],
            speaker_timeline=[],
            identified_speakers={},
            speaker_statistics={'total_speakers': 0}
        )
    
    def format_enhanced_transcript_for_report(self, transcription_segments: List[EnhancedTranscriptionSegment], 
                                             include_timestamps: bool = True, 
                                             include_confidence: bool = False,
                                             include_speaker_labels: bool = True) -> str:
        """Format enhanced transcription segments with speaker identification for reports"""
        if not transcription_segments:
            return "No speech detected in audio."
        
        # Filter out hallucinations
        valid_segments = [seg for seg in transcription_segments if not seg.is_hallucination]
        
        if not valid_segments:
            return "No reliable speech transcription available (potential hallucinations filtered out)."
        
        formatted_lines = []
        current_speaker = None
        
        for segment in valid_segments:
            line_parts = []
            
            # Add speaker label if it changed or if first segment
            if include_speaker_labels and segment.speaker_label != current_speaker:
                current_speaker = segment.speaker_label
                formatted_lines.append(f"\n**{current_speaker}:**")
            
            if include_timestamps:
                start_min = int(segment.start_time // 60)
                start_sec = int(segment.start_time % 60)
                end_min = int(segment.end_time // 60)
                end_sec = int(segment.end_time % 60)
                timestamp = f"[{start_min:02d}:{start_sec:02d}-{end_min:02d}:{end_sec:02d}]"
                line_parts.append(timestamp)
            
            line_parts.append(segment.text)
            
            if include_confidence:
                confidence_info = f"(conf: {segment.confidence:.2f}"
                if segment.speaker_confidence is not None:
                    confidence_info += f", speaker: {segment.speaker_confidence:.2f}"
                confidence_info += ")"
                line_parts.append(confidence_info)
            
            formatted_lines.append("  " + " ".join(line_parts))
        
        return "\n".join(formatted_lines) 