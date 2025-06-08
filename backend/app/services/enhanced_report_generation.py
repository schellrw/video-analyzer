"""
Enhanced Report Generation Service
Improved version with better violation analysis, transcript integration, and executive summaries.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import base64
import io

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, red, orange, green
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib import colors

logger = logging.getLogger(__name__)


class EnhancedReportGenerationService:
    """Enhanced service for generating comprehensive PDF reports with improved violation analysis."""
    
    def __init__(self):
        """Initialize the enhanced report generation service."""
        self.styles = getSampleStyleSheet()
        
        # Enhanced color scheme (must be defined before _setup_custom_styles)
        self.colors = {
            'primary': HexColor('#1f2937'),      # Dark gray
            'secondary': HexColor('#374151'),     # Medium gray
            'accent': HexColor('#3b82f6'),       # Blue
            'success': HexColor('#10b981'),      # Green
            'warning': HexColor('#f59e0b'),      # Orange
            'danger': HexColor('#ef4444'),       # Red
            'light_gray': HexColor('#f3f4f6'),   # Light gray
            'border': HexColor('#d1d5db'),       # Border gray
            'critical': HexColor('#dc2626'),     # Critical red
            'high': HexColor('#ea580c'),         # High orange
            'medium': HexColor('#ca8a04'),       # Medium yellow
            'low': HexColor('#16a34a')           # Low green
        }
        
        # Now setup custom styles (after colors are defined)
        self._setup_custom_styles()
        
        # Violation severity mapping
        self.violation_priorities = {
            'excessive force': {'severity': 10, 'category': 'Use of Force'},
            'constitutional violation': {'severity': 9, 'category': 'Civil Rights'},
            'improper procedure': {'severity': 7, 'category': 'Procedural'},
            'weapon misuse': {'severity': 8, 'category': 'Use of Force'},
            'verbal abuse': {'severity': 6, 'category': 'Conduct'},
            'search seizure': {'severity': 8, 'category': 'Constitutional'},
            'discrimination': {'severity': 7, 'category': 'Civil Rights'},
            'unprofessional conduct': {'severity': 5, 'category': 'Conduct'}
        }
        
        logger.info("EnhancedReportGenerationService initialized")
    
    def _setup_custom_styles(self):
        """Setup enhanced custom paragraph styles."""
        # Enhanced title style
        self.styles.add(ParagraphStyle(
            name='EnhancedTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        # Critical violation alert style
        self.styles.add(ParagraphStyle(
            name='CriticalViolation',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            textColor=white,
            fontName='Helvetica-Bold',
            backColor=self.colors['critical'],
            borderColor=self.colors['critical'],
            borderWidth=2,
            borderPadding=12,
            alignment=TA_CENTER
        ))
        
        # High priority violation style
        self.styles.add(ParagraphStyle(
            name='HighPriorityViolation',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            textColor=self.colors['critical'],
            fontName='Helvetica-Bold',
            backColor=HexColor('#fef2f2'),
            borderColor=self.colors['critical'],
            borderWidth=1,
            borderPadding=8
        ))
        
        # Medium priority violation style
        self.styles.add(ParagraphStyle(
            name='MediumPriorityViolation',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            textColor=self.colors['warning'],
            fontName='Helvetica-Bold',
            backColor=HexColor('#fffbeb'),
            borderColor=self.colors['warning'],
            borderWidth=1,
            borderPadding=8
        ))
        
        # Transcript style
        self.styles.add(ParagraphStyle(
            name='TranscriptText',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Courier',
            textColor=HexColor('#374151'),
            spaceAfter=6,
            leftIndent=12
        ))
        
        # Executive summary style
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica',
            textColor=HexColor('#1f2937'),
            spaceAfter=8,
            alignment=TA_JUSTIFY
        ))
    
    def generate_enhanced_comprehensive_report(self, analysis_results: Dict[str, Any], 
                                             case_info: Dict[str, Any] = None,
                                             output_path: str = None) -> str:
        """
        Generate an enhanced comprehensive PDF report with improved violation analysis.
        """
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                case_id = case_info.get('case_id', 'unknown') if case_info else 'unknown'
                output_path = f"reports/enhanced_analysis_report_{case_id}_{timestamp}.pdf"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            story = []
            
            # Enhanced title page
            story.extend(self._build_enhanced_title_page(analysis_results, case_info))
            story.append(PageBreak())
            
            # Enhanced executive summary (focused on likely violations)
            story.extend(self._build_enhanced_executive_summary(analysis_results))
            story.append(PageBreak())
            
            # Priority violation analysis
            story.extend(self._build_priority_violation_analysis(analysis_results))
            story.append(PageBreak())
            
            # Audio transcript with pertinent snippets
            story.extend(self._build_audio_transcript_analysis(analysis_results))
            story.append(PageBreak())
            
            # Comprehensive frame analysis
            story.extend(self._build_comprehensive_frame_analysis(analysis_results))
            story.append(PageBreak())
            
            # Enhanced recommendations
            story.extend(self._build_enhanced_recommendations(analysis_results))
            story.append(PageBreak())
            
            # Full transcript appendix
            story.extend(self._build_full_transcript_appendix(analysis_results))
            
            doc.build(story)
            
            logger.info(f"Enhanced report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating enhanced report: {str(e)}")
            raise
    
    def _build_enhanced_executive_summary(self, analysis_results: Dict[str, Any]) -> List:
        """Build enhanced executive summary focusing on most likely violations."""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['Heading1']))
        elements.append(Spacer(1, 12))
        
        # Get summary data
        summary = analysis_results.get('summary', {})
        violations = analysis_results.get('violations', [])
        violations_detected = summary.get('violations_detected', [])
        total_frames = analysis_results.get('total_frames_analyzed', 0)
        
        # Confidence analysis - show variation
        frame_analyses = analysis_results.get('frame_analyses', [])
        if frame_analyses:
            confidences = [f.get('confidence', 0) for f in frame_analyses]
            min_conf = min(confidences) if confidences else 0
            max_conf = max(confidences) if confidences else 0
            avg_conf = sum(confidences) / len(confidences) if confidences else 0
            
            # Detect if all confidences are the same (potential issue)
            unique_confidences = len(set(round(c, 2) for c in confidences))
            
            confidence_text = f"""
            Analysis Confidence Range: {min_conf:.1%} - {max_conf:.1%} (Average: {avg_conf:.1%})
            Confidence Variation: {unique_confidences} distinct confidence levels across {len(confidences)} frames
            """
            
            if unique_confidences <= 2:
                confidence_text += "\n⚠️ Note: Limited confidence variation detected - manual review recommended"
        else:
            confidence_text = "Confidence analysis not available"
        
        elements.append(Paragraph("Analysis Quality Assessment:", self.styles['Heading2']))
        elements.append(Paragraph(confidence_text, self.styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Prioritize violations over general concerns to reduce overlap
        high_priority_violations = [v for v in violations if v.get('priority_score', 0) > 0.8]
        
        # Overall assessment
        overall_severity = analysis_results.get('severity_assessment', 'low').upper()
        concerns_found = analysis_results.get('concerns_found', False)
        
        if high_priority_violations:
            status_text = f"🚨 HIGH PRIORITY: {len(high_priority_violations)} significant violations identified"
            elements.append(Paragraph(status_text, self.styles['CriticalViolation']))
        elif violations:
            status_text = f"⚠️ CONCERNS DETECTED: {len(violations)} potential issues identified"
            elements.append(Paragraph(status_text, self.styles['HighPriorityViolation']))
        elif concerns_found:
            status_text = f"ℹ️ REVIEW RECOMMENDED: General concerns detected in {summary.get('total_concerning_frames', 0)} frames"
            elements.append(Paragraph(status_text, self.styles['MediumPriorityViolation']))
        else:
            status_text = "✅ NO SIGNIFICANT VIOLATIONS: Analysis indicates appropriate conduct"
            elements.append(Paragraph(status_text, self.styles['Normal']))
        
        elements.append(Spacer(1, 12))
        
        # Frame sampling methodology explanation
        extraction_strategy = analysis_results.get('extraction_strategy', 'unknown')
        sampling_text = f"""
        Frame Selection Method: {extraction_strategy.title()} sampling
        Frames Analyzed: {total_frames} from video
        Coverage: Distributed across non-blackout segments with motion-based prioritization
        """
        elements.append(Paragraph("Sampling Methodology:", self.styles['Heading2']))
        elements.append(Paragraph(sampling_text, self.styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Top violations or concerning findings (reduce redundancy)
        if violations:
            elements.append(Paragraph("Primary Concerns Identified:", self.styles['Heading2']))
            elements.append(Spacer(1, 8))
            
            # Group violations by type to avoid duplication
            violation_types = {}
            for violation in violations[:5]:  # Top 5 violations
                v_type = violation.get('type', 'unknown')
                if v_type not in violation_types:
                    violation_types[v_type] = []
                violation_types[v_type].append(violation)
            
            for i, (v_type, v_list) in enumerate(violation_types.items(), 1):
                primary_violation = v_list[0]  # Use the highest priority one
                additional_count = len(v_list) - 1
                
                violation_text = self._format_violation_for_executive_summary(primary_violation, i)
                if additional_count > 0:
                    violation_text += f" (+{additional_count} similar instances)"
                    
                elements.append(Paragraph(violation_text, self.styles['HighPriorityViolation']))
                elements.append(Spacer(1, 8))
        
        # Quick statistics with better context
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Analysis Overview:", self.styles['Heading2']))
        
        stats_data = [
            ['Overall Severity Level', overall_severity],
            ['Average Analysis Confidence', f"{summary.get('average_confidence', 0):.1%}"],
            ['Frames with Detected Concerns', f"{summary.get('total_concerning_frames', 0)}/{total_frames}"],
            ['Unique Violation Types', str(len(violations_detected))],
            ['Primary Concerns Found', 'YES' if concerns_found else 'NO']
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['light_gray']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        
        elements.append(stats_table)
        
        return elements
    
    def _filter_high_priority_violations(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and sort violations by priority score and severity."""
        if not violations:
            return []
        
        # Calculate priority scores
        for violation in violations:
            base_priority = 5  # Default priority
            violation_type = violation.get('type', '').lower()
            
            if violation_type in self.violation_priorities:
                base_priority = self.violation_priorities[violation_type]['severity']
            
            confidence = violation.get('confidence', 0.5)
            priority_score = base_priority * confidence * violation.get('priority_score', 1.0)
            violation['calculated_priority'] = priority_score
        
        # Sort by calculated priority (highest first)
        sorted_violations = sorted(violations, key=lambda x: x.get('calculated_priority', 0), reverse=True)
        
        # Return top violations with priority score > 5.0
        return [v for v in sorted_violations if v.get('calculated_priority', 0) > 5.0]
    
    def _format_violation_for_executive_summary(self, violation: Dict[str, Any], index: int) -> str:
        """Format a violation for the executive summary."""
        timestamp = violation.get('timestamp_formatted', 'Unknown time')
        violation_type = violation.get('type', 'Unknown violation').title()
        confidence = violation.get('confidence', 0)
        description = violation.get('description', 'No description available')
        
        # Truncate description for executive summary
        if len(description) > 150:
            description = description[:150] + "..."
        
        formatted_text = f"""
        <b>{index}. {violation_type}</b> at {timestamp} (Confidence: {confidence:.1%})<br/>
        {description}
        """
        
        return formatted_text
    
    def _get_pertinent_audio_snippet(self, violation: Dict[str, Any], 
                                   analysis_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get relevant audio snippet for a violation."""
        audio_context = violation.get('audio_context')
        if not audio_context:
            return None
        
        closest_segment = audio_context.get('closest_segment')
        if closest_segment and abs(closest_segment.get('time_offset', 0)) < 10:
            return closest_segment
        
        return None
    
    def _build_priority_violation_analysis(self, analysis_results: Dict[str, Any]) -> List:
        """Build detailed analysis of priority violations."""
        elements = []
        
        elements.append(Paragraph("PRIORITY VIOLATION ANALYSIS", self.styles['Heading1']))
        elements.append(Spacer(1, 12))
        
        # Get violations from the actual data structure
        violations_detected = analysis_results.get('violations_detected', [])
        violation_timeline = analysis_results.get('violation_timeline', [])
        
        if not violation_timeline and not violations_detected:
            elements.append(Paragraph(
                "No violations detected in the analyzed timeframe. See comprehensive analysis for all observations.",
                self.styles['Normal']
            ))
            return elements
        
        # Show violation timeline if available
        if violation_timeline:
            elements.append(Paragraph("Detected Violations Timeline:", self.styles['Heading2']))
            elements.append(Spacer(1, 8))
            
            for timeline_item in violation_timeline:
                elements.extend(self._format_timeline_violation(timeline_item))
                elements.append(Spacer(1, 12))
        
        # Show general violations detected
        if violations_detected:
            elements.append(Paragraph("Additional Violations Detected:", self.styles['Heading2']))
            elements.append(Spacer(1, 8))
            
            for violation_type in violations_detected:
                elements.append(Paragraph(f"• {violation_type.title()}", self.styles['HighPriorityViolation']))
                elements.append(Spacer(1, 6))
        
        return elements
    
    def _format_timeline_violation(self, timeline_item: Dict[str, Any]) -> List:
        """Format a timeline violation entry."""
        elements = []
        
        # Violation header
        timestamp = timeline_item.get('timestamp_formatted', 'Unknown')
        violations = timeline_item.get('violations', [])
        confidence = timeline_item.get('confidence', 0)
        severity = timeline_item.get('severity', 'low')
        
        header_text = f"<b>{', '.join(violations).title()}</b> - {timestamp} (Confidence: {confidence:.1%}, Severity: {severity.upper()})"
        elements.append(Paragraph(header_text, self.styles['Heading3']))
        elements.append(Spacer(1, 6))
        
        # Description
        description = timeline_item.get('description', 'No description available')
        elements.append(Paragraph(description, self.styles['Normal']))
        elements.append(Spacer(1, 6))
        
        return elements
    
    def _build_audio_transcript_analysis(self, analysis_results: Dict[str, Any]) -> List:
        """Build audio transcript analysis with pertinent snippets highlighted and speaker identification."""
        elements = []
        
        elements.append(Paragraph("AUDIO TRANSCRIPT ANALYSIS", self.styles['Heading1']))
        elements.append(Spacer(1, 12))
        
        # Check for enhanced audio analysis with speaker diarization
        audio_analysis = analysis_results.get('audio_analysis', {})
        speaker_summary = analysis_results.get('speaker_summary', {})
        
        if not audio_analysis:
            elements.append(Paragraph(
                "No audio analysis data available in this report.",
                self.styles['Normal']
            ))
            return elements
        
        # Audio overview
        elements.append(Paragraph("Audio Analysis Overview:", self.styles['Heading2']))
        
        speech_duration = audio_analysis.get('total_speech_duration', 0)
        total_duration = analysis_results.get('video_info', {}).get('duration', 0)
        speech_percentage = (speech_duration / total_duration * 100) if total_duration > 0 else 0
        
        overview_text = f"""
        Total Speech Duration: {speech_duration:.1f} seconds ({speech_percentage:.1f}% of video)
        Audio Quality Score: {audio_analysis.get('audio_quality_score', 0):.2f}/1.0
        Valid Transcription Segments: {audio_analysis.get('valid_transcription_segments', 0)}
        Average Confidence: {audio_analysis.get('average_confidence', 0):.1%}
        """
        
        elements.append(Paragraph(overview_text, self.styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Speaker identification summary
        if speaker_summary.get('has_speaker_diarization', False):
            elements.append(Paragraph("Speaker Identification:", self.styles['Heading2']))
            
            total_speakers = speaker_summary.get('total_speakers_identified', 0)
            identified_speakers = speaker_summary.get('identified_speakers', {})
            speaker_percentages = speaker_summary.get('speaker_talk_percentage', {})
            
            speaker_text = f"Identified {total_speakers} distinct speakers in the recording:\n\n"
            
            for speaker_id, speaker_label in identified_speakers.items():
                percentage = speaker_percentages.get(speaker_label, 0)
                speaker_text += f"• {speaker_label}: {percentage:.1f}% of speech time\n"
            
            if speaker_summary.get('most_active_speaker'):
                speaker_text += f"\nMost active speaker: {speaker_summary['most_active_speaker']}"
            
            elements.append(Paragraph(speaker_text, self.styles['Normal']))
            elements.append(Spacer(1, 12))
        
        # Get transcription segments
        segments = audio_analysis.get('transcription_segments', [])
        
        if not segments:
            elements.append(Paragraph(
                "No transcription segments available.",
                self.styles['Normal']
            ))
            return elements
        
        # Show key segments with speaker identification if available
        elements.append(Paragraph("Key Audio Segments:", self.styles['Heading2']))
        elements.append(Spacer(1, 8))
        
        # Check if segments have speaker information (enhanced transcription)
        has_speaker_info = any(
            hasattr(seg, 'speaker_label') or (isinstance(seg, dict) and 'speaker_label' in seg)
            for seg in segments[:5]
        )
        
        for i, segment in enumerate(segments[:10], 1):  # Show first 10 segments
            if hasattr(segment, 'start_time'):
                # Enhanced transcription segment
                start_time = segment.start_time
                end_time = segment.end_time
                text = segment.text
                confidence = segment.confidence
                speaker_label = getattr(segment, 'speaker_label', 'Unknown Speaker')
                is_hallucination = getattr(segment, 'is_hallucination', False)
            else:
                # Regular transcription segment (dict format)
                start_time = segment.get('start_time', 0)
                end_time = segment.get('end_time', 0)
                text = segment.get('text', '')
                confidence = segment.get('confidence', 0)
                speaker_label = segment.get('speaker_label', 'Unknown Speaker')
                is_hallucination = segment.get('is_hallucination', False)
            
            # Skip hallucinations
            if is_hallucination:
                continue
            
            # Format segment with speaker identification
            if has_speaker_info and speaker_label != 'Unknown Speaker':
                segment_text = f"""
                <b>[{start_time:.1f}s - {end_time:.1f}s] {speaker_label}</b><br/>
                (Confidence: {confidence:.1%})<br/>
                "{text}"
                """
            else:
                segment_text = f"""
                <b>[{start_time:.1f}s - {end_time:.1f}s]</b> 
                (Confidence: {confidence:.1%})<br/>
                "{text}"
                """
            
            elements.append(Paragraph(segment_text, self.styles['TranscriptText']))
            elements.append(Spacer(1, 8))
        
        if len(segments) > 10:
            elements.append(Paragraph(
                f"... and {len(segments) - 10} additional segments. See full transcript in appendix.",
                self.styles['Normal']
            ))
        
        return elements
    
    def _build_comprehensive_frame_analysis(self, analysis_results: Dict[str, Any]) -> List:
        """Build comprehensive analysis of all frames."""
        elements = []
        
        elements.append(Paragraph("COMPREHENSIVE FRAME ANALYSIS", self.styles['Heading1']))
        elements.append(Spacer(1, 12))
        
        frame_analyses = analysis_results.get('frame_analyses', [])
        
        elements.append(Paragraph(
            f"This section provides analysis for all {len(frame_analyses)} frames examined. "
            "Frames are organized by significance and potential concerns.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 12))
        
        # Group frames by concern level
        concerning_frames = [f for f in frame_analyses if f.get('concerns_detected', False)]
        neutral_frames = [f for f in frame_analyses if not f.get('concerns_detected', False)]
        
        # Show concerning frames first
        if concerning_frames:
            elements.append(Paragraph("Frames with Detected Concerns:", self.styles['Heading2']))
            elements.append(Spacer(1, 8))
            
            for frame in concerning_frames:
                elements.extend(self._format_frame_analysis(frame, detailed=True))
                elements.append(Spacer(1, 8))
        
        # Summary of neutral frames
        if neutral_frames:
            elements.append(Paragraph("Neutral Frames Summary:", self.styles['Heading2']))
            elements.append(Spacer(1, 8))
            
            neutral_text = f"""
            {len(neutral_frames)} frames showed no significant concerns. These frames 
            primarily contained routine interactions or environmental footage without 
            detected violations or concerning behavior.
            """
            elements.append(Paragraph(neutral_text, self.styles['Normal']))
        
        return elements
    
    def _format_frame_analysis(self, frame: Dict[str, Any], detailed: bool = False) -> List:
        """Format individual frame analysis."""
        elements = []
        
        frame_num = frame.get('frame_number', 'N/A')
        timestamp = frame.get('timestamp_formatted', 'N/A')
        confidence = frame.get('confidence', 0)
        
        header = f"Frame {frame_num} - {timestamp} (Confidence: {confidence:.1%})"
        elements.append(Paragraph(header, self.styles['Heading3']))
        elements.append(Spacer(1, 4))
        
        # Analysis text
        analysis = frame.get('analysis_text', 'No analysis available')
        elements.append(Paragraph(analysis, self.styles['Normal']))
        
        if detailed:
            # Additional details for concerning frames
            violations = frame.get('potential_violations', [])
            if violations:
                elements.append(Spacer(1, 4))
                violations_text = f"<b>Detected Issues:</b> {', '.join(violations)}"
                elements.append(Paragraph(violations_text, self.styles['HighPriorityViolation']))
        
        return elements
    
    def _build_enhanced_recommendations(self, analysis_results: Dict[str, Any]) -> List:
        """Build enhanced recommendations based on analysis."""
        elements = []
        
        elements.append(Paragraph("ENHANCED RECOMMENDATIONS", self.styles['Heading1']))
        elements.append(Spacer(1, 12))
        
        violations = analysis_results.get('violations', [])
        high_priority_violations = self._filter_high_priority_violations(violations)
        
        # Priority recommendations based on violations found
        if high_priority_violations:
            elements.append(Paragraph("Immediate Actions Required:", self.styles['Heading2']))
            elements.append(Spacer(1, 8))
            
            immediate_actions = [
                "Conduct immediate internal investigation of flagged incidents",
                "Interview all officers and civilians involved in high-priority violations",
                "Preserve all evidence including additional video angles and witness statements",
                "Consider suspension pending investigation for officers involved in critical violations",
                "Notify legal counsel and prepare for potential civil rights litigation"
            ]
            
            for action in immediate_actions:
                elements.append(Paragraph(f"• {action}", self.styles['Normal']))
            
            elements.append(Spacer(1, 12))
        
        # Standard recommendations
        standard_recs = analysis_results.get('recommendations', [])
        if standard_recs:
            elements.append(Paragraph("Additional Recommendations:", self.styles['Heading2']))
            elements.append(Spacer(1, 8))
            
            for rec in standard_recs:
                elements.append(Paragraph(f"• {rec}", self.styles['Normal']))
        
        return elements
    
    def _build_full_transcript_appendix(self, analysis_results: Dict[str, Any]) -> List:
        """Build full transcript appendix with speaker identification."""
        elements = []
        
        elements.append(Paragraph("APPENDIX: FULL AUDIO TRANSCRIPT", self.styles['Heading1']))
        elements.append(Spacer(1, 12))
        
        # Check for audio analysis
        audio_analysis = analysis_results.get('audio_analysis', {})
        speaker_summary = analysis_results.get('speaker_summary', {})
        
        if not audio_analysis:
            elements.append(Paragraph(
                "No audio transcript available for this analysis.",
                self.styles['Normal']
            ))
            return elements
        
        # Get transcription segments
        segments = audio_analysis.get('transcription_segments', [])
        
        if not segments:
            elements.append(Paragraph(
                "No transcription segments were generated for this video.",
                self.styles['Normal']
            ))
            return elements
        
        # Transcript header with speaker information
        if speaker_summary.get('has_speaker_diarization', False):
            elements.append(Paragraph(
                "This transcript includes speaker identification. Speakers have been automatically "
                "identified based on audio characteristics and speech patterns. Speaker labels "
                "are provided as follows:",
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 8))
            
            # List identified speakers
            identified_speakers = speaker_summary.get('identified_speakers', {})
            if identified_speakers:
                speaker_legend = "Speaker Legend:\n"
                for speaker_id, speaker_label in identified_speakers.items():
                    speaker_legend += f"• {speaker_label}\n"
                
                elements.append(Paragraph(speaker_legend, self.styles['Normal']))
                elements.append(Spacer(1, 12))
        else:
            elements.append(Paragraph(
                "This transcript does not include speaker identification. All speech is presented "
                "in chronological order without speaker labels.",
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 12))
        
        # Format full transcript with speaker labels
        elements.append(Paragraph("Complete Transcript:", self.styles['Heading2']))
        elements.append(Spacer(1, 8))
        
        # Check if segments have speaker information
        has_speaker_info = any(
            hasattr(seg, 'speaker_label') or (isinstance(seg, dict) and 'speaker_label' in seg)
            for seg in segments
        )
        
        current_speaker = None
        valid_segment_count = 0
        
        for segment in segments:
            # Extract segment information
            if hasattr(segment, 'start_time'):
                # Enhanced transcription segment
                start_time = segment.start_time
                end_time = segment.end_time
                text = segment.text.strip()
                confidence = segment.confidence
                speaker_label = getattr(segment, 'speaker_label', 'Unknown Speaker')
                is_hallucination = getattr(segment, 'is_hallucination', False)
            else:
                # Regular transcription segment (dict format)
                start_time = segment.get('start_time', 0)
                end_time = segment.get('end_time', 0)
                text = segment.get('text', '').strip()
                confidence = segment.get('confidence', 0)
                speaker_label = segment.get('speaker_label', 'Unknown Speaker')
                is_hallucination = segment.get('is_hallucination', False)
            
            # Skip hallucinations and empty text
            if is_hallucination or not text:
                continue
            
            valid_segment_count += 1
            
            # Format timestamp
            start_min = int(start_time // 60)
            start_sec = int(start_time % 60)
            timestamp = f"[{start_min:02d}:{start_sec:02d}]"
            
            # Add speaker header if speaker changed or first valid segment
            if has_speaker_info and speaker_label != current_speaker:
                current_speaker = speaker_label
                elements.append(Spacer(1, 8))
                elements.append(Paragraph(f"**{current_speaker}:**", self.styles['Heading3']))
            
            # Format transcript line with timestamp and confidence if low
            transcript_line = f"{timestamp} {text}"
            
            # Add confidence warning for low-confidence segments
            if confidence < 0.4:
                transcript_line += f" <i>(Low confidence: {confidence:.1%})</i>"
            
            elements.append(Paragraph(transcript_line, self.styles['TranscriptText']))
        
        # Summary
        elements.append(Spacer(1, 16))
        elements.append(Paragraph(
            f"End of transcript. Total valid segments: {valid_segment_count}",
            self.styles['Normal']
        ))
        
        # Add note about filtered content
        total_segments = len(segments)
        filtered_count = total_segments - valid_segment_count
        if filtered_count > 0:
            elements.append(Paragraph(
                f"Note: {filtered_count} segments were filtered out as potential hallucinations or empty content.",
                self.styles['Normal']
            ))
        
        return elements
    
    def generate_enhanced_summary_report(self, analysis_results: Dict[str, Any], 
                                       output_path: str = None) -> str:
        """Generate enhanced executive summary report."""
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"reports/enhanced_summary_{timestamp}.pdf"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            
            # Enhanced executive summary only
            story.extend(self._build_enhanced_executive_summary(analysis_results))
            story.append(Spacer(1, 20))
            
            # Priority violations only
            story.extend(self._build_priority_violation_analysis(analysis_results))
            
            doc.build(story)
            
            logger.info(f"Enhanced summary report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating enhanced summary: {str(e)}")
            raise
    
    def _build_enhanced_title_page(self, analysis_results: Dict[str, Any], 
                                 case_info: Dict[str, Any] = None) -> List:
        """Build enhanced title page for the report."""
        elements = []
        
        # Main title
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(
            "ENHANCED VIDEO ANALYSIS REPORT",
            self.styles['EnhancedTitle']
        ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Case information
        if case_info:
            case_table_data = [
                ['Case ID:', case_info.get('case_id', 'N/A')],
                ['Case Title:', case_info.get('title', 'N/A')],
                ['Date of Incident:', case_info.get('incident_date', 'N/A')],
                ['Location:', case_info.get('location', 'N/A')],
                ['Reporting Officer:', case_info.get('reporting_officer', 'N/A')]
            ]
        else:
            case_table_data = [
                ['Video File:', analysis_results.get('video_path', 'N/A')],
                ['Analysis Date:', analysis_results.get('analysis_timestamp', datetime.now().strftime('%Y-%m-%d'))],
                ['Total Frames Analyzed:', str(analysis_results.get('total_frames_analyzed', 0))],
                ['Processing Time:', f"{analysis_results.get('processing_time', 0):.2f} seconds"]
            ]
        
        case_table = Table(case_table_data, colWidths=[2*inch, 4*inch])
        case_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(case_table)
        elements.append(Spacer(1, 1*inch))
        
        # Analysis summary box
        summary = analysis_results.get('summary', {})
        severity = analysis_results.get('severity_assessment', 'low').upper()
        concerns_found = analysis_results.get('concerns_found', False)
        
        summary_data = [
            ['ENHANCED ANALYSIS SUMMARY'],
            [f"Severity Level: {severity}"],
            [f"Concerns Detected: {'YES' if concerns_found else 'NO'}"],
            [f"Overall Confidence: {summary.get('average_confidence', 0):.1%}"],
            [f"Violations Found: {len(analysis_results.get('violations_detected', []))}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[6*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors['light_gray']),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 1*inch))
        
        # Legal disclaimer
        disclaimer_text = """
        <b>ENHANCED ANALYSIS DISCLAIMER:</b> This report is generated using advanced AI 
        analysis and should be used as a supplementary tool for investigation purposes only. 
        All findings should be verified through manual review and additional investigation. 
        This analysis does not constitute legal advice or definitive evidence.
        """
        
        elements.append(Paragraph(disclaimer_text, self.styles['Normal']))
        
        return elements 