import pytest
from app import app as flask_app
from blueprint.models import db
from sqlalchemy import text
from unittest.mock import patch
from blueprint.models import User, Profile, TimeSlot, Booking, Payment, Rating
from datetime import datetime, timedelta
import re
from flask_wtf.csrf import generate_csrf

@pytest.fixture(autouse=True)
def bypass_recaptcha():
    with patch('blueprint.auth.verify_recaptcha', return_value=True):
        yield

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # disable CSRF for testing

    with flask_app.app_context():
        db.create_all()
    yield flask_app
    with flask_app.app_context():
        db.session.remove()
        db.session.execute(text('TRUNCATE TABLE "favourite" CASCADE'))
        db.session.execute(text('TRUNCATE TABLE "user" CASCADE'))
        db.session.commit()
        # optionally drop tables: db.drop_all()

@pytest.fixture(autouse=True)
def disable_csrf(monkeypatch):
    monkeypatch.setattr('flask_wtf.csrf.validate_csrf', lambda *args, **kwargs: True)
        
@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def disable_custom_csrf(monkeypatch):
    monkeypatch.setattr('controllers.security_controller.validate_csrf', lambda *args, **kwargs: None)
    
    
# auth
'''def test_profile_get_and_update(client, app):
    # Register user
    resp = client.post('/auth/?mode=register', data={
        'form_type': 'register',
    'email': 'test@example.com',
    'password': 'Password123!',
    'confirm_password': 'Password123!',
    'age': '25',
    'gender': 'male',
    'role': 'seeker',
    'preference': 'female',
    'age_verify': 'on',  # ✅ FIXED
    'g-recaptcha-response': 'dummy-token'
}, follow_redirects=True)
    assert resp.status_code == 200
    # print("RESPONSE DATA:")
    # print(resp.data.decode())
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None, "User should exist after registration"

        # Activate user for next steps if needed
        user.active = True
        user.email_verified = True
        db.session.commit()
'''

'''
def register_user(client):
    return client.post('/auth/?mode=register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'age': '25',
        'gender': 'male',
        'role': 'seeker',
        'preference': 'female',
        'age_verify': 'on',
        'form_type': 'register',
        'g-recaptcha-response': 'dummy-token'
    }, follow_redirects=True)
    '''
    
def login_user(client, email='test@example.com', password='password123'):
    return client.post('/auth/?mode=login', data={
        'email': email,
        'password': password,
        'form_type': 'login'
    }, follow_redirects=True)
    
#end of auth
    
# profile
'''def test_profile_photo_save(client, app):
    register_user(client)
    
    with app.app_context():
        # Ensure user is verified + active after registration
        user = User.query.filter_by(email='test@example.com').first()
        user.email_verified = True
        user.active = True
        db.session.commit()

    login_user(client)

    photo_url = 'http://example.com/photo.jpg'

    # Test saving photo URL
    resp = client.post('/profile/save-photo', json={'photo_url': photo_url})
    assert resp.status_code == 200, f"Unexpected status code: {resp.status_code}\nResponse: {resp.data.decode()}"

    json_data = resp.get_json()
    assert json_data['message'] == 'Photo saved successfully'

    # Verify the user's photo_url field is updated in DB
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()  # re-query here
        profile = Profile.query.filter_by(user_id=user.id).first()
        assert profile.photo == photo_url        
			
        
@pytest.mark.parametrize("initial_role,expected_pending_role,flash_message_part", [
    ('seeker', 'escort', "seeker ➔ escort"),
    ('escort', 'seeker', "escort ➔ seeker"),
])
def test_request_role_change(client, initial_role, expected_pending_role, flash_message_part):
    email = 'test@example.com'
    register_and_activate_user(client, email=email, role=initial_role)
    login_user(client, email=email)

    # Do not follow redirects here to preserve flash messages in session
    resp = client.post('/profile/request-role-change', follow_redirects=False)
    assert resp.status_code == 302  # redirect status

    with client.application.app_context():
        user = User.query.filter_by(email=email).first()
        assert user.pending_role == expected_pending_role

    # Check flashes in session before redirect happens
    with client.session_transaction() as sess:
        flashes = sess.get('_flashes', [])
    messages = [msg for cat, msg in flashes]
    assert any(flash_message_part in msg for msg in messages)
'''    
'''
def register_and_activate_user(client, email='test@example.com', role='seeker'):
    # Register user
    client.post('/auth/?mode=register', data={
        'email': email,
        'password': 'password123',
        'confirm_password': 'password123',
        'age': '25',
        'gender': 'male',
        'role': role,
        'preference': 'female',
        'age_verify': 'on',
        'form_type': 'register',
        'g-recaptcha-response': 'dummy-token'
    }, follow_redirects=True)
    # Activate user manually
    with client.application.app_context():
        user = User.query.filter_by(email=email).first()
        user.active = True
        user.email_verified = True
        db.session.commit()
'''
'''def test_request_role_change_invalid_role(client):
    email = 'invalid@example.com'
    register_and_activate_user(client, email=email, role='admin')  # invalid role
    login_user(client, email=email)

    resp = client.post('/profile/request-role-change', follow_redirects=False)
    assert resp.status_code == 302  # redirect expected

    with client.application.app_context():
        user = User.query.filter_by(email=email).first()
        # pending_role should NOT be set for invalid role
        assert user.pending_role is None or user.pending_role == '', "pending_role should not be set"

    with client.session_transaction() as sess:
        flashes = sess.get('_flashes', [])
    messages = [msg for category, msg in flashes]
    assert any("Role change not allowed" in msg for msg in messages), "Should flash role change not allowed message"    
    
def test_deactivate_profile(client, app):
    register_user(client)
    login_user(client)

    # Send POST request to deactivate profile route
    resp = client.post('/profile/deactivate', follow_redirects=False)

    # Assert it redirects (usually 302 on success)
    assert resp.status_code == 302

    # Optionally check Location header for redirect URL (e.g. to profile or home)
    assert '/profile' in resp.headers['Location'] or '/' in resp.headers['Location']

    # Verify in the DB that user is deactivated
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.active == False or user.is_active == False  # depends on your model field
        

def test_get_profile_photo(client, app):
    register_user(client)

    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        user.active = True
        user.email_verified = True
        db.session.commit()

    login_user(client)

    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        profile = Profile.query.filter_by(user_id=user.id).first()
        profile.photo = 'http://example.com/myphoto.jpg'
        db.session.commit()
        user_id = user.id  # ✅ store the ID while still in context

    # Now do the request
    resp = client.get('/profile/photo')
    assert resp.status_code == 200
    data = resp.get_json()

    # ✅ compare using stored `user_id`
    assert data['user_id'] == user_id
    assert data['photo_url'] == 'http://example.com/myphoto.jpg'
# end of profile



'''


def register_and_activate_user(client, email, role):
    client.post('/auth/?mode=register', data={
        'email': email,
        'password': 'password123',
        'confirm_password': 'password123',
        'age': '30',
        'gender': 'female' if role == 'escort' else 'male',
        'role': role,
        'preference': 'any',
        'age_verify': 'on',
        'form_type': 'register',
        'g-recaptcha-response': 'dummy-token'
    }, follow_redirects=True)

    with flask_app.app_context():
        user = User.query.filter_by(email=email).first()
        user.active = True
        user.email_verified = True
        db.session.commit()

'''
# Browse.html
def test_browse_escorts_basic(client, app):
    # Register users
    register_and_activate_user(client, 'escort1@example.com', 'escort')
    register_and_activate_user(client, 'seeker1@example.com', 'seeker')

    # Log in as seeker (who browses escorts)
    login_user(client, 'seeker1@example.com')

    with app.app_context():
        escort = User.query.filter_by(email='escort1@example.com').first()
        escort_profile = Profile.query.filter_by(user_id=escort.id).first()
        escort_profile.name = 'escort1'
        escort_profile.age = 28
        escort_profile.rating = 4.5
        db.session.commit()

    resp = client.get('/browse/browse')
    assert resp.status_code == 200
    assert b'escort1' in resp.data

# Browse.html
def test_browse_seekers_basic(client, app):
    # Register users
    register_and_activate_user(client, 'seeker1@example.com', 'seeker')
    register_and_activate_user(client, 'escort1@example.com', 'escort')

    # Log in as escort (who browses seekers)
    login_user(client, 'escort1@example.com')

    with app.app_context():
        seeker = User.query.filter_by(email='seeker1@example.com').first()
        seeker_profile = Profile.query.filter_by(user_id=seeker.id).first()
        seeker_profile.name = 'seeker1'
        seeker_profile.age = 26
        seeker_profile.rating = 4.2
        db.session.commit()

    resp = client.get('/browse/browseSeeker')
    assert resp.status_code == 200
    assert b'seeker1' in resp.data
    
# Browse.html
def test_browse_escorts_with_availability(client, app):
    register_and_activate_user(client, 'escort2@example.com', 'escort')
    register_and_activate_user(client, 'seeker2@example.com', 'seeker')
    login_user(client, 'seeker2@example.com')

    future_start = (datetime.utcnow() + timedelta(days=1)).replace(second=0, microsecond=0)
    future_end = future_start + timedelta(hours=1)

    with app.app_context():
        escort = User.query.filter_by(email='escort2@example.com').first()
        escort.active = True
        escort.deleted = False
        escort_profile = Profile.query.filter_by(user_id=escort.id).first()
        escort_profile.name = 'escort2'
        db.session.add(TimeSlot(user_id=escort.id, start_time=future_start, end_time=future_end))
        db.session.commit()

    url = f"/browse/browse?avail_date={future_start.date()}&avail_time={future_start.strftime('%H:%M')}"
    resp = client.get(url)
    print(resp.data.decode())  # debug
    assert resp.status_code == 200
    assert b'escort2' in resp.data, "escort2 should appear with availability filter"
    
# Browse.html
def test_browse_escorts_with_availability(client, app):
    register_and_activate_user(client, 'escort2@example.com', 'escort')
    register_and_activate_user(client, 'seeker2@example.com', 'seeker')
    login_user(client, 'seeker2@example.com')

    future_start = (datetime.utcnow() + timedelta(days=1)).replace(second=0, microsecond=0)
    future_end = future_start + timedelta(hours=1)


    with app.app_context():
        escort = User.query.filter_by(email='escort2@example.com').first()
        escort.active = True
        escort.deleted = False
        escort_profile = Profile.query.filter_by(user_id=escort.id).first()
        escort_profile.name = 'escort2'
        db.session.add(TimeSlot(user_id=escort.id, start_time=future_start, end_time=future_end))
        db.session.commit()

    # Check if profile appears without availability filter
    resp = client.get('/browse/browse')
    assert resp.status_code == 200
    assert b'escort2' in resp.data, "escort2 should appear without availability filter"

    # Now check with availability filter
    url = f"/browse/browse?avail_date={future_start.date()}&avail_time={future_start.strftime('%H:%M')}"
    resp = client.get(url)
    assert resp.status_code == 200
    assert b'escort2' in resp.data, "escort2 should appear with availability filter"

# Browse.html
def test_browse_escorts_basic_and_filtered(client, app):
    register_and_activate_user(client, 'escort1@example.com', 'escort')
    register_and_activate_user(client, 'escort2@example.com', 'escort')
    register_and_activate_user(client, 'seeker1@example.com', 'seeker')
    login_user(client, 'seeker1@example.com')  # Seeker browsing escorts

    with app.app_context():
        escort1 = User.query.filter_by(email='escort1@example.com').first()
        escort2 = User.query.filter_by(email='escort2@example.com').first()
        profile1 = Profile.query.filter_by(user_id=escort1.id).first()
        profile2 = Profile.query.filter_by(user_id=escort2.id).first()
        profile1.name = 'escort1'
        profile1.age = 25
        profile1.rating = 4.6
        profile2.name = 'escort2'
        profile2.age = 32
        profile2.rating = 3.8
        db.session.commit()

    resp = client.get('/browse/browse')
    assert resp.status_code == 200
    assert b'escort1' in resp.data or b'escort2' in resp.data

# Browse.html
def test_browse_seekers_basic_and_filtered(client, app):
    register_and_activate_user(client, 'seeker1@example.com', 'seeker')
    register_and_activate_user(client, 'seeker2@example.com', 'seeker')
    register_and_activate_user(client, 'escort1@example.com', 'escort')
    login_user(client, 'escort1@example.com')  # Escort browsing seekers

    with app.app_context():
        seeker1 = User.query.filter_by(email='seeker1@example.com').first()
        seeker2 = User.query.filter_by(email='seeker2@example.com').first()
        profile1 = Profile.query.filter_by(user_id=seeker1.id).first()
        profile2 = Profile.query.filter_by(user_id=seeker2.id).first()
        profile1.name = 'seeker1'
        profile1.age = 23
        profile1.rating = 4.2
        profile2.name = 'seeker2'
        profile2.age = 30
        profile2.rating = 3.5
        db.session.commit()

    resp = client.get('/browse/browseSeeker')
    assert resp.status_code == 200
    assert b'seeker1' in resp.data or b'seeker2' in resp.data
'''

'''
# Browse.html
def test_browse_excludes_booked_escorts(client, app):
    register_and_activate_user(client, 'escort3@example.com', 'escort')
    register_and_activate_user(client, 'seeker3@example.com', 'seeker')
    login_user(client, 'seeker3@example.com')

    now = datetime.utcnow() + timedelta(days=1)
    with app.app_context():
        escort = User.query.filter_by(email='escort3@example.com').first()
        db.session.add(TimeSlot(user_id=escort.id, start_time=now, end_time=now + timedelta(hours=1)))
        db.session.add(Booking(escort_id=escort.id, seeker_id=escort.id, start_time=now, end_time=now + timedelta(minutes=30), status='Confirmed'))
        db.session.commit()

    resp = client.get(f"/browse/browse?avail_date={now.date()}&avail_time={now.strftime('%H:%M')}")
    assert b'escort3@example.com' not in resp.data
'''
    
'''
# Browse.html
def test_favourite_toggle_and_render(client, app):
    # Register escort and seeker
    register_and_activate_user(client, 'escort4@example.com', 'escort')
    register_and_activate_user(client, 'seeker4@example.com', 'seeker')
    login_user(client, 'seeker4@example.com')

    with app.app_context():
        escort = User.query.filter_by(email='escort4@example.com').first()
        escort_profile = Profile.query.filter_by(user_id=escort.id).first()
        escort_profile.name = 'escort4'
        db.session.commit()
        escort_id = escort.id  # ✅ STORE ID inside context

    # Add to favourites using the stored ID
    resp = client.post(f"/browse/favourite/{escort_id}")
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'added'

    # Load browse page and verify escort4 is favourited
    resp = client.get('/browse/browse')
    assert resp.status_code == 200
    page = resp.data.decode()
    
    assert 'escort4' in page
    
    # Adjust this to your actual template condition
    assert '♥ Unfavorite' in page or 'btn-danger' in page

'''

'''
# booking.html allow escort to create their availability time slot
def test_create_availability_slot(client, app):
    # Register and activate escort user
    register_and_activate_user(client, 'escort_test@example.com', 'escort')
    login_user(client, 'escort_test@example.com')

    # Prepare future start and end time
    start_time = (datetime.utcnow() + timedelta(days=1)).replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=2)

    # Get CSRF token from GET /booking page (where form lives)
    response = client.get('/booking/')
    assert response.status_code == 200
    # Extract CSRF token from the rendered HTML (simplest with regex)
    import re
    csrf_token = re.search(b'name="csrf_token" value="([^"]+)"', response.data).group(1).decode()

    # Post to create_slot with the form data
    response = client.post('/booking/slots/create', data={
        'start_time': start_time.strftime('%Y-%m-%dT%H:%M'),
        'end_time': end_time.strftime('%Y-%m-%dT%H:%M'),
        'csrf_token': csrf_token,
    }, follow_redirects=True)

    # Check success response
    assert response.status_code == 200
    assert b'Availability slot created.' in response.data

    # Verify availability slot exists in DB
    with app.app_context():
        user = User.query.filter_by(email='escort_test@example.com').first()
        slot = TimeSlot.query.filter_by(user_id=user.id, start_time=start_time, end_time=end_time).first()
        assert slot is not None
'''




'''def test_make_booking_for_available_slot(client, app):
    # Register and activate escort and seeker
    register_and_activate_user(client, 'escort_test@example.com', 'escort')
    register_and_activate_user(client, 'seeker_test@example.com', 'seeker')

    # Escort logs in and creates an availability slot
    login_user(client, 'escort_test@example.com')

    start_time = (datetime.utcnow() + timedelta(days=1)).replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)

    # Get CSRF token from the /booking page (form for escort to create slot)
    response = client.get('/booking/')
    assert response.status_code == 200

    csrf_token = re.search(b'name="csrf_token" value="([^"]+)"', response.data).group(1).decode()

    # Escort creates a time slot
    response = client.post('/booking/slots/create', data={
        'start_time': start_time.strftime('%Y-%m-%dT%H:%M'),
        'end_time': end_time.strftime('%Y-%m-%dT%H:%M'),
        'csrf_token': csrf_token,
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Availability slot created' in response.data

    # Get the escort user_id
    with app.app_context():
        escort = User.query.filter_by(email='escort_test@example.com').first()
        escort_id = escort.id
        slot = TimeSlot.query.filter_by(user_id=escort_id).first()
        assert slot is not None
        slot_id = slot.id


    # Now, seeker logs in
    login_user(client, 'seeker_test@example.com')

    # Pull CSRF token directly from session
    withresponse = client.get('/booking/')
    assert response.status_code == 200
    csrf_token = re.search(b'name="csrf_token" value="([^"]+)"', response.data).group(1).decode()

    # Seeker books the available slot
    response = client.post(f'/booking/book/{escort_id}', data={
        # 'escort_id': escort_id,
        # 'start_time': start_time.strftime('%Y-%m-%dT%H:%M'),
        # 'end_time': end_time.strftime('%Y-%m-%dT%H:%M'),
        # 'csrf_token': csrf_token,
        'slot_id': slot_id,
        'start_time': start_time.strftime('%Y-%m-%d %H:%M'),  # NOTE: not %Y-%m-%dT%H:%M
        'duration': 15,
        'csrf_token': csrf_token,
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Booking request sent successfully' in response.data  # Adjust to your actual success message

    # Verify booking exists in DB
    with app.app_context():
        seeker = User.query.filter_by(email='seeker_test@example.com').first()
        booking = Booking.query.filter_by(
            seeker_id=seeker.id,
            escort_id=escort_id,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=15)  # Must reflect actual booked end time
        ).first()
        assert booking is not None

'''


## TESTING
def test_make_payment_flow(client, app):
    # 1. Register and activate escort and seeker users (implement your helper)
    register_and_activate_user(client, 'escort_test@example.com', 'escort')
    register_and_activate_user(client, 'seeker_test@example.com', 'seeker')

    # 2. Escort logs in and creates a time slot
    login_user(client, 'escort_test@example.com')

    start_time = (datetime.utcnow() + timedelta(days=1)).replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)

    response = client.get('/booking/')
    

    response = client.post('/booking/slots/create', data={
        'start_time': start_time.strftime('%Y-%m-%dT%H:%M'),
        'end_time': end_time.strftime('%Y-%m-%dT%H:%M'),
        # 'csrf_token': csrf_token,
    }, follow_redirects=True)
    print(response.status_code)
    print(response.data.decode())
    assert response.status_code == 200
    assert b'Availability slot created' in response.data

    with app.app_context():
        escort = User.query.filter_by(email='escort_test@example.com').first()
        slot = TimeSlot.query.filter_by(user_id=escort.id).first()
        assert slot is not None
        slot_id = slot.id

    # 3. Seeker logs in and books the slot (creates a booking with status 'Pending')
    login_user(client, 'seeker_test@example.com')
    
    response = client.get('/booking/')
    # csrf_token = re.search(b'name="csrf_token" value="([^"]+)"', response.data).group(1).decode()

    response = client.post(f'/booking/book/{escort.id}', data={
        'slot_id': slot_id,
        'start_time': start_time.strftime('%Y-%m-%d %H:%M'),
        'duration': 60,  # or 15 depending on your booking duration logic
        # 'csrf_token': csrf_token,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Booking request sent successfully' in response.data

    with app.app_context():
        seeker = User.query.filter_by(email='seeker_test@example.com').first()
        booking = Booking.query.filter_by(seeker_id=seeker.id, escort_id=escort.id).first()
        assert booking is not None
        assert booking.status == 'Pending'
        booking_id = booking.id
       
 
	
 	###################
    
 	# Escort logs in and accepts the booking
    login_user(client, 'escort_test@example.com')
    response = client.get('/booking/')
    csrf_token = re.search(b'name="csrf_token" value="([^"]+)"', response.data).group(1).decode()
    response = client.post('/booking/handle', data={
    'booking_id': booking_id,
    'action': 'accept',
    'csrf_token': csrf_token,
    }, follow_redirects=True)
    
    with app.app_context():
        booking = Booking.query.get(booking_id)
        assert booking.status == 'Confirmed'


    assert response.status_code == 200
    assert b'accepted' in response.data


    # 4. Seeker initiates payment (GET /payment/initiate/<booking_id>) - should redirect with token
    login_user(client, 'seeker_test@example.com')
    response = client.get(f'/payment/initiate/{booking_id}', follow_redirects=False)
    # Expect redirect to payment page with token in query param
    assert response.status_code == 302
    location = response.headers['Location']
    assert '/payment/pay' in location
    token = re.search(r'token=([^&]+)', location).group(1)

    # 5. GET payment page with token
    response = client.get(f'/payment/pay?token={token}')
    assert response.status_code == 200
    assert b'Payment' in response.data  # Check page content for payment form

    # 6. POST payment with valid card details
    # Extract CSRF token from form for POST

    response = client.post('/payment/pay', data={
        'token': token,
        # 'csrf_token': csrf_token,
        'card_number': '4242424242424242',
        'expiry': '12/30',
        'cvv': '123',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Payment successful' in response.data

    # 7. Verify payment record and booking status updated
    with app.app_context():
        payment = Payment.query.filter_by(booking_id=booking_id).first()
        assert payment is not None
        assert payment.status == 'Completed'
        booking = Booking.query.get(booking_id)
        assert booking.status == 'Confirmed'
	
	# seeker post rating
 
	# seeker see
    login_user(client, 'seeker_test@example.com')
    response = client.get('/rating/rateable-bookings')
    
    assert response.status_code == 200
    assert b'Rate Your Completed Bookings' in response.data or b'No Bookings to Rate' in response.data
    
	#seeker post
    response = client.post(f'rating/submit', json={
        'booking_id': booking_id,  # Include the actual booking ID
        'rating': 5,
        'feedback': 'Excellent experience!',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Rating submitted successfully' in response.data

    # Seeker views their ratings and sees the new rating
    with app.app_context():
        rating = Rating.query.filter_by(booking_id=booking_id, rating=5).first()
        assert rating is not None
        assert rating.feedback == "Excellent experience!"



## not done below
# stopped        

# # --- Rating Tests ---

# def test_submit_rating_and_view(client):
