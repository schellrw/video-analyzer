#!/usr/bin/env python3
"""
Violation Analysis Service
Analyzes raw analysis data to identify, timestamp, and categorize potential violations
without harsh keyword biases. It correlates frame and audio data.
"""

import logging
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)

class ViolationAnalysisService:
    """
    A service to perform an unbiased analysis of video and audio data,
    extracting key moments, violations, and generating a structured timeline.
    """

    def __init__(self):
        """Initialize the service."""
        # More nuanced event triggers with severity and category
        self.audio_event_triggers = {
            'Use of Force': [
                (r'\btaser\b|\btaze\b', {'severity': 'high', 'confidence': 0.9, 'description': 'Taser deployment threatened or initiated'}),
                (r'\b(dog|k-9).*(bite|fight|rip)\b', {'severity': 'high', 'confidence': 0.85, 'description': 'K-9 unit deployment threatened or initiated'}),
                (r'\bstop moving\b|\b(help me.?){2,}\b', {'severity': 'high', 'confidence': 0.75, 'description': 'Physical struggle and restraint of suspect'}),
            ],
            'Escalation': [
                (r'\bget out right now\b|\bget your hands up\b', {'severity': 'medium', 'confidence': 0.8, 'description': 'Officers issuing direct commands to suspect'}),
                (r'\blast warning\b|\blast chance\b', {'severity': 'medium', 'confidence': 0.88, 'description': 'Final warning issued before action'}),
            ]
        }
        logger.info("ViolationAnalysisService initialized")

    def analyze(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes raw analysis data to produce a more refined set of results
        for report generation.

        Args:
            analysis_data: The raw data from initial AI processing.

        Returns:
            The enhanced analysis data.
        """
        logger.info("Starting violation analysis...")

        # Get violations from visual frame analysis
        frame_violations = self._extract_violations_from_frames(analysis_data.get('frame_analyses', []))

        # Get violations from audio analysis
        audio_violations = self._extract_violations_from_audio(analysis_data.get('audio_analysis', {}))

        # Combine and de-duplicate violations
        all_violations = self._combine_and_deduplicate(frame_violations, audio_violations)

        # Build a clean timeline
        violation_timeline = sorted(all_violations, key=lambda x: x['timestamp'])

        # Update analysis data
        analysis_data['violations'] = violation_timeline
        analysis_data['violation_timeline'] = violation_timeline
        
        # Update summary based on new findings
        self._update_summary(analysis_data)
        
        logger.info(f"Violation analysis completed. Found {len(violation_timeline)} distinct violations.")
        
        return analysis_data

    def _extract_violations_from_frames(self, frame_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts and formats violations detected in video frames."""
        violations = []
        for frame in frame_analyses:
            if frame.get('concerns_detected') and frame.get('potential_violations'):
                for violation_text in frame.get('potential_violations'):
                    violations.append({
                        'timestamp': frame.get('timestamp', 0),
                        'timestamp_formatted': self._format_timestamp(frame.get('timestamp', 0)),
                        'type': violation_text.replace('_', ' ').title(),
                        'description': f"Visually detected concern: {violation_text}",
                        'severity': frame.get('severity_level', 'medium'),
                        'confidence': frame.get('confidence', 0.7),
                        'source': 'video',
                        'context': {'frame_number': frame.get('frame_number')}
                    })
        return violations

    def _extract_violations_from_audio(self, audio_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts violations from audio transcription using regex for more nuanced matching.
        """
        violations = []
        if not audio_analysis or 'transcription_segments' not in audio_analysis:
            return violations

        for segment in audio_analysis.get('transcription_segments', []):
            # Handle both object (dataclass) and dict style access safely
            if hasattr(segment, 'text') and hasattr(segment, 'start_time'):
                text = segment.text.lower()
                segment_start_time = segment.start_time
            elif isinstance(segment, dict):
                text = segment.get('text', '').lower()
                segment_start_time = segment.get('start_time', 0)
            else:
                logger.warning(f"Skipping unknown segment type in violation analysis: {type(segment)}")
                continue

            for category, triggers in self.audio_event_triggers.items():
                for pattern, details in triggers:
                    for match in re.finditer(pattern, text):
                        # Estimate timestamp based on word position
                        # This is an approximation but better than using segment start time for everything
                        start_char, _ = match.span()
                        words_before = len(text[:start_char].split())
                        estimated_time = segment_start_time + self._estimate_time_offset(words_before)
                        
                        violations.append({
                            'timestamp': estimated_time,
                            'timestamp_formatted': self._format_timestamp(estimated_time),
                            'type': details['description'].split(':')[0],
                            'description': details['description'],
                            'severity': details['severity'],
                            'confidence': details['confidence'],
                            'source': 'audio',
                            'audio_context': self._get_audio_context(text, match.group(0))
                        })
        return violations

    def _combine_and_deduplicate(self, frame_violations: List, audio_violations: List) -> List:
        """Combines and removes duplicate/similar violations."""
        combined = frame_violations + audio_violations
        if not combined:
            return []

        # Sort by timestamp to group time-based duplicates
        combined.sort(key=lambda x: x['timestamp'])
        
        deduplicated: List[Dict[str, Any]] = []
        last_violation: Optional[Dict[str, Any]] = None

        for current_violation in combined:
            if last_violation is not None:
                time_diff = abs(current_violation['timestamp'] - last_violation['timestamp'])
                # If same type and within 5 seconds, consider it a duplicate
                if current_violation['type'] == last_violation['type'] and time_diff < 5:
                    # Update confidence/severity if current is higher
                    if current_violation['confidence'] > last_violation['confidence']:
                        last_violation['confidence'] = current_violation['confidence']
                    continue  # Skip adding this duplicate
            
            deduplicated.append(current_violation)
            last_violation = current_violation

        return deduplicated

    def _update_summary(self, analysis_data: Dict[str, Any]):
        """Recalculates summary metrics based on the new violation analysis."""
        summary = analysis_data.get('summary', {})
        violations = analysis_data.get('violations', [])
        frame_analyses = analysis_data.get('frame_analyses', [])
        
        # Recalculate overall severity
        if any(v['severity'] == 'high' for v in violations):
            summary['severity_assessment'] = 'high'
        elif any(v['severity'] == 'medium' for v in violations):
            summary['severity_assessment'] = 'medium'
        else:
            summary['severity_assessment'] = 'low'
            
        summary['violations_detected'] = list(set([v['type'] for v in violations]))
        summary['concerns_found'] = len(violations) > 0
        
        # Ensure frame confidence stats are realistic
        if frame_analyses:
            confidences = [f.get('confidence', 0) for f in frame_analyses]
            if confidences:
                summary['average_confidence'] = sum(confidences) / len(confidences)
        
        analysis_data['summary'] = summary
        
    def _format_timestamp(self, seconds: float) -> str:
        """Formats seconds into MM:SS."""
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"

    def _estimate_time_offset(self, word_count: int, words_per_second: int = 3) -> float:
        """Estimates time offset within a segment based on word count."""
        return word_count / words_per_second

    def _get_audio_context(self, full_text: str, matched_phrase: str, window: int = 15) -> Dict:
        """Extracts a snippet of text around a matched phrase."""
        words = full_text.split()
        matched_words = matched_phrase.split()
        
        try:
            # Find where the matched phrase starts
            for i in range(len(words) - len(matched_words) + 1):
                if words[i:i+len(matched_words)] == matched_words:
                    start_index = i
                    break
            else:
                start_index = full_text.find(matched_phrase) // 5 # fallback
        except:
            return {'snippet': matched_phrase, 'full_segment': full_text[:200]}

        start = max(0, start_index - window)
        end = min(len(words), start_index + len(matched_words) + window)
        snippet = " ".join(words[start:end])
        
        return {
            'snippet': f"...{snippet}...",
            'matched_phrase': matched_phrase
        } 