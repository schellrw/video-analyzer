# violation_detector.py - Detect potential civil rights violations
from typing import List, Dict, Any
import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ViolationDetector:
    def __init__(self):
        # Expanded violation trigger matrix
        self.VIOLATION_TRIGGERS = {
            'visual': {
                'excessive_force': [
                    'knee_on_neck', 'multiple_officers_tackling', 'chokehold',
                    'excessive_restraint', 'weapon_pointed_at_compliant_subject',
                    'strike_to_head', 'taser_misuse', 'continued_force_after_compliance'
                ],
                'improper_restraint': [
                    'hogtie_position', 'prolonged_prone_restraint', 'pressure_on_back',
                    'restraint_asphyxia_position', 'handcuffs_too_tight'
                ],
                'procedural_violations': [
                    'search_without_consent', 'failure_to_identify', 'improper_arrest',
                    'destruction_of_property', 'failure_to_render_aid'
                ],
                'discrimination_indicators': [
                    'disparate_treatment', 'profiling_behavior', 'selective_enforcement'
                ]
            },
            'audio': {
                'verbal_abuse': [
                    'racial_slurs', 'ethnic_slurs', 'sexual_slurs', 'threats',
                    'derogatory_language', 'intimidation'
                ],
                'procedural_audio_violations': [
                    'failure_to_read_miranda', 'coerced_confession', 'denial_of_counsel',
                    'improper_interrogation'
                ],
                'medical_neglect': [
                    'ignored_medical_pleas', 'denial_of_medical_care', 'breathing_complaints_ignored'
                ],
                'escalation_language': [
                    'inflammatory_commands', 'contradictory_orders', 'provocative_language'
                ]
            },
            'temporal': {
                'escalation_patterns': [
                    'rapid_escalation', 'disproportionate_response', 'failure_to_deescalate'
                ],
                'response_timing': [
                    'delayed_medical_aid', 'prolonged_detention', 'excessive_restraint_duration'
                ],
                'procedural_timing': [
                    'rushed_procedures', 'insufficient_warning', 'premature_force'
                ]
            }
        }
        
        # Severity levels for different violations
        self.VIOLATION_SEVERITY = {
            'knee_on_neck': 'critical',
            'chokehold': 'critical',
            'racial_slurs': 'high',
            'excessive_restraint': 'high',
            'failure_to_render_aid': 'high',
            'improper_arrest': 'medium',
            'procedural_violations': 'medium',
            'verbal_abuse': 'medium'
        }
        
        # Legal frameworks and precedents
        self.LEGAL_FRAMEWORKS = {
            'section_1983': {
                'description': '42 U.S.C. § 1983 - Civil Rights Under Color of Law',
                'elements': [
                    'Acting under color of state law',
                    'Deprivation of constitutional rights',
                    'Causation between action and deprivation'
                ]
            },
            'fourth_amendment': {
                'description': 'Fourth Amendment - Unreasonable Search and Seizure',
                'violations': [
                    'excessive_force', 'unlawful_search', 'unlawful_seizure'
                ]
            },
            'fourteenth_amendment': {
                'description': 'Fourteenth Amendment - Equal Protection',
                'violations': [
                    'discriminatory_enforcement', 'selective_prosecution'
                ]
            }
        }
    
    def detect_violations(self, visual_analysis: List[Dict], transcript: Dict) -> Dict[str, Any]:
        """Main violation detection method"""
        try:
            violations = {
                'visual_violations': self._detect_visual_violations(visual_analysis),
                'audio_violations': self._detect_audio_violations(transcript),
                'temporal_violations': self._detect_temporal_violations(visual_analysis, transcript),
                'composite_violations': [],
                'severity_assessment': {},
                'legal_implications': {},
                'timeline': []
            }
            
            # Detect composite violations (combinations of visual/audio/temporal)
            violations['composite_violations'] = self._detect_composite_violations(
                violations['visual_violations'],
                violations['audio_violations'],
                violations['temporal_violations']
            )
            
            # Assess overall severity
            violations['severity_assessment'] = self._assess_overall_severity(violations)
            
            # Map to legal frameworks
            violations['legal_implications'] = self._map_to_legal_frameworks(violations)
            
            # Create violation timeline
            violations['timeline'] = self._create_violation_timeline(violations, visual_analysis, transcript)
            
            logger.info(f"Detected {len(violations['visual_violations']) + len(violations['audio_violations']) + len(violations['temporal_violations'])} potential violations")
            
            return violations
            
        except Exception as e:
            logger.error(f"Error detecting violations: {e}")
            raise
    
    def _detect_visual_violations(self, visual_analysis: List[Dict]) -> List[Dict]:
        """Detect violations from visual analysis"""
        violations = []
        
        try:
            for frame_analysis in visual_analysis:
                timestamp = frame_analysis['timestamp']
                
                # Check each analysis category
                for analysis_type in ['general_description', 'police_activity', 'violation_check']:
                    text = frame_analysis.get(analysis_type, '').lower()
                    
                    # Check for visual violation triggers
                    for category, triggers in self.VIOLATION_TRIGGERS['visual'].items():
                        for trigger in triggers:
                            if self._match_violation_pattern(text, trigger):
                                violations.append({
                                    'type': 'visual',
                                    'category': category,
                                    'trigger': trigger,
                                    'timestamp': timestamp,
                                    'frame_index': frame_analysis['frame_index'],
                                    'description': frame_analysis.get('violation_check', ''),
                                    'confidence': frame_analysis.get('scene_confidence', 0.5),
                                    'severity': self.VIOLATION_SEVERITY.get(trigger, 'medium'),
                                    'context': self._extract_visual_context(frame_analysis)
                                })
            
            return self._deduplicate_violations(violations)
            
        except Exception as e:
            logger.error(f"Error detecting visual violations: {e}")
            return []
    
    def _detect_audio_violations(self, transcript: Dict) -> List[Dict]:
        """Detect violations from audio transcript"""
        violations = []
        
        try:
            # Analyze full transcript text
            full_text = transcript.get('text', '')
            
            # Check each segment for violations
            for segment in transcript.get('segments', []):
                segment_text = segment['text'].lower()
                start_time = segment['start']
                end_time = segment['end']
                
                # Check for audio violation triggers
                for category, triggers in self.VIOLATION_TRIGGERS['audio'].items():
                    for trigger in triggers:
                        if self._match_violation_pattern(segment_text, trigger):
                            violations.append({
                                'type': 'audio',
                                'category': category,
                                'trigger': trigger,
                                'start_time': start_time,
                                'end_time': end_time,
                                'text': segment['text'],
                                'confidence': segment.get('confidence', 0.5),
                                'severity': self.VIOLATION_SEVERITY.get(trigger, 'medium'),
                                'context': self._extract_audio_context(transcript, start_time, end_time)
                            })
            
            return violations
            
        except Exception as e:
            logger.error(f"Error detecting audio violations: {e}")
            return []
    
    def _detect_temporal_violations(self, visual_analysis: List[Dict], transcript: Dict) -> List[Dict]:
        """Detect temporal pattern violations"""
        violations = []
        
        try:
            # Analyze escalation patterns
            escalation_violations = self._analyze_escalation_patterns(visual_analysis, transcript)
            violations.extend(escalation_violations)
            
            # Analyze response timing
            timing_violations = self._analyze_response_timing(visual_analysis, transcript)
            violations.extend(timing_violations)
            
            # Analyze procedural timing
            procedural_violations = self._analyze_procedural_timing(visual_analysis, transcript)
            violations.extend(procedural_violations)
            
            return violations
            
        except Exception as e:
            logger.error(f"Error detecting temporal violations: {e}")
            return []
    
    def _analyze_escalation_patterns(self, visual_analysis: List[Dict], transcript: Dict) -> List[Dict]:
        """Analyze force escalation patterns"""
        violations = []
        
        try:
            # Track force level over time
            force_timeline = []
            
            for frame in visual_analysis:
                force_level = self._assess_force_level(frame)
                force_timeline.append({
                    'timestamp': frame['timestamp'],
                    'force_level': force_level,
                    'description': frame.get('police_activity', '')
                })
            
            # Detect rapid escalation
            for i in range(1, len(force_timeline)):
                prev_force = force_timeline[i-1]['force_level']
                curr_force = force_timeline[i]['force_level']
                time_diff = force_timeline[i]['timestamp'] - force_timeline[i-1]['timestamp']
                
                # Flag rapid escalation (significant force increase in short time)
                if curr_force - prev_force >= 2 and time_diff < 5:  # 2+ levels in 5 seconds
                    violations.append({
                        'type': 'temporal',
                        'category': 'escalation_patterns',
                        'trigger': 'rapid_escalation',
                        'start_time': force_timeline[i-1]['timestamp'],
                        'end_time': force_timeline[i]['timestamp'],
                        'force_change': f"{prev_force} to {curr_force}",
                        'time_delta': time_diff,
                        'severity': 'high',
                        'description': f"Force escalated from level {prev_force} to {curr_force} in {time_diff:.1f} seconds"
                    })
            
            return violations
            
        except Exception as e:
            logger.error(f"Error analyzing escalation patterns: {e}")
            return []
    
    def _analyze_response_timing(self, visual_analysis: List[Dict], transcript: Dict) -> List[Dict]:
        """Analyze response timing violations"""
        violations = []
        
        try:
            # Look for medical aid requests and response
            medical_requests = []
            medical_responses = []
            
            # Find medical requests in transcript
            for segment in transcript.get('segments', []):
                text_lower = segment['text'].lower()
                if any(phrase in text_lower for phrase in ['can\'t breathe', 'help', 'medical', 'hurt', 'pain']):
                    medical_requests.append({
                        'timestamp': segment['start'],
                        'text': segment['text']
                    })
            
            # Find medical responses in visual analysis
            for frame in visual_analysis:
                description = frame.get('police_activity', '').lower()
                if any(phrase in description for phrase in ['medical', 'paramedic', 'ambulance', 'aid']):
                    medical_responses.append({
                        'timestamp': frame['timestamp'],
                        'description': frame.get('police_activity', '')
                    })
            
            # Check for delayed medical response
            for request in medical_requests:
                request_time = request['timestamp']
                response_times = [r['timestamp'] for r in medical_responses if r['timestamp'] > request_time]
                
                if not response_times:
                    # No medical response found
                    violations.append({
                        'type': 'temporal',
                        'category': 'response_timing',
                        'trigger': 'delayed_medical_aid',
                        'timestamp': request_time,
                        'severity': 'critical',
                        'description': f"Medical aid requested at {request_time:.1f}s but no response detected",
                        'request_text': request['text']
                    })
                else:
                    response_time = min(response_times)
                    delay = response_time - request_time
                    
                    if delay > 120:  # More than 2 minutes delay
                        violations.append({
                            'type': 'temporal',
                            'category': 'response_timing',
                            'trigger': 'delayed_medical_aid',
                            'request_time': request_time,
                            'response_time': response_time,
                            'delay': delay,
                            'severity': 'high' if delay > 300 else 'medium',
                            'description': f"Medical aid requested at {request_time:.1f}s, response at {response_time:.1f}s (delay: {delay:.1f}s)"
                        })
            
            return violations
            
        except Exception as e:
            logger.error(f"Error analyzing response timing: {e}")
            return []
    
    def _analyze_procedural_timing(self, visual_analysis: List[Dict], transcript: Dict) -> List[Dict]:
        """Analyze procedural timing violations"""
        violations = []
        
        try:
            # Look for Miranda rights timing
            arrest_time = None
            miranda_time = None
            
            # Find arrest indicators
            for frame in visual_analysis:
                description = frame.get('police_activity', '').lower()
                if any(phrase in description for phrase in ['handcuff', 'arrest', 'custody']):
                    if arrest_time is None:
                        arrest_time = frame['timestamp']
                    break
            
            # Find Miranda rights reading
            for segment in transcript.get('segments', []):
                text_lower = segment['text'].lower()
                if 'right to remain silent' in text_lower or 'miranda' in text_lower:
                    miranda_time = segment['start']
                    break
            
            # Check Miranda timing
            if arrest_time and not miranda_time:
                violations.append({
                    'type': 'temporal',
                    'category': 'procedural_timing',
                    'trigger': 'failure_to_read_miranda',
                    'arrest_time': arrest_time,
                    'severity': 'medium',
                    'description': f"Arrest occurred at {arrest_time:.1f}s but no Miranda rights detected"
                })
            elif arrest_time and miranda_time and miranda_time - arrest_time > 300:  # 5 minutes
                violations.append({
                    'type': 'temporal',
                    'category': 'procedural_timing',
                    'trigger': 'delayed_miranda_rights',
                    'arrest_time': arrest_time,
                    'miranda_time': miranda_time,
                    'delay': miranda_time - arrest_time,
                    'severity': 'medium',
                    'description': f"Miranda rights read {miranda_time - arrest_time:.1f}s after arrest"
                })
            
            return violations
            
        except Exception as e:
            logger.error(f"Error analyzing procedural timing: {e}")
            return []
    
    def _match_violation_pattern(self, text: str, trigger: str) -> bool:
        """Match violation patterns in text"""
        # Simple keyword matching - in production, use more sophisticated NLP
        trigger_patterns = {
            'knee_on_neck': ['knee.*neck', 'kneeling.*neck', 'pressure.*neck'],
            'racial_slurs': ['racial.*slur', 'discriminatory.*language'],
            'excessive_force': ['excessive.*force', 'brutal', 'violence'],
            'can\'t_breathe': ['can\'t breathe', 'cannot breathe', 'help.*breathe']
        }
        
        patterns = trigger_patterns.get(trigger, [trigger.replace('_', '.*')])
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _assess_force_level(self, frame_analysis: Dict) -> int:
        """Assess force level from frame analysis (0-5 scale)"""
        description = frame_analysis.get('police_activity', '').lower()
        
        force_indicators = {
            5: ['deadly force', 'weapon fired', 'shot', 'gun'],
            4: ['taser', 'baton', 'pepper spray', 'strike'],
            3: ['tackle', 'takedown', 'restraint', 'force'],
            2: ['grab', 'push', 'control', 'handcuff'],
            1: ['verbal command', 'instruction