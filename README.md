# Staky AI - Audio Transcription & Summarization Service

A Flask-based SaaS application that uses AI to transcribe and summarize audio files, with a freemium business model.

## Features

- **Audio Transcription**: Convert spoken audio to text using Groq's Whisper model
- **AI Summarization**: Generate well-structured summaries using Groq's LLM (llama3-70b)
- **Multiple Input Methods**: Upload audio files or record directly in the browser
- **User Authentication**: Secure login and registration through Supabase
- **Transcription History**: Save and view past transcriptions (when logged in)
- **Responsive Design**: Mobile-friendly interface built with Bootstrap
- **Dual-Mode Operation**: Works with or without database connectivity
- **Freemium Model**: One free transcription per user with premium plans
- **Admin Panel**: Manage users and assign admin privileges

## Tech Stack

- **Backend**: Python/Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: PostgreSQL via Supabase
- **AI Services**: Groq API (for transcription and summarization)
- **Authentication**: Supabase Auth

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL database (or Supabase account)
- Groq API key

### Environment Variables

The application requires the following environment variables:

```
# Groq API key
GROQ_API_KEY=your-groq-api-key

# For database connection
DATABASE_URL=postgresql://username:password@host:port/database
# Or when using Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-service-key

# For session management
FLASK_SECRET_KEY=your-secret-key
```

### Installation

1. Clone the repository

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables (see above)

4. Create database tables (see database_schema.md for details)

5. Run the application:
   ```
   python main.py
   ```

The application will be available at http://localhost:5000

## Usage

### Uploading Audio

1. Navigate to the Workshop page
2. Select the "Upload Audio File" tab
3. Choose an audio file from your device
4. Click "Process Audio"
5. View the transcription and summary on the results page

### Recording Audio

1. Navigate to the Workshop page
2. Select the "Record Audio" tab
3. Click the red microphone button to start recording
4. Click the stop button when finished
5. Preview your recording
6. Click "Use This Recording" to process it
7. View the transcription and summary on the results page

### User Dashboard

When logged in, users can access their dashboard to view past transcriptions and summaries.

### Freemium Model

The application implements a freemium business model:

1. **Free Trial**: Each registered user gets one free transcription
2. **Usage Tracking**: The system tracks how many transcriptions each user has processed
3. **Upgrade Prompt**: After using their free trial, users are directed to the pricing page
4. **Admin Access**: Admin users have unlimited transcription capabilities

### Admin Panel

Admin users can access an admin panel with these features:

1. **User Management**: View all registered users and their usage statistics
2. **Admin Privileges**: Grant or revoke admin status for any user
3. **Unlimited Usage**: Admin accounts bypass the one-transcription limit

See `admin_setup_guide.md` for detailed information on setting up and managing admin accounts.

## Database Setup

The application requires two main tables:

1. `users` - Stores user account information
2. `transcriptions` - Stores transcription history

See `database_schema.md` for detailed information on the database schema.

## Deployment

The application is ready for deployment on any platform that supports Python/Flask applications.

### Deployment Options

- Replit: Ready to deploy with minimal configuration
- Heroku: Supports Flask applications and PostgreSQL databases
- AWS, GCP, Azure: For more scalable deployments

## Developer Notes

- The application can run in "local-only mode" without database integration
- Comprehensive error handling for both database and API failures
- Browser recording feature uses the MediaRecorder API

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Groq API for providing high-quality AI models
- Supabase for authentication and database functionality