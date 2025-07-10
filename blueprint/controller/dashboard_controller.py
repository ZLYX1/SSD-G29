# controllers/dashboard_controller.py
from blueprint.models import Booking, User, Favourite, Profile, Payment, Report
from extensions import db
from sqlalchemy import func, text
 
class DashboardController:
 
    @staticmethod
    def get_user_spending_summary(user_id):
        if not user_id:
            return None
 
        total_spent = db.session.query(func.sum(Payment.amount)).filter_by(user_id=user_id).scalar() or 0
        total_transactions = db.session.query(func.count(Payment.id)).filter_by(user_id=user_id).scalar() or 0
 
        monthly_breakdown = db.session.query(
            func.date_trunc('month', Payment.created_at).label('month'),
            func.sum(Payment.amount).label('total')
        ).filter(
            Payment.user_id == user_id
        ).group_by(
            func.date_trunc('month', Payment.created_at)
        ).order_by(text('month desc')).limit(1).all()
 
        breakdown = []
        for month, total in monthly_breakdown:  # or monthly_earnings
            try:
                breakdown.append({
            		"month": month.strftime("%Y-%m"),
            		"total": float(total)
        		})
            except Exception as e:
                print(f"[DEBUG] Error formatting month/total: month={month}, total={total}, error={e}")
                continue  # Skip the bad entry
    
        return {
            "total_spent": round(float(total_spent), 2),
            "transaction_count": total_transactions,
            "monthly_breakdown": breakdown
        }
 
    @staticmethod
    def get_user_earning_summary(user_id):
        if not user_id:
            return None
 
        total_earned = db.session.query(func.sum(Payment.amount))\
            .join(Booking, Payment.booking_id == Booking.id)\
            .filter(Booking.escort_id == user_id).scalar() or 0
 
        total_paid_bookings = db.session.query(func.count(Payment.id))\
            .join(Booking, Payment.booking_id == Booking.id)\
            .filter(Booking.escort_id == user_id).scalar() or 0
 
        monthly_earnings = db.session.query(
            func.date_trunc('month', Payment.created_at).label('month'),
            func.sum(Payment.amount).label('total')
        ).join(Booking, Payment.booking_id == Booking.id)\
         .filter(Booking.escort_id == user_id)\
         .group_by(func.date_trunc('month', Payment.created_at))\
         .order_by(text('month desc')).limit(6).all()
 
        breakdown = [
            {"month": month.strftime("%Y-%m"), "total": float(total)}
            for month, total in monthly_earnings
        ]
 
        return {
            "total_earned": round(float(total_earned), 2),
            "paid_bookings": total_paid_bookings,
            "monthly_breakdown": breakdown
        }
 
    @staticmethod
    def get_favourite_profiles(user_id):
        favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=user_id).all()]
        # # favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=session['user_id']).all()]
        # if favourite_ids:
        #     return Profile.query.filter(Profile.user_id.in_(favourite_ids)).all()
        # else: 
        #     return []
        
        try:
            favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=user_id).all()]
            if favourite_ids:
                return Profile.query.filter(Profile.user_id.in_(favourite_ids)).all()
            return []
        except Exception as e:
            print("Error fetching favourites:", e)
            return []
 
    # @staticmethod
    def get_upcoming_bookings_count(user_id):
        return db.session.query(Booking).join(
            User, Booking.escort_id == User.id
        ).filter(
            Booking.seeker_id == user_id,
            Booking.status == 'Confirmed',
            User.deleted == False,
            User.active == True,
            User.activate == True
        ).count()
 
    @staticmethod
    def get_booking_requests_count(user_id):
        return db.session.query(Booking).join(
            User, Booking.seeker_id == User.id
        ).filter(
            Booking.escort_id == user_id,
            Booking.status == 'Pending',
            User.deleted == False,
            User.active == True,
            User.activate == True
        ).count()
 
    # @staticmethod
    # def get_admin_dashboard_counts():
    #     total_users = User.query.count()
    #     total_reports = Report.query.filter_by(status='Pending Review').count()
    #     seeker_to_escort = User.query.filter(User.role == 'seeker', User.pending_role == 'escort').count()
    #     escort_to_seeker = User.query.filter(User.role == 'escort', User.pending_role == 'seeker').count()
 
    #     return {
    #         'total_users': total_users,
    #         'total_reports': total_reports,
    #         'seeker_to_escort_requests': seeker_to_escort,
    #         'escort_to_seeker_requests': escort_to_seeker
    #     }
