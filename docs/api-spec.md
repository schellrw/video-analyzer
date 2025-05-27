# Video Analyzer API Specification

## Base URL
- Development: `http://localhost:5000/api`
- Production: `https://api.videoanalyzer.tech/api`

## Authentication
All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Response Format
All API responses follow this structure:
```json
{
  "success": boolean,
  "data": object | array | null,
  "message": string,
  "errors": array | null,
  "timestamp": string,
  "meta": {
    "pagination": object | null,
    "total": number | null
  }
}
```

## Endpoints

### Authentication

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "string",
  "password": "string",
  "firstName": "string",
  "lastName": "string",
  "organization": "string",
  "role": "attorney" | "investigator" | "admin"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "string",
      "firstName": "string",
      "lastName": "string",
      "organization": "string",
      "role": "string"
    },
    "token": "jwt_string"
  }
}
```

#### POST /api/auth/login
Authenticate user and return JWT token.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

#### POST /api/auth/refresh
Refresh JWT token.

#### POST /api/auth/logout
Logout user and invalidate token.

### Cases

#### GET /api/cases
List all cases for the authenticated user.

**Query Parameters:**
- `page`: number (default: 1)
- `limit`: number (default: 20)
- `status`: string (pending, analyzing, completed, archived)
- `search`: string

#### POST /api/cases
Create a new case.

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "incidentDate": "ISO string",
  "location": "string",
  "tags": ["string"]
}
```

#### GET /api/cases/{caseId}
Get case details by ID.

#### PUT /api/cases/{caseId}
Update case information.

#### DELETE /api/cases/{caseId}
Delete a case and all associated data.

### Video Files

#### POST /api/cases/{caseId}/videos
Upload video file to a case.

**Request:** Multipart form data
- `file`: video file
- `metadata`: JSON string with additional info

**Response:**
```json
{
  "success": true,
  "data": {
    "video": {
      "id": "uuid",
      "filename": "string",
      "size": number,
      "duration": number,
      "format": "string",
      "uploadUrl": "string",
      "status": "uploading"
    }
  }
}
```

#### GET /api/cases/{caseId}/videos
List all videos in a case.

#### GET /api/videos/{videoId}
Get video details and metadata.

#### POST /api/videos/{videoId}/analyze
Start AI analysis of a video.

**Request Body:**
```json
{
  "analysisTypes": ["transcription", "violation_detection", "sentiment_analysis"],
  "priority": "low" | "normal" | "high"
}
```

#### GET /api/videos/{videoId}/analysis
Get analysis results for a video.

### Analysis Results

#### GET /api/analysis/{analysisId}
Get specific analysis results.

#### PUT /api/analysis/{analysisId}/review
Submit human review of AI analysis.

**Request Body:**
```json
{
  "verified": boolean,
  "corrections": {
    "transcription": "string",
    "violations": ["string"],
    "notes": "string"
  }
}
```

### Reports

#### POST /api/cases/{caseId}/reports
Generate legal report for a case.

**Request Body:**
```json
{
  "template": "standard" | "detailed" | "summary",
  "includeEvidence": boolean,
  "customSections": ["string"]
}
```

#### GET /api/reports/{reportId}
Get generated report.

#### GET /api/reports/{reportId}/download
Download report as PDF.

### Administration

#### GET /api/admin/users
List all users (admin only).

#### PUT /api/admin/users/{userId}
Update user permissions (admin only).

#### GET /api/admin/analytics
Get platform analytics (admin only).

## Webhooks

### Video Processing Complete
Sent when video analysis is finished.

**Payload:**
```json
{
  "event": "video.analysis.complete",
  "videoId": "uuid",
  "caseId": "uuid",
  "analysisResults": {
    "transcription": "string",
    "violations": ["string"],
    "confidence": number
  }
}
```

## Error Codes

- `400` - Bad Request: Invalid request data
- `401` - Unauthorized: Missing or invalid authentication
- `403` - Forbidden: Insufficient permissions
- `404` - Not Found: Resource not found
- `409` - Conflict: Resource already exists
- `422` - Unprocessable Entity: Validation errors
- `429` - Too Many Requests: Rate limit exceeded
- `500` - Internal Server Error: Server error
- `503` - Service Unavailable: AI service unavailable

## Rate Limiting
- Authentication endpoints: 5 requests per minute
- File upload endpoints: 10 requests per hour
- Analysis endpoints: 50 requests per hour
- General API: 1000 requests per hour

## File Size Limits
- Video files: 2GB maximum
- Document uploads: 50MB maximum
- Image files: 10MB maximum 