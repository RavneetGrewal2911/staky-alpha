"""
Staky AI - Audio Transcription & Summarization Service

This module defines the Flask application and all routes for handling
audio transcription, user authentication, and data management for Staky AI.

The application can run in two modes:
1. Authenticated mode (with Supabase database)
2. Local-only mode (without authentication or history saving)

Staky AI transforms audio into actionable insights with AI-powered
transcription and summarization, saving hours of manual work.

Dependencies:
- Flask for web framework
- Groq for AI model access
- Supabase for database storage
- Python-dotenv for environment variable management
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from groq import Groq
import markdown
from dotenv import load_dotenv
import os
import datetime
from functools import wraps

# Load environment variables from .env file
# This includes API keys and configuration settings
load_dotenv()

# Initialize the Groq client
# Groq API is used for both transcription and summarization
client = Groq(api_key=os.getenv('API_KEY'))

# Initialize Flask app
app = Flask(__name__)
# Secret key for session management and CSRF protection

# 50MB limit for file uploads - adjust as needed for larger audio files
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  

# Create uploads folder if it doesn't exist
# This folder is used for temporary storage of audio files
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Import database connection after app initialization
# This prevents circular import issues
from database import supabase_client , create_tables

# Print table creation instructions and verify database setup
create_tables()

# Set database_available flag - we'll use this to conditionally enable/disable features
# The application can work in local-only mode without authentication if the database
# is not configured, providing a fallback for users who don't have Supabase set up
database_available = True
try:
    # Try to access a table to see if the database is configured
    supabase_client.table('users').select('count', count='exact').limit(1).execute()
except Exception as e:
    database_available = False
    print(f"WARNING: Database not available: {e}")
    print("Running in local-only mode (no authentication or history saving)")
    print("Follow the instructions above to set up Supabase tables")

# Login required decorator for protected routes
# This decorator ensures users are authenticated before accessing protected pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    """
    Landing page route
    Displays the main welcome page with introduction to the service
    """
    return render_template('index.html')

@app.route("/pricing")
def pricing():
    """
    Pricing page route
    Displays the pricing plans and subscription information
    """
    return render_template('pricing.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    User registration route
    Handles both the registration form display (GET) and form submission (POST)
    Creates new user accounts in Supabase Auth and the users table
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        try:
            # Register user with Supabase Auth
            # This creates the authentication record
            auth_response = supabase_client.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            # Create a user record in our custom table
            # This stores additional user information like name
            user_id = auth_response.user.id
            supabase_client.table('users').insert({
                "id": user_id,
                "name": name,
                "email": email,
                "created_at": datetime.datetime.now().isoformat(),
                "usage_count": 0,
                "is_admin": False
            }).execute()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    User login route
    Handles both login form display (GET) and form submission (POST)
    Authenticates users through Supabase and sets up session data
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Sign in user with Supabase Auth
            # Handles authentication and password validation
            auth_response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Set session data for the authenticated user
            # This maintains the user's logged-in state
            user_id = auth_response.user.id
            session['user_id'] = user_id
            session['email'] = email
            
            # Get user details from our database
            # Retrieve additional user information from the users table
            user_data = supabase_client.table('users').select('name, usage_count, is_admin').eq('id', user_id).execute()
            if user_data.data:
                session['name'] = user_data.data[0].get('name', '')
                session['usage_count'] = user_data.data[0].get('usage_count', 0)
                session['is_admin'] = user_data.data[0].get('is_admin', False)
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'danger')
    
    return render_template('login.html')

@app.route("/logout")
def logout():
    """
    User logout route
    Signs out user from Supabase Auth and clears session data
    """
    try:
        # Sign out from Supabase Auth
        # This invalidates the authentication token
        supabase_client.auth.sign_out()
    except:
        # If Supabase signout fails, we'll still clear the session
        pass
    
    # Clear session data to complete the logout process
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route("/dashboard")
@login_required
def dashboard():
    """
    User dashboard route
    Shows user's previously saved transcriptions
    Protected by login_required decorator
    """
    # Get user's previous transcriptions from the database
    try:
        user_id = session['user_id']
        # Query the transcriptions table for this user's records
        # Order by creation date (newest first)
        transcriptions = supabase_client.table('transcriptions').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return render_template('dashboard.html', transcriptions=transcriptions.data)
    except Exception as e:
        flash(f'Error retrieving your transcriptions: {str(e)}', 'danger')
        # If database query fails, render an empty dashboard
        return render_template('dashboard.html', transcriptions=[])

@app.route("/workshop")
def workshop():
    """
    Main transcription workshop route
    Shows the interface for uploading or recording audio
    Only requires login if the database is available
    """
    # Only require login if database is available
    if database_available and 'user_id' not in session:
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('login'))
    return render_template('workshop.html')

@app.route("/file_upload", methods=['POST'])
def file_upload():
    """
    File upload and processing route
    Handles audio file uploads or browser recordings
    Processes audio files through Groq API for transcription and summarization
    Saves results to database if available and user is logged in
    
    Free trial users are limited to 1 transcription before being prompted to upgrade
    Admin users have unlimited transcriptions
    """
    # Only require login if database is available
    if database_available and 'user_id' not in session:
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('login'))
    
    # Check usage limits if database is available and user is logged in
    if database_available and 'user_id' in session:
        # Skip usage check for admin users
        is_admin = session.get('is_admin', False)
        if not is_admin:
            # Get current usage count from session
            usage_count = session.get('usage_count', 0)
            
            # If user has already used their free trial, redirect to pricing
            if usage_count >= 1:
                flash('You have used your free trial. Please upgrade to continue using Staky AI.', 'warning')
                return redirect(url_for('pricing'))
    
    try:
        # Handle both file uploads and browser recordings
        # Two input methods are supported: traditional file upload and in-browser recording
        if 'file' in request.files:
            # Regular file upload from device
            file = request.files['file']
            
            if not file:
                flash('No file selected', 'danger')
                return redirect(url_for('workshop'))
            
            filename = file.filename
            file_content = file.read()
            
        elif 'recorded_audio' in request.form:
            # Browser recording (base64 encoded)
            # This allows users to record audio directly in the browser
            import base64
            
            # Get base64 data and convert to bytes for processing
            base64_audio = request.form['recorded_audio']
            file_content = base64.b64decode(base64_audio)
            filename = request.form.get('recorded_filename', 'browser-recording.wav')
            
        else:
            flash('No audio data provided', 'danger')
            return redirect(url_for('workshop'))
        
        # Save the file temporarily for processing
        # Using a timestamped filename to avoid collisions
        temp_path = os.path.join('uploads', f"temp_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}")
        with open(temp_path, 'wb') as f:
            f.write(file_content)
        
        # Create a transcription of the audio file using Groq/Whisper
        with open(temp_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(filename, audio_file),
                model="whisper-large-v3-turbo"
            )
        
        # Clean up the temp file after processing
        try:
            os.remove(temp_path)
        except:
            # Non-critical failure, we can continue even if cleanup fails
            pass
            
        # Generate summary with Groq LLM
        # Using llama3-70b model to analyze and summarize the transcription
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "summarize the given data in in a well arranged manner. use headings and subheadings without overdoing it and make sure they are the best posible way to summarize the given data. do not use hr elements. do not include any message from your side. you are dealing with important data so make sure that you dont miss any inportant details in it.give your answer in markdown format ",
                },
                {
                    "role": "user",
                    "content": transcription.text,
                }
            ],
            model="llama3-70b-8192",
        )
        
        result = chat_completion.choices[0].message.content
        
        # Save transcription to database and update usage count if available and user is logged in
        if database_available and 'user_id' in session:
            try:
                user_id = session['user_id']
                is_admin = session.get('is_admin', False)
                
                # Save the transcription to the database
                transcription_data = {
                    "user_id": user_id,
                    "filename": filename,
                    "raw_transcription": transcription.text,
                    "summary": result,
                    "created_at": datetime.datetime.now().isoformat()
                }
                supabase_client.table('transcriptions').insert(transcription_data).execute()
                
                # Update usage count for non-admin users
                if not is_admin:
                    # Get current usage count
                    current_usage = session.get('usage_count', 0)
                    new_usage = current_usage + 1
                    
                    # Update in database
                    supabase_client.table('users').update({"usage_count": new_usage}).eq('id', user_id).execute()
                    
                    # Update in session
                    session['usage_count'] = new_usage
                    
            except Exception as db_error:
                print(f"Warning: Could not save to database or update usage: {db_error}")
                # Continue anyway - we'll still show the result to the user
                # This ensures core functionality even if database saving fails
        
        # Render result page with both the summary and raw transcription
        # The summary is rendered as markdown for better formatting
        return render_template('result.html', result=markdown.markdown(result), raw_text=transcription.text)
    
    except Exception as e:
        # Comprehensive error handling to improve user experience
        error_message = str(e)
        flash(f'Error processing file: {error_message}', 'danger')
        print(f"Error in file_upload: {error_message}")
        return redirect(url_for('workshop'))

@app.route("/transcription/<id>")
@login_required
def view_transcription(id):
    """
    View a single saved transcription
    Retrieves a specific transcription from the database
    Ensures users can only view their own transcriptions
    """
    try:
        user_id = session['user_id']
        
        # Get transcription from database with security check
        # The user_id filter ensures users can only access their own data
        transcription = supabase_client.table('transcriptions').select('*').eq('id', id).eq('user_id', user_id).execute()
        
        if not transcription.data:
            flash('Transcription not found or access denied', 'danger')
            return redirect(url_for('dashboard'))
        
        # Render the same result template used for new transcriptions
        # This provides a consistent user experience
        return render_template('result.html', 
                             result=markdown.markdown(transcription.data[0]['summary']), 
                             raw_text=transcription.data[0]['raw_transcription'])
    
    except Exception as e:
        flash(f'Error retrieving transcription: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/profile")
@login_required
def profile():
    """
    User profile page
    Shows user information and allows editing name
    Protected by login_required decorator
    """
    return render_template('profile.html')

@app.route("/update_profile", methods=['POST'])
@login_required
def update_profile():
    """
    Update user profile information
    Currently supports updating the user's name
    Updates both the database record and the session data
    """
    try:
        user_id = session['user_id']
        name = request.form.get('name')
        
        # Update user record in database
        supabase_client.table('users').update({"name": name}).eq('id', user_id).execute()
        
        # Update session data to reflect the changes immediately
        session['name'] = name
        
        flash('Profile updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'danger')
    
    return redirect(url_for('profile'))

@app.route("/admin")
@login_required
def admin_panel():
    """
    Admin panel for managing users
    Only accessible to admin users
    """
    # Check if user is an admin
    if not session.get('is_admin', False):
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Get all users from the database
        users = supabase_client.table('users').select('*').execute()
        return render_template('admin.html', users=users.data)
    except Exception as e:
        flash(f'Error retrieving user data: {str(e)}', 'danger')
        return render_template('admin.html', users=[])

@app.route("/admin/toggle_admin/<user_id>", methods=['POST'])
@login_required
def toggle_admin_status(user_id):
    """
    Toggle admin status for a user
    Only accessible to admin users
    """
    # Check if user is an admin
    if not session.get('is_admin', False):
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Get current admin status
        user_data = supabase_client.table('users').select('is_admin').eq('id', user_id).execute()
        
        if not user_data.data:
            flash('User not found', 'danger')
            return redirect(url_for('admin_panel'))
        
        current_status = user_data.data[0].get('is_admin', False)
        new_status = not current_status
        
        # Update admin status
        supabase_client.table('users').update({"is_admin": new_status}).eq('id', user_id).execute()
        
        # Update session if the user is updating their own status
        if user_id == session.get('user_id'):
            session['is_admin'] = new_status
        
        flash(f'Admin status updated successfully. User is {"now" if new_status else "no longer"} an admin.', 'success')
    except Exception as e:
        flash(f'Error updating admin status: {str(e)}', 'danger')
    
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
