from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from blueprint.decorators import login_required, admin_required
from controllers.report_controller import ReportController
from blueprint.models import db, User, Profile, Report
import json

report_bp = Blueprint('report', __name__, url_prefix='/report')

@report_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_report():
    """Submit a new report"""
    if request.method == 'POST':
        try:
            # Get form data
            reported_user_id = request.form.get('reported_user_id')
            report_type = request.form.get('report_type')
            title = request.form.get('title')
            description = request.form.get('description')
            severity = request.form.get('severity', 'Medium')
            evidence_urls = request.form.getlist('evidence_urls')
            
            # Validate required fields
            if not all([reported_user_id, report_type, title, description]):
                if request.is_json:
                    return jsonify({'success': False, 'message': 'All fields are required'})
                flash('All fields are required', 'error')
                return redirect(request.url)
            
            # Submit report
            result = ReportController.create_report(
                reporter_id=session['user_id'],
                reported_id=int(reported_user_id),
                report_type=report_type,
                title=title,
                description=description,
                evidence_urls=evidence_urls if evidence_urls else None,
                severity=severity
            )
            
            if request.is_json:
                return jsonify(result)
            
            if result['success']:
                flash(result['message'], 'success')
                return redirect(url_for('report.my_reports'))
            else:
                flash(result['message'], 'error')
                return redirect(request.url)
                
        except Exception as e:
            error_msg = f'Error submitting report: {str(e)}'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg})
            flash(error_msg, 'error')
            return redirect(request.url)
    
    # GET request - show report form
    reported_user_id = request.args.get('user_id')
    reported_user = None
    if reported_user_id:
        reported_user = User.query.get(reported_user_id)
    
    report_types = ReportController.get_report_types()
    severity_levels = ReportController.get_severity_levels()
    
    return render_template('reports/submit_report.html',
                         reported_user=reported_user,
                         report_types=report_types,
                         severity_levels=severity_levels)

@report_bp.route('/my-reports')
@login_required
def my_reports():
    """View reports made by current user"""
    reports_made = ReportController.get_user_reports(session['user_id'], 'made')
    
    return render_template('reports/my_reports.html',
                         reports=reports_made)

@report_bp.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard for managing reports"""
    status_filter = request.args.get('status')
    severity_filter = request.args.get('severity')
    search_term = request.args.get('search')
    search_type = request.args.get('search_type', 'all')
    
    if search_term:
        reports = ReportController.search_reports(search_term, search_type)
    else:
        reports = ReportController.get_all_reports(status_filter, severity_filter)
    
    statistics = ReportController.get_report_statistics()
    report_types = ReportController.get_report_types()
    severity_levels = ReportController.get_severity_levels()
    
    return render_template('reports/admin_dashboard.html',
                         reports=reports,
                         statistics=statistics,
                         report_types=report_types,
                         severity_levels=severity_levels,
                         current_status=status_filter,
                         current_severity=severity_filter,
                         search_term=search_term,
                         search_type=search_type)

@report_bp.route('/admin/update-status', methods=['POST'])
@admin_required
def update_report_status():
    """Update report status (admin only)"""
    try:
        report_id = request.form.get('report_id')
        new_status = request.form.get('status')
        admin_notes = request.form.get('admin_notes')
        resolution = request.form.get('resolution')
        
        if not all([report_id, new_status]):
            if request.is_json:
                return jsonify({'success': False, 'message': 'Report ID and status are required'})
            flash('Report ID and status are required', 'error')
            return redirect(request.referrer or url_for('report.admin_dashboard'))
        
        result = ReportController.update_report_status(
            report_id=int(report_id),
            new_status=new_status,
            admin_id=session['user_id'],
            admin_notes=admin_notes,
            resolution=resolution
        )
        
        if request.is_json:
            return jsonify(result)
        
        # Handle regular form submission
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
        
        # Redirect back to report details or dashboard
        return redirect(url_for('report.view_report_details', report_id=report_id))
        
    except Exception as e:
        error_msg = f'Error updating report: {str(e)}'
        if request.is_json:
            return jsonify({'success': False, 'message': error_msg})
        flash(error_msg, 'error')
        return redirect(request.referrer or url_for('report.admin_dashboard'))
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating report: {str(e)}'})

@report_bp.route('/admin/report/<int:report_id>')
@admin_required
def view_report_details(report_id):
    """View detailed report information"""
    report = Report.query.get_or_404(report_id)
    
    # Parse evidence URLs if they exist
    evidence_urls = []
    if report.evidence_urls:
        try:
            evidence_urls = json.loads(report.evidence_urls)
        except:
            evidence_urls = []
    
    return render_template('reports/report_details.html',
                         report=report,
                         evidence_urls=evidence_urls)

@report_bp.route('/admin/statistics')
@admin_required
def report_statistics():
    """View report statistics and analytics"""
    statistics = ReportController.get_report_statistics()
    
    # Additional analytics
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Reports by type
    reports_by_type = db.session.query(
        Report.report_type,
        func.count(Report.id).label('count')
    ).group_by(Report.report_type).all()
    
    # Reports by month (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    reports_by_month = db.session.query(
        func.date_trunc('month', Report.created_at).label('month'),
        func.count(Report.id).label('count')
    ).filter(Report.created_at >= six_months_ago).group_by('month').order_by('month').all()
    
    return render_template('reports/statistics.html',
                         statistics=statistics,
                         reports_by_type=reports_by_type,
                         reports_by_month=reports_by_month)

@report_bp.route('/user/<int:user_id>/reports')
@admin_required
def user_report_history(user_id):
    """View all reports related to a specific user"""
    user = User.query.get_or_404(user_id)
    reports_made = ReportController.get_user_reports(user_id, 'made')
    reports_received = ReportController.get_user_reports(user_id, 'received')
    
    return render_template('reports/user_report_history.html',
                         user=user,
                         reports_made=reports_made,
                         reports_received=reports_received)

# Public reporting (for reporting profiles from browse page)
@report_bp.route('/report-user/<int:user_id>')
@login_required
def report_user(user_id):
    """Quick report form for a specific user"""
    user = User.query.get_or_404(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    
    report_types = ReportController.get_report_types()
    severity_levels = ReportController.get_severity_levels()
    
    return render_template('reports/quick_report.html',
                         reported_user=user,
                         profile=profile,
                         report_types=report_types,
                         severity_levels=severity_levels)
