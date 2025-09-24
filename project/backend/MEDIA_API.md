# Media Storage API Documentation

## Overview
This API provides per-user media storage functionality using Cloudflare R2 for file storage and PostgreSQL for metadata management.

## Configuration

### Environment Variables
Add these to your `.env` file:

```env
# PostgreSQL Database
DB_NAME=afrikaidb
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Cloudflare R2 Storage (optional)
USE_R2_STORAGE=False  # Set to True to enable R2
R2_ACCESS_KEY_ID=your-r2-access-key-id
R2_SECRET_ACCESS_KEY=your-r2-secret-access-key
R2_BUCKET_NAME=your-r2-bucket-name
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_CUSTOM_DOMAIN=your-custom-domain.com  # optional

# User Storage Quota
DEFAULT_USER_STORAGE_QUOTA=100  # MB per user
```

### Installation
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py create_user_profiles  # For existing users
```

## API Endpoints

### User Profile Management
- `GET /api/user-profile/` - Get current user's profile and storage info
- `PATCH /api/user-profile/{id}/` - Update storage quota (admin only)

### Media File Management
- `GET /api/media-files/` - List user's media files
- `GET /api/media-files/{id}/` - Get specific media file details
- `DELETE /api/media-files/{id}/` - Delete media file
- `POST /api/media-files/generate-pdf/` - Generate PDF report
- `POST /api/media-files/generate-podcast/` - Generate podcast

### Generate PDF Report
```http
POST /api/media-files/generate-pdf/
Content-Type: application/json
Authorization: Token your-auth-token

{
  "countries": ["Morocco", "Algeria"],
  "risks": ["climate", "economic"],
  "year": 2025,
  "title": "North Africa Climate Report",
  "description": "Climate and economic risks analysis",
  "tags": ["climate", "economic", "north-africa"]
}
```

Response:
```json
{
  "id": "uuid-here",
  "owner_username": "john_doe",
  "file_type": "pdf",
  "file_size": 2048576,
  "file_size_mb": 2.0,
  "original_filename": "report_uuid.pdf",
  "title": "North Africa Climate Report",
  "description": "Climate and economic risks analysis",
  "countries": ["Morocco", "Algeria"],
  "risk_categories": ["climate", "economic"],
  "year": 2025,
  "status": "completed",
  "download_url": "https://presigned-url-here",
  "generated_at": "2025-09-24T12:00:00Z"
}
```

### Generate Podcast
```http
POST /api/media-files/generate-podcast/
Content-Type: application/json
Authorization: Token your-auth-token

{
  "countries": ["Kenya"],
  "risks": ["water", "food"],
  "year": 2025,
  "title": "Kenya Water Crisis Podcast",
  "description": "Analysis of water and food security in Kenya",
  "tags": ["water", "food", "kenya"],
  "tone": "serious"
}
```

## Storage Quotas
- Each user has a storage quota (default: 100MB)
- Files count against the quota when successfully uploaded
- Quota exceeded returns HTTP 413 with quota details
- Admins can adjust quotas via user profiles

## File Storage
- Local storage: Files saved to `media/users/{user_id}/`
- R2 storage: Files uploaded to Cloudflare R2 bucket
- Presigned URLs provided for secure access
- Files automatically cleaned up on deletion

## Authentication
All endpoints except legacy ones require authentication:
- Token Authentication: `Authorization: Token your-token`
- Session Authentication: For web browsers

## Error Handling
- 400: Bad request (validation errors)
- 401: Authentication required
- 403: Permission denied
- 413: Storage quota exceeded
- 500: Server error during generation

## Legacy Endpoints (Backward Compatibility)
- `POST /api/report/generate` - Generate report (no auth required)
- `POST /api/podcast/generate` - Generate podcast (no auth required)

These save files to shared media folders without user association.