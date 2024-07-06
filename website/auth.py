#auth.py
from flask import Blueprint, render_template, request, flash, url_for, redirect, current_app
from . import db,mail
from .models import User , OAuthToken
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer,SignatureExpired, BadSignature
from flask_mail import Message
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import os
auth = Blueprint("auth", __name__)




#------------------------------------------------------------------------------------------------------------
def encrypt_token(token):
    key = os.getenv('ENCRYPTION_KEY')
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token):
    key = os.getenv('ENCRYPTION_KEY')
    f = Fernet(key)
    return f.decrypt(encrypted_token.encode()).decode()

#--------------------------------------------------------------------Oauth----------------------------------------------------
@auth.route("/login/google")
def login_with_google():
    oauth = current_app.config['oauth']
    redirect_uri = url_for('auth.authorize_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth.route("/authorize/google")
def authorize_google():
    oauth = current_app.config['oauth']
    try:
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.parse_id_token(token, nonce=None)
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            new_user = User(
                email=user_info['email'],
                username=user_info['email'].split("@")[0],
                university=user_info['email'],
                password=generate_password_hash('password1'),
                image_url=user_info['picture']
            )
            db.session.add(new_user)
            db.session.commit()
            user = new_user
        
        oauth_token = OAuthToken(
            user_id=user.id,
            provider='google',
            access_token=encrypt_token(token['access_token']),
            refresh_token=encrypt_token(token.get('refresh_token', '')) if token.get('refresh_token') else None,
            token_expiry=datetime.now() + timedelta(seconds=token['expires_in'])
        )
        db.session.add(oauth_token)
        db.session.commit()
        login_user(user)
        return redirect(url_for('views.home'))
    except Exception as e:
        current_app.logger.error(f"OAuth google Error: {e}")
        flash("An error occurred while logging in with Google.", category='error')
        return redirect(url_for('auth.login'))


# @auth.route("/login/linkedin")
# def login_with_linkedin():
#     oauth = current_app.config['oauth']
#     redirect_uri = url_for('auth.authorize_linkedin', _external=True)
#     return oauth.linkedin.authorize_redirect(redirect_uri,scope='profile email')


# @auth.route("/authorize/linkedin")
# def authorize_linkedin():
#     oauth = current_app.config['oauth']
#     print(vars(oauth))
#     try:
#         token = oauth.linkedin.authorize_access_token()
#         print(token)
#         user_info = oauth.linkedin.get('me').json()
#         email_info = oauth.linkedin.get('emailAddress?q=members&projection=(elements*(handle~))').json()
#         print(email_info)
#         print(user_info)
#         email = email_info['elements'][0]['handle~']['emailAddress']
#         user = User.query.filter_by(email=email).first()
#         if not user:
#             username = user_info['email'].split("@")[0],
#             new_user = User(
#                 email=email,
#                 username=username,
#                 university='your university or institute name',
#                 password=generate_password_hash('password1'),
#                 image_url=user_info.get('picture'),
#             )
#             db.session.add(new_user)
#             db.session.commit()
#             user = new_user
        
#         oauth_token = OAuthToken(
#             user_id=user.id,
#             provider='linkedin',
#             access_token=encrypt_token(token['access_token']),
#             refresh_token=encrypt_token(token.get('refresh_token', '')) if token.get('refresh_token') else None,
#             token_expiry=datetime.now() + timedelta(seconds=token['expires_in'])
#         )
#         db.session.add(oauth_token)
#         db.session.commit()
#         login_user(user)
#         return redirect(url_for('views.home'))
#     except Exception as e:
#         current_app.logger.error(f"OAuth linkedin Error: {e}")
#         flash("An error occurred while logging in with LinkedIn.", category='error')
#         return redirect(url_for('auth.login'))




#----------------------------------------------login-----------------------------------------------------


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
     
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            if user.verified:  
                flash("Logged in successfully", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Email not verified. Please check your email for the verification link.", category='error')
        else:
            flash("Incorrect email or password", category='error')

    return render_template("login.html")







#-----------------------------------------------------------signup-----------------------------------------------

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        university = request.form.get("university")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if not username or len(username) < 2:
            flash('Username is too short.', category='error')
        elif not password1 or len(password1) < 8:
            flash('Password is too short.', category='error')
        elif not email or len(email) < 5:
            flash('Email is invalid.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        else:
            email_exists = User.query.filter_by(email=email).first()
            username_exists = User.query.filter_by(username=username).first()
            if email_exists:
                flash('Email is already in use.', category='error')
            elif username_exists:
                flash('Username is already taken.', category='error')
            else:
                hashed_password = generate_password_hash(password1)
                new_user = User(email=email, username=username, password=hashed_password, university=university)

                
                ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
                verification_token = ts.dumps(email, salt=os.getenv('EMAIL_CONFIRM_SALT'))

                
                msg = Message('Confirm Your Email', recipients=[email])
                verification_link = url_for('auth.verify_email', token=verification_token, _external=True)
                msg.body = f"Click the link to verify your email: {verification_link}"
                mail.send(msg)

                
                db.session.add(new_user)
                db.session.commit()

                flash('Account created successfully! Please check your email for verification instructions.', category='success')
                return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)

@auth.route("/verify_email/<token>")
def verify_email(token):
    try:
        ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        email = ts.loads(token, salt=os.getenv('EMAIL_CONFIRM_SALT'), max_age=86400)  
        user = User.query.filter_by(email=email).first()
        if user:
            user.verified = True
            db.session.commit()
            flash('Email verified successfully! You can now log in.', category='success')
        else:
            flash('Invalid verification link.', category='error')
    except:
        flash('Invalid or expired verification link.', category='error')

    return redirect(url_for('auth.login'))



#-------------------------------------------------------------------logout--------------------------------------

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))

#-----------------------------------------------------------Password recovery--------------------------------------

@auth.route("/forgot-password", methods=["GET", "POST"])
def recover_password():
    if request.method == 'POST':
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
            token = ts.dumps(email, salt=os.getenv('RECOVER_KEY_SALT'))

            msg = Message('Password Reset Request', recipients=[email])
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            msg.body = f"Click the link to reset your password: {reset_link}"
            mail.send(msg)

            flash('A password reset link has been sent to your email.', category='success')
        else:
            flash('Email not found.', category='error')
    return render_template("forgot-password.html")


#-----------------------------------------reset password---------------------------
@auth.route("/reset-password", methods=["GET", "POST"], endpoint="auth_reset_password")
@login_required
def user_reset_password():
    if request.method == 'POST':
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 8:
            flash('Password is too short.', category='error')
        else:
            user = User.query.get(current_user.id)
            if user:
                user.password = generate_password_hash(password1)
                db.session.commit()
                flash('Your password has been updated!', category='success')
                return redirect("/edit_profile")

    return render_template("reset-password.html" , page = "Reset")



@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        email = ts.loads(token, salt=os.getenv('RECOVER_KEY_SALT'), max_age=60)           # Token expires in 1 hour (3600 seconds)
    except (SignatureExpired, BadSignature):
        flash('The reset link is invalid or has expired.', category='error')
        return redirect(url_for('auth.recover_password'))

    if request.method == 'POST':
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 8:
            flash('Password is too short.', category='error')
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                user.password = generate_password_hash(password1)
                db.session.commit()
                flash('Your password has been updated!', category='success')
                return redirect(url_for('auth.login'))

    return render_template("reset-password.html" , page = "Recovery")



