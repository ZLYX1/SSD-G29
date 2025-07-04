from flask import session, flash
from blueprint.models import db, Report, User, Profile
from datetime import datetime, timedelta
import json

class ReportController:
    """Controller for handling user reports"""
    
    @staticmethod
    def create_report(reporter_id, reported_id, report_type, title, description, evidence_urls=None, severity='Medium'):
        """Create a new report"""
        try:
            # Validate users exist
            reporter = User.query.get(reporter_id)
            reported = User.query.get(reported_id)
            
            if not reporter or not reported:
                return {'success': False, 'message': 'Invalid user specified'}
            
            # Prevent self-reporting
            if reporter_id == reported_id:
                return {'success': False, 'message': 'You cannot report yourself'}
            
            # Check for duplicate recent reports (within 24 hours)
            existing_report = Report.query.filter_by(
                reporter_id=reporter_id,
                reported_id=reported_id,
                report_type=report_type
            ).filter(
                Report.created_at >= datetime.now() - timedelta(hours=24)
            ).first()
            
            if existing_report:
                return {'success': False, 'message': 'You have already reported this user for this reason recently'}
            
            # Create new report
            new_report = Report(
                reporter_id=reporter_id,
                reported_id=reported_id,
                report_type=report_type,
                title=title,
                description=description,
                evidence_urls=json.dumps(evidence_urls) if evidence_urls else None,
                severity=severity,
                status='Pending Review'
            )
            
            db.session.add(new_report)
            db.session.commit()
            
            return {
                'success': True, 
                'message': 'Report submitted successfully. Our team will review it shortly.',
                'report_id': new_report.id
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error creating report: {str(e)}'}
    
    @staticmethod
    def get_user_reports(user_id, report_type='made', limit=50):
        """Get reports made by or against a user"""
        try:
            if report_type == 'made':
                reports = Report.query.filter_by(reporter_id=user_id).order_by(Report.created_at.desc()).limit(limit).all()
            elif report_type == 'received':
                reports = Report.query.filter_by(reported_id=user_id).order_by(Report.created_at.desc()).limit(limit).all()
            else:
                return []
            
            return reports
        except Exception as e:
            print(f"Error fetching user reports: {e}")
            return []
    
    @staticmethod
    def get_all_reports(status=None, severity=None, limit=100):
        """Get all reports for admin review"""
        try:
            query = Report.query
            
            if status:
                query = query.filter_by(status=status)
            if severity:
                query = query.filter_by(severity=severity)
            
            reports = query.order_by(Report.created_at.desc()).limit(limit).all()
            return reports
        except Exception as e:
            print(f"Error fetching reports: {e}")
            return []
    
    @staticmethod
    def update_report_status(report_id, new_status, admin_id, admin_notes=None, resolution=None):
        """Update report status (admin only)"""
        try:
            report = Report.query.get(report_id)
            if not report:
                return {'success': False, 'message': 'Report not found'}
            
            report.status = new_status
            report.assigned_admin_id = admin_id
            report.updated_at = datetime.utcnow()
            
            if admin_notes:
                report.admin_notes = admin_notes
            if resolution:
                report.resolution = resolution
            if new_status in ['Resolved', 'Dismissed']:
                report.resolved_at = datetime.utcnow()
            
            db.session.commit()
            
            return {'success': True, 'message': f'Report status updated to {new_status}'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error updating report: {str(e)}'}
    
    @staticmethod
    def get_report_statistics():
        """Get report statistics for admin dashboard"""
        try:
            stats = {
                'total_reports': Report.query.count(),
                'pending_reports': Report.query.filter_by(status='Pending Review').count(),
                'under_investigation': Report.query.filter_by(status='Under Investigation').count(),
                'resolved_reports': Report.query.filter_by(status='Resolved').count(),
                'dismissed_reports': Report.query.filter_by(status='Dismissed').count(),
                'high_severity': Report.query.filter_by(severity='High').count(),
                'critical_severity': Report.query.filter_by(severity='Critical').count(),
            }
            
            # Recent reports (last 7 days)
            from datetime import timedelta
            week_ago = datetime.now() - timedelta(days=7)
            stats['recent_reports'] = Report.query.filter(Report.created_at >= week_ago).count()
            
            return stats
        except Exception as e:
            print(f"Error getting report statistics: {e}")
            return {}
    
    @staticmethod
    def get_report_types():
        """Get available report types"""
        return [
            ('inappropriate_behavior', 'Inappropriate Behavior'),
            ('harassment', 'Harassment or Abuse'),
            ('fraud', 'Fraud or Scam'),
            ('fake_profile', 'Fake Profile'),
            ('violence_threats', 'Violence or Threats'),
            ('spam', 'Spam or Solicitation'),
            ('underage', 'Underage User'),
            ('identity_theft', 'Identity Theft'),
            ('privacy_violation', 'Privacy Violation'),
            ('other', 'Other')
        ]
    
    @staticmethod
    def get_severity_levels():
        """Get available severity levels"""
        return [
            ('Low', 'Low - Minor issue'),
            ('Medium', 'Medium - Moderate concern'),
            ('High', 'High - Serious issue'),
            ('Critical', 'Critical - Immediate attention required')
        ]
    
    @staticmethod
    def search_reports(search_term, search_type='all'):
        """Search reports by various criteria"""
        try:
            query = Report.query
            
            if search_type == 'reporter_email':
                query = query.join(User, Report.reporter_id == User.id).filter(
                    User.email.ilike(f'%{search_term}%')
                )
            elif search_type == 'reported_email':
                query = query.join(User, Report.reported_id == User.id).filter(
                    User.email.ilike(f'%{search_term}%')
                )
            elif search_type == 'title':
                query = query.filter(Report.title.ilike(f'%{search_term}%'))
            elif search_type == 'description':
                query = query.filter(Report.description.ilike(f'%{search_term}%'))
            else:  # search all text fields
                query = query.filter(
                    db.or_(
                        Report.title.ilike(f'%{search_term}%'),
                        Report.description.ilike(f'%{search_term}%')
                    )
                )
            
            return query.order_by(Report.created_at.desc()).limit(50).all()
        except Exception as e:
            print(f"Error searching reports: {e}")
            return []
