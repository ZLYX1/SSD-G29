# controllers/browse_controller.py

from blueprint.models import Profile, User, TimeSlot, Booking, Favourite
from extensions import db
from sqlalchemy import and_
from datetime import datetime, time, timedelta

class BrowseController:
    @staticmethod
    def get_profiles(user_role, filters=None, limit=None):
        query = BrowseController.get_userQuery(user_role=user_role,
                                               user_active=True, 
                                               user_deleted=False)
        
        if filters:
            if filters.get('min_age') is not None:
                query = query.filter(Profile.age >= filters['min_age'])

            if filters.get('max_age') is not None:
                query = query.filter(Profile.age <= filters['max_age'])

            if filters.get('gender'):
                query = query.filter(User.gender == filters['gender'])

            if filters.get('min_rating') is not None:
                query = query.filter(Profile.rating >= filters['min_rating'])

            if filters.get('avail_date'):
                try:
                    # Parse datetime from avail_date and avail_time
                    if filters.get('avail_time'):
                        selected_datetime = datetime.strptime(
                            f"{filters['avail_date']} {filters['avail_time']}", "%Y-%m-%d %H:%M"
                        )
                    else:
                        selected_datetime = datetime.combine(
                            datetime.strptime(filters['avail_date'], "%Y-%m-%d"), time(0, 0)
                        )

                    # Join with TimeSlot to find available users
                    query = query.join(TimeSlot).filter(
                        and_(
                            TimeSlot.start_time <= selected_datetime,
                            TimeSlot.end_time > selected_datetime
                        )
                    )

                    # Exclude those already booked
                    overlapping_bookings = db.session.query(Booking.escort_id).filter(
                        Booking.status.in_(["Pending", "Confirmed"]),
                        Booking.start_time < selected_datetime,
                        Booking.end_time > selected_datetime
                    ).subquery()

                    query = query.filter(~User.id.in_(overlapping_bookings))

                except ValueError:
                    pass  # Invalid datetime input ignored

        if limit:
            query = query.limit(limit)

        return query.distinct().all()
	

    @staticmethod
    def get_favourite_ids(user_id):
        return [f.favourite_user_id for f in Favourite.query.filter_by(user_id=user_id).all()]

    @staticmethod
    def get_userQuery(user_role, user_active = True, user_deleted = False):
    
        return Profile.query.join(User).filter(
            User.role == user_role,
            User.active == True,
            User.deleted == False
        )

    @staticmethod
    def get_overlapping(escort_id, start_time, end_time, allowed_statuses=["Pending", "Confirmed"]):
        return Booking.query.filter(
        Booking.escort_id == escort_id,
        Booking.status.in_(allowed_statuses),
        Booking.start_time < end_time,
        Booking.end_time > start_time
    ).first()
    
    @staticmethod
    def get_specific_profile(user_id, deleted, active):
        return Profile.query.join(User).filter(
        Profile.user_id == user_id,
        User.deleted == deleted,  # Exclude deleted users
        User.active == active    # Only show active users
    ).first()

    
    @staticmethod
    def get_available_slots(user_id, start_time = None, end_time= None):
        if end_time is None:
            return TimeSlot.query.filter(
                TimeSlot.user_id == user_id,
                TimeSlot.start_time >= datetime.utcnow()
            ).order_by(TimeSlot.start_time.asc()).all()
        else:
            return TimeSlot.query.filter(
                TimeSlot.user_id == user_id,
                TimeSlot.start_time <= start_time,
                TimeSlot.end_time >= end_time
            ).first()

    @staticmethod
    def get_valid_start_times(slot, duration_minutes, escort_id):
        valid_starts = []
        current_start = slot.start_time
        end_limit = slot.end_time - timedelta(minutes=duration_minutes)
        while current_start <= end_limit:
            current_end = current_start + timedelta(minutes=duration_minutes)
            conflict = BrowseController.get_overlapping(
			escort_id=escort_id,
   			start_time= current_start,
   			end_time= current_end
    		)
            # conflict = Booking.query.filter(
            #     Booking.escort_id == escort_id,
            #     Booking.status.in_(["Pending", "Confirmed"]),
            #     Booking.start_time < current_end,
            #     Booking.end_time > current_start
            # ).first()
            if not conflict and current_start >= datetime.utcnow():
                valid_starts.append(current_start)
            current_start += timedelta(minutes=15)
        return valid_starts

    @staticmethod
    def toggle_favourite(current_user_id, target_user_id):
        existing = Favourite.query.filter_by(user_id=current_user_id, favourite_user_id=target_user_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return 'removed'
        else:
            new_fav = Favourite(user_id=current_user_id, favourite_user_id=target_user_id)
            db.session.add(new_fav)
            db.session.commit()
            return 'added'

    '''@staticmethod
    def can_book(escort_id, new_start, new_end):
        # 1. Check if escort has availability covering the requested time
        available_slot = BrowseController.get_available_slots(
		user_id=escort_id,
		start_time=new_start,
		end_time= new_end
	    )
        if not available_slot:
            return False, "Escort is not available for the requested time."
    
        # 2. Check for overlapping bookings (Pending or Confirmed)
        overlapping_booking = BrowseController.get_overlapping(
    		escort_id=escort_id,
	    	start_time=new_start,
    		end_time=new_end
    	)
        if overlapping_booking:
            return False, "The escort already has a booking that conflicts with this time."
        # If all good
        return True, "Time slot is available for booking."
'''
