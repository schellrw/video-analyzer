"""
Report Generation Service
Generates comprehensive PDF reports for legal use with professional formatting.
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


class ReportGenerationService:
    """Service for generating comprehensive PDF reports for legal use."""
    
    def __init__(self):
        """Initialize the report generation service."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Color scheme for professional reports
        self.colors = {
            'primary': HexColor('#1f2937'),      # Dark gray
            'secondary': HexColor('#374151'),     # Medium gray
            'accent': HexColor('#3b82f6'),       # Blue
            'success': HexColor('#10b981'),      # Green
            'warning': HexColor('#f59e0b'),      # Orange
            'danger': HexColor('#ef4444'),       # Red
            'light_gray': HexColor('#f3f4f6'),   # Light gray
            'border': HexColor('#d1d5db')        # Border gray
        }
        
        logger.info("ReportGenerationService initialized")
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        
        # Helper function to safely add styles
        def add_style_if_not_exists(style_name, style_obj):
            if style_name not in self.styles:
                self.styles.add(style_obj)
        
        # Title style
        add_style_if_not_exists('ReportTitle', ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#1f2937'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        add_style_if_not_exists('SectionHeader', ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#1f2937'),
            fontName='Helvetica-Bold'
        ))
        
        # Subsection header style
        add_style_if_not_exists('SubsectionHeader', ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=HexColor('#374151'),
            fontName='Helvetica-Bold'
        ))
        
        # Body text style - use custom name to avoid conflicts
        add_style_if_not_exists('ReportBodyText', ParagraphStyle(
            name='ReportBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=HexColor('#1f2937'),
            alignment=TA_JUSTIFY
        ))
        
        # Violation alert style
        add_style_if_not_exists('ViolationAlert', ParagraphStyle(
            name='ViolationAlert',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            textColor=HexColor('#ef4444'),
            fontName='Helvetica-Bold',
            backColor=HexColor('#fef2f2'),
            borderColor=HexColor('#ef4444'),
            borderWidth=1,
            borderPadding=8
        ))
        
        # Timestamp style
        add_style_if_not_exists('Timestamp', ParagraphStyle(
            name='Timestamp',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#6b7280'),
            fontName='Helvetica-Bold'
        ))
    
    def generate_comprehensive_report(self, analysis_results: Dict[str, Any], 
                                    case_info: Dict[str, Any] = None,
                                    output_path: str = None) -> str:
        """
        Generate a comprehensive PDF report from video analysis results.
        
        Args:
            analysis_results: Results from video analysis
            case_info: Optional case information
            output_path: Optional output file path
            
        Returns:
            Path to the generated PDF file
        """
        try:
            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                case_id = case_info.get('case_id', 'unknown') if case_info else 'unknown'
                output_path = f"reports/video_analysis_report_{case_id}_{timestamp}.pdf"
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build report content
            story = []
            
            # Title page
            story.extend(self._build_title_page(analysis_results, case_info))
            story.append(PageBreak())
            
            # Executive summary
            story.extend(self._build_executive_summary(analysis_results))
            story.append(PageBreak())
            
            # Violation timeline
            story.extend(self._build_violation_timeline(analysis_results))
            story.append(PageBreak())
            
            # Detailed analysis
            story.extend(self._build_detailed_analysis(analysis_results))
            story.append(PageBreak())
            
            # Statistical analysis
            story.extend(self._build_statistical_analysis(analysis_results))
            story.append(PageBreak())
            
            # Recommendations
            story.extend(self._build_recommendations(analysis_results))
            story.append(PageBreak())
            
            # Technical appendix
            story.extend(self._build_technical_appendix(analysis_results))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise
    
    def _build_title_page(self, analysis_results: Dict[str, Any], 
                         case_info: Dict[str, Any] = None) -> List:
        """Build the title page of the report."""
        elements = []
        
        # Main title
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(
            "VIDEO ANALYSIS REPORT",
            self.styles['ReportTitle']
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
                ['Analysis Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
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
        severity = summary.get('severity_assessment', 'low').upper()
        concerns_found = summary.get('concerns_found', False)
        
        severity_color = self.colors['success']
        if severity == 'HIGH':
            severity_color = self.colors['danger']
        elif severity == 'MEDIUM':
            severity_color = self.colors['warning']
        
        summary_data = [
            ['ANALYSIS SUMMARY'],
            [f"Severity Level: {severity}"],
            [f"Concerns Detected: {'YES' if concerns_found else 'NO'}"],
            [f"Overall Confidence: {summary.get('average_confidence', 0):.1%}"],
            [f"Violations Found: {len(summary.get('violations_detected', []))}"]
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
        
        # Disclaimer
        disclaimer_text = """
        <b>LEGAL DISCLAIMER:</b> This report is generated using artificial intelligence 
        analysis and should be used as a supplementary tool for investigation purposes only. 
        All findings should be verified through manual review and additional investigation. 
        This analysis does not constitute legal advice or definitive evidence.
        """
        
        elements.append(Paragraph(disclaimer_text, self.styles['ReportBodyText']))
        
        return elements
    
    def _build_executive_summary(self, analysis_results: Dict[str, Any]) -> List:
        """Build the executive summary section."""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        
        summary = analysis_results.get('summary', {})
        
        # Overview paragraph
        overview_text = f"""
        This report presents the results of an automated video analysis conducted on 
        {analysis_results.get('total_frames_analyzed', 0)} key frames extracted from the provided video footage. 
        The analysis was completed in {analysis_results.get('processing_time', 0):.2f} seconds using 
        advanced AI vision models specifically trained for law enforcement scenario analysis.
        """
        
        elements.append(Paragraph(overview_text, self.styles['ReportBodyText']))
        elements.append(Spacer(1, 12))
        
        # Key findings
        elements.append(Paragraph("Key Findings:", self.styles['SubsectionHeader']))
        
        key_findings = summary.get('key_findings', [])
        if key_findings:
            for i, finding in enumerate(key_findings[:5], 1):  # Top 5 findings
                finding_text = f"""
                <b>{i}. Timestamp {finding.get('timestamp_formatted', 'N/A')}</b> 
                (Confidence: {finding.get('confidence', 0):.1%})<br/>
                {finding.get('description', 'No description available')[:200]}...
                """
                elements.append(Paragraph(finding_text, self.styles['ReportBodyText']))
                elements.append(Spacer(1, 6))
        else:
            elements.append(Paragraph("No significant findings detected in the analyzed frames.", 
                                    self.styles['ReportBodyText']))
        
        elements.append(Spacer(1, 12))
        
        # Violations summary
        violations = summary.get('violations_detected', [])
        if violations:
            elements.append(Paragraph("Potential Violations Detected:", self.styles['SubsectionHeader']))
            for violation in violations:
                elements.append(Paragraph(f"• {violation.title()}", self.styles['ReportBodyText']))
        
        elements.append(Spacer(1, 12))
        
        # Recommendations summary
        recommendations = analysis_results.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("Priority Recommendations:", self.styles['SubsectionHeader']))
            for rec in recommendations[:3]:  # Top 3 recommendations
                elements.append(Paragraph(f"• {rec}", self.styles['ReportBodyText']))
        
        return elements
    
    def _build_violation_timeline(self, analysis_results: Dict[str, Any]) -> List:
        """Build the violation timeline section."""
        elements = []
        
        elements.append(Paragraph("VIOLATION TIMELINE", self.styles['SectionHeader']))
        
        timeline = analysis_results.get('violation_timeline', [])
        
        if not timeline:
            elements.append(Paragraph(
                "No violations detected in the analyzed timeframe.",
                self.styles['ReportBodyText']
            ))
            return elements
        
        elements.append(Paragraph(
            "The following timeline shows detected violations ordered by priority (severity × confidence):",
            self.styles['ReportBodyText']
        ))
        elements.append(Spacer(1, 12))
        
        # Create timeline table
        timeline_data = [['Time', 'Severity', 'Confidence', 'Violations', 'Description']]
        
        for item in timeline:
            severity = item.get('severity', 'low').upper()
            confidence = f"{item.get('confidence', 0):.1%}"
            violations = ', '.join(item.get('violations', []))
            description = item.get('description', '')[:100] + '...' if len(item.get('description', '')) > 100 else item.get('description', '')
            
            timeline_data.append([
                item.get('timestamp_formatted', 'N/A'),
                severity,
                confidence,
                violations,
                description
            ])
        
        timeline_table = Table(timeline_data, colWidths=[1*inch, 0.8*inch, 0.8*inch, 1.5*inch, 2.4*inch])
        
        # Style the table
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]
        
        # Color code severity levels
        for i, item in enumerate(timeline, 1):
            severity = item.get('severity', 'low')
            if severity == 'high':
                table_style.append(('BACKGROUND', (1, i), (1, i), self.colors['danger']))
                table_style.append(('TEXTCOLOR', (1, i), (1, i), white))
            elif severity == 'medium':
                table_style.append(('BACKGROUND', (1, i), (1, i), self.colors['warning']))
        
        timeline_table.setStyle(TableStyle(table_style))
        elements.append(timeline_table)
        
        return elements
    
    def _build_detailed_analysis(self, analysis_results: Dict[str, Any]) -> List:
        """Build the detailed frame-by-frame analysis section."""
        elements = []
        
        elements.append(Paragraph("DETAILED FRAME ANALYSIS", self.styles['SectionHeader']))
        
        frame_analyses = analysis_results.get('frame_analyses', [])
        
        elements.append(Paragraph(
            f"This section provides detailed analysis for all {len(frame_analyses)} analyzed frames. "
            "Only frames with detected concerns are shown in detail.",
            self.styles['ReportBodyText']
        ))
        elements.append(Spacer(1, 12))
        
        concerning_frames = [f for f in frame_analyses if f.get('concerns_detected', False)]
        
        if not concerning_frames:
            elements.append(Paragraph(
                "No concerning activities detected in any analyzed frames.",
                self.styles['ReportBodyText']
            ))
            return elements
        
        for frame in concerning_frames:
            # Frame header
            frame_header = f"Frame {frame.get('frame_number', 'N/A')} - {frame.get('timestamp_formatted', 'N/A')}"
            elements.append(Paragraph(frame_header, self.styles['SubsectionHeader']))
            
            # Frame details table
            frame_data = [
                ['Confidence:', f"{frame.get('confidence', 0):.1%}"],
                ['Severity:', frame.get('severity_level', 'N/A').title()],
                ['Processing Time:', f"{frame.get('processing_time', 0):.3f}s"],
                ['Cached Result:', 'Yes' if frame.get('cached', False) else 'No']
            ]
            
            frame_table = Table(frame_data, colWidths=[1.5*inch, 2*inch])
            frame_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            elements.append(frame_table)
            elements.append(Spacer(1, 8))
            
            # Violations
            violations = frame.get('potential_violations', [])
            if violations:
                violations_text = f"<b>Detected Violations:</b> {', '.join(violations)}"
                elements.append(Paragraph(violations_text, self.styles['ViolationAlert']))
                elements.append(Spacer(1, 6))
            
            # Description
            description = frame.get('description', 'No description available.')
            elements.append(Paragraph(f"<b>Analysis:</b> {description}", self.styles['ReportBodyText']))
            
            # Key objects and actions
            key_objects = frame.get('key_objects', [])
            officer_actions = frame.get('officer_actions', [])
            civilian_actions = frame.get('civilian_actions', [])
            
            if key_objects or officer_actions or civilian_actions:
                elements.append(Spacer(1, 6))
                
                if key_objects:
                    elements.append(Paragraph(f"<b>Key Objects:</b> {', '.join(key_objects)}", 
                                            self.styles['ReportBodyText']))
                
                if officer_actions:
                    elements.append(Paragraph(f"<b>Officer Actions:</b> {', '.join(officer_actions)}", 
                                            self.styles['ReportBodyText']))
                
                if civilian_actions:
                    elements.append(Paragraph(f"<b>Civilian Actions:</b> {', '.join(civilian_actions)}", 
                                            self.styles['ReportBodyText']))
            
            elements.append(Spacer(1, 16))
        
        return elements
    
    def _build_statistical_analysis(self, analysis_results: Dict[str, Any]) -> List:
        """Build the statistical analysis section."""
        elements = []
        
        elements.append(Paragraph("STATISTICAL ANALYSIS", self.styles['SectionHeader']))
        
        summary = analysis_results.get('summary', {})
        
        # Confidence distribution
        confidence_dist = summary.get('confidence_distribution', {})
        
        stats_data = [
            ['Metric', 'Value'],
            ['Total Frames Analyzed', str(analysis_results.get('total_frames_analyzed', 0))],
            ['Processing Time', f"{analysis_results.get('processing_time', 0):.2f} seconds"],
            ['Average Confidence', f"{summary.get('average_confidence', 0):.1%}"],
            ['Frames with High Confidence (>70%)', str(confidence_dist.get('high', 0))],
            ['Frames with Medium Confidence (40-70%)', str(confidence_dist.get('medium', 0))],
            ['Frames with Low Confidence (<40%)', str(confidence_dist.get('low', 0))],
            ['Total Concerning Frames', str(summary.get('total_concerning_frames', 0))],
            ['Unique Violations Detected', str(len(summary.get('violations_detected', [])))],
            ['Overall Severity Assessment', summary.get('severity_assessment', 'low').title()],
            ['Estimated API Cost', f"${analysis_results.get('total_api_cost_estimate', 0):.4f}"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.colors['light_gray']]),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        # Violation breakdown
        violations = summary.get('violations_detected', [])
        if violations:
            elements.append(Paragraph("Violation Types Detected:", self.styles['SubsectionHeader']))
            
            violation_data = [['Violation Type', 'Frequency']]
            
            # Count violations across all frames
            violation_counts = {}
            for frame in analysis_results.get('frame_analyses', []):
                for violation in frame.get('potential_violations', []):
                    violation_counts[violation] = violation_counts.get(violation, 0) + 1
            
            for violation, count in violation_counts.items():
                violation_data.append([violation.title(), str(count)])
            
            violation_table = Table(violation_data, colWidths=[3*inch, 1*inch])
            violation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.colors['light_gray']]),
            ]))
            
            elements.append(violation_table)
        
        return elements
    
    def _build_recommendations(self, analysis_results: Dict[str, Any]) -> List:
        """Build the recommendations section."""
        elements = []
        
        elements.append(Paragraph("RECOMMENDATIONS", self.styles['SectionHeader']))
        
        recommendations = analysis_results.get('recommendations', [])
        
        if not recommendations:
            elements.append(Paragraph(
                "No specific recommendations generated based on the analysis results.",
                self.styles['ReportBodyText']
            ))
            return elements
        
        elements.append(Paragraph(
            "Based on the analysis results, the following recommendations are provided:",
            self.styles['ReportBodyText']
        ))
        elements.append(Spacer(1, 12))
        
        for i, recommendation in enumerate(recommendations, 1):
            rec_text = f"<b>{i}.</b> {recommendation}"
            elements.append(Paragraph(rec_text, self.styles['ReportBodyText']))
            elements.append(Spacer(1, 6))
        
        elements.append(Spacer(1, 12))
        
        # General recommendations
        general_recs = [
            "Conduct manual review of all flagged timestamps for verification",
            "Cross-reference findings with witness statements and other evidence",
            "Consider additional video angles if available",
            "Document all findings in the official case file",
            "Consult with legal counsel regarding potential violations"
        ]
        
        elements.append(Paragraph("General Recommendations:", self.styles['SubsectionHeader']))
        
        for rec in general_recs:
            elements.append(Paragraph(f"• {rec}", self.styles['ReportBodyText']))
            elements.append(Spacer(1, 4))
        
        return elements
    
    def _build_technical_appendix(self, analysis_results: Dict[str, Any]) -> List:
        """Build the technical appendix section."""
        elements = []
        
        elements.append(Paragraph("TECHNICAL APPENDIX", self.styles['SectionHeader']))
        
        # Analysis methodology
        elements.append(Paragraph("Analysis Methodology:", self.styles['SubsectionHeader']))
        
        methodology_text = f"""
        This analysis was conducted using the LLaVA (Large Language and Vision Assistant) model 
        via the Hugging Face Inference API. The video was processed using a 
        {analysis_results.get('extraction_strategy', 'uniform')} frame extraction strategy, 
        analyzing {analysis_results.get('total_frames_analyzed', 0)} key frames.
        
        Each frame was analyzed for potential civil rights violations, police misconduct, 
        and concerning behavior using a specialized prompt designed for law enforcement scenarios. 
        Confidence scores were calculated based on the specificity and certainty of the AI's analysis.
        """
        
        elements.append(Paragraph(methodology_text, self.styles['ReportBodyText']))
        elements.append(Spacer(1, 12))
        
        # Technical specifications
        elements.append(Paragraph("Technical Specifications:", self.styles['SubsectionHeader']))
        
        tech_data = [
            ['Parameter', 'Value'],
            ['AI Model', 'LLaVA-1.5-7B-HF'],
            ['Frame Extraction Strategy', analysis_results.get('extraction_strategy', 'uniform').title()],
            ['Maximum Frames Analyzed', str(analysis_results.get('total_frames_analyzed', 0))],
            ['Image Resolution', '512x512 (max dimension)'],
            ['Image Quality', '85% JPEG'],
            ['Analysis Timestamp', analysis_results.get('analysis_timestamp', 'N/A')],
            ['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')]
        ]
        
        tech_table = Table(tech_data, colWidths=[2.5*inch, 3*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.colors['light_gray']]),
        ]))
        
        elements.append(tech_table)
        elements.append(Spacer(1, 12))
        
        # Limitations and disclaimers
        elements.append(Paragraph("Limitations and Disclaimers:", self.styles['SubsectionHeader']))
        
        limitations_text = """
        <b>Important Limitations:</b>
        
        • AI analysis is supplementary and should not replace human judgment
        • Results may vary based on video quality, lighting, and camera angles
        • False positives and false negatives are possible
        • Context outside the frame is not considered in the analysis
        • Legal interpretation requires human expertise and additional evidence
        
        <b>Recommended Use:</b>
        
        This report should be used as a starting point for investigation and manual review. 
        All flagged incidents should be verified through additional analysis, witness statements, 
        and other available evidence before drawing legal conclusions.
        """
        
        elements.append(Paragraph(limitations_text, self.styles['ReportBodyText']))
        
        return elements
    
    def generate_summary_report(self, analysis_results: Dict[str, Any], 
                              output_path: str = None) -> str:
        """
        Generate a shorter summary report for quick review.
        
        Args:
            analysis_results: Results from video analysis
            output_path: Optional output file path
            
        Returns:
            Path to the generated PDF file
        """
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"reports/video_analysis_summary_{timestamp}.pdf"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            
            # Title
            story.append(Paragraph("VIDEO ANALYSIS SUMMARY", self.styles['ReportTitle']))
            story.append(Spacer(1, 20))
            
            # Executive summary
            story.extend(self._build_executive_summary(analysis_results))
            story.append(Spacer(1, 20))
            
            # Key statistics
            summary = analysis_results.get('summary', {})
            stats_text = f"""
            <b>Quick Statistics:</b><br/>
            • Total Frames Analyzed: {analysis_results.get('total_frames_analyzed', 0)}<br/>
            • Concerning Frames: {summary.get('total_concerning_frames', 0)}<br/>
            • Average Confidence: {summary.get('average_confidence', 0):.1%}<br/>
            • Severity Level: {summary.get('severity_assessment', 'low').title()}<br/>
            • Processing Time: {analysis_results.get('processing_time', 0):.2f} seconds
            """
            
            story.append(Paragraph(stats_text, self.styles['ReportBodyText']))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Summary report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating summary report: {str(e)}")
            raise 