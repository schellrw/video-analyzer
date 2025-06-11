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
import textwrap

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
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            story = []

            # Pre-calculate primary concerns so it's consistent everywhere
            violations = analysis_results.get('violations', [])
            primary_concerns = self._get_primary_concerns(violations)
            
            # Enhanced title page
            story.extend(self._build_enhanced_title_page(analysis_results, case_info))
            story.append(PageBreak())
            
            # Enhanced executive summary
            story.extend(self._build_enhanced_executive_summary(analysis_results, primary_concerns))
            story.append(PageBreak())
            
            # Primary concerns and timeline
            story.extend(self._build_primary_concerns_section(analysis_results, primary_concerns))
            story.append(PageBreak())
            
            # Detected Violations Timeline is now part of the above section
            
            # Key Audio Segments Analysis
            story.extend(self._build_key_audio_segments(analysis_results))
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
    
    def _build_enhanced_executive_summary(self, analysis_results: Dict[str, Any], primary_concerns: List[Dict[str, Any]]) -> List:
        """Build enhanced executive summary using pre-calculated primary concerns."""
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
    
    def _build_primary_concerns_section(self, analysis_results: Dict[str, Any], primary_concerns: List[Dict[str, Any]]) -> List:
        """Builds the primary concerns and violation timeline section."""
        elements = []
        elements.append(Paragraph("PRIMARY CONCERNS AND VIOLATION TIMELINE", self.styles['Heading1']))
        elements.append(Spacer(1, 12))
        
        # This re-uses the same primary concerns from the summary
        elements.append(Paragraph("Primary Concerns Identified:", self.styles['Heading2']))
        if primary_concerns:
            table_data = [['#', Paragraph('Primary Concern Identified', self.styles['Normal'])]]
            col_widths = [0.4 * inch, 6.1 * inch]
            
            for i, concern in enumerate(primary_concerns, 1):
                concern_text = self._format_concern_for_summary(concern, i)
                p = Paragraph(concern_text, self.styles['Normal'])
                table_data.append([str(i), p])
            
            concern_table = Table(table_data, colWidths=col_widths)
            concern_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
                ('BOX', (0, 0), (-1, -1), 2, self.colors['danger']),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, self.colors['border'])
            ]))
            elements.append(concern_table)
        else:
            elements.append(Paragraph("No primary concerns were identified based on the analysis.", self.styles['Normal']))
        
        elements.append(Spacer(1, 24))

        # Full timeline is included here as well
        elements.append(Paragraph("Full Violation Timeline:", self.styles['Heading2']))
        elements.extend(self._build_violation_timeline(analysis_results))
        
        return elements

    def _get_primary_concerns(self, violations: List[Dict[str, Any]], count: int = 4) -> List[Dict[str, Any]]:
        """Selects the most severe and confident violations as primary concerns."""
        # Sort by severity (high > medium > low) and then by confidence
        def severity_key(v):
            return ({'high': 0, 'medium': 1, 'low': 2}.get(v.get('severity', 'low'), 3), -v.get('confidence', 0))
        
        return sorted(violations, key=severity_key)[:count]

    def _format_concern_for_summary(self, concern: Dict[str, Any], index: int) -> str:
        """Formats a single concern for the executive summary table."""
        return (
            f"<b>{concern.get('type')} at {concern.get('timestamp_formatted', 'N/A')} "
            f"(Confidence: {concern.get('confidence', 0):.1%})</b><br/>"
            f"{concern.get('description', 'No description available.')}"
        )

    def _get_overview_data(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Gathers data for the analysis overview table."""
        summary = analysis_results.get('summary', {})
        violations = analysis_results.get('violations', [])
        frame_analyses = analysis_results.get('frame_analyses', [])
        
        return {
            'Overall Severity Level': summary.get('severity_assessment', 'N/A').upper(),
            'Average Analysis Confidence': f"{summary.get('average_confidence', 0):.1%}",
            'Frames with Detected Concerns': f"{len([f for f in frame_analyses if f.get('concerns_detected')])}/{len(frame_analyses)}",
            'Unique Violation Types': len(set(v['type'] for v in violations)),
            'Primary Concerns Found': "YES" if violations else "NO"
        }

    def _build_violation_timeline(self, analysis_results: Dict[str, Any]) -> List:
        """Builds the detected violations timeline list items."""
        elements = []
        
        timeline = analysis_results.get('violation_timeline', [])
        if not timeline:
            elements.append(Paragraph("No specific violation events were detected in the timeline.", self.styles['Normal']))
            return elements
            
        for item in timeline:
            item_text = (
                f"<b>- {item.get('timestamp_formatted', 'N/A')} (Confidence: {item.get('confidence', 0):.1%}, "
                f"Severity: {item.get('severity', 'N/A').upper()})</b><br/>"
                f"<i>{item.get('description', 'No details available.')}</i>"
            )
            elements.append(Paragraph(item_text, self.styles['Normal']))
            elements.append(Spacer(1, 8))
            
        return elements

    def _build_key_audio_segments(self, analysis_results: Dict[str, Any]) -> List:
        """Builds the section for key audio segments, ensuring content can split across pages."""
        elements = []
        elements.append(Paragraph("Key Audio Segments:", self.styles['h1']))
        elements.append(Spacer(1, 12))
        
        audio_violations = [v for v in analysis_results.get('violations', []) if v.get('source') == 'audio']
        
        if not audio_violations:
            elements.append(Paragraph("No key audio segments with violations were identified.", self.styles['Normal']))
            return elements
        
        for violation in audio_violations:
            context = violation.get('audio_context', {})
            snippet = context.get('snippet', 'No snippet available.')
            
            # Use simple paragraphs which are splittable, instead of a table.
            header_text = f"<b>{violation.get('timestamp_formatted')} - {violation.get('type')} (Confidence: {violation.get('confidence', 0):.1%})</b>"
            snippet_text = f"<i>\"{snippet}\"</i>"

            p_header = Paragraph(header_text, self.styles['h4'])
            p_snippet = Paragraph(snippet_text, self.styles['TranscriptText'])

            elements.append(p_header)
            elements.append(Spacer(1, 4))
            elements.append(p_snippet)
            elements.append(Spacer(1, 18))
            
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
        """Formats a single frame analysis, handling potential verbosity and layout issues."""
        frame_elements = []
        
        # Frame Title
        title_text = (
            f"<b>Frame {frame.get('frame_number', 'N/A')} - "
            f"{self._format_timestamp(frame.get('timestamp', 0))} "
            f"(Confidence: {frame.get('confidence', 0):.1%})</b>"
        )
        frame_elements.append(Paragraph(title_text, self.styles['h4']))
        frame_elements.append(Spacer(1, 8))
        
        # Summarize analysis text to avoid excessive verbosity
        analysis_text = frame.get('analysis_text', 'No analysis text available.')
        summary_text = self._summarize_text(analysis_text, max_sentences=3)
        
        frame_elements.append(Paragraph(summary_text, self.styles['Normal']))
        frame_elements.append(Spacer(1, 8))
        
        # Handle "Detected Issues" box to prevent overlap
        if frame.get('concerns_detected') and frame.get('potential_violations'):
            issues_text = "<b>Detected Issues:</b> " + ", ".join(frame.get('potential_violations'))
            
            # Create a Paragraph with a red border, but use a Table to contain it
            issue_paragraph = Paragraph(issues_text, style=self.styles['Normal'])
            issue_table = Table([[issue_paragraph]], colWidths=[6.5 * inch])
            issue_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 2, self.colors['danger']),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ]))
            
            frame_elements.append(issue_table)
            frame_elements.append(Spacer(1, 10))
            
        return [KeepTogether(frame_elements)]

    def _summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """A simple text summarizer to extract key sentences."""
        # A more sophisticated NLP model could be used here.
        # For now, we'll extract the first few sentences and any sentence with a keyword.
        sentences = text.split('. ')
        
        # Prioritize sentences with keywords
        keywords = ['force', 'violation', 'concern', 'escalation', 'threat', 'weapon', 'struggle']
        key_sentences = [s for s in sentences if any(key in s.lower() for key in keywords)]
        
        # Combine with first sentences, ensuring no duplicates
        result_sentences = sentences[:max_sentences]
        for s in key_sentences:
            if s not in result_sentences:
                result_sentences.append(s)
        
        # Limit total length and join
        summary = ". ".join(result_sentences[:max_sentences + 1])
        if len(summary) > 500: # Hard limit
            summary = textwrap.shorten(summary, width=500, placeholder="...")

        return summary + "." if not summary.endswith('.') else summary
    
    def _build_enhanced_recommendations(self, analysis_results: Dict[str, Any]) -> List:
        """Build enhanced recommendations based on detected violations."""
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
        """Build the full audio transcript appendix, allowing content to split across pages."""
        elements = []
        
        elements.append(Paragraph("APPENDIX A: FULL AUDIO TRANSCRIPT", self.styles['Heading1']))
        elements.append(Spacer(1, 12))
        
        audio_analysis = analysis_results.get('audio_analysis', {})
        segments = audio_analysis.get('transcription_segments', [])
        
        if not segments:
            elements.append(Paragraph("No audio transcript available.", self.styles['Normal']))
            return elements
        
        for segment in segments:
            # Handle both object (dataclass) and dict style access safely
            if hasattr(segment, 'text') and hasattr(segment, 'start_time'):
                start_time_val = segment.start_time
                end_time_val = segment.end_time
                text = segment.text
            elif isinstance(segment, dict):
                start_time_val = segment.get('start_time', 0)
                end_time_val = segment.get('end_time', 0)
                text = segment.get('text', '')
            else:
                logger.warning(f"Skipping unknown segment type in transcript appendix: {type(segment)}")
                continue

            start_time = self._format_timestamp(start_time_val)
            end_time = self._format_timestamp(end_time_val)
            
            # Header paragraph for the segment
            header_paragraph = Paragraph(
                f"<b>Transcript Segment: [{start_time} - {end_time}]</b>",
                self.styles['h3'] # Use a heading style for the segment time
            )
            elements.append(header_paragraph)
            elements.append(Spacer(1, 6))

            # Body paragraph, which is allowed to split across pages naturally
            body_paragraph = Paragraph(text, self.styles['TranscriptText'])
            elements.append(body_paragraph)
            elements.append(Spacer(1, 18)) # Add space after each segment
            
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
            story.extend(self._build_primary_concerns(analysis_results))
            
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

    def _format_timestamp(self, seconds: float) -> str:
        """Helper function to format seconds into MM:SS."""
        if seconds is None:
            return "N/A"
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}" 