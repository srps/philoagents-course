# Philoagents Multiplayer Implementation

This document describes the implementation of session management and thread isolation to enable multiple users to simultaneously interact with the philoagents application without interference.

## Overview

The multiplayer functionality ensures that each user has their own private conversation history with the philosophers, while maintaining the existing functionality for individual users.

## Key Components

### 1. Session Management System

**Location**: `philoagents-api/src/philoagents/application/session_service/`

- **SessionManager**: Manages user sessions with unique identifiers
- **UserSession**: Represents individual user sessions with metadata
- **Features**:
  - Automatic session creation with UUID
  - Session expiration handling (60 minutes default)
  - Background cleanup of expired sessions
  - Thread ID generation using composite keys

### 2. Database Schema Updates

**Thread ID Format**: `user_id:philosopher_id`

- **Before**: `thread_id = philosopher_id`
- **After**: `thread_id = f"{user_id}:{philosopher_id}"`

This ensures complete isolation between users while maintaining conversation continuity for each user-philosopher pair.

### 3. API Modifications

#### New Endpoints

- `POST /session` - Create a new user session
- Enhanced `POST /reset-memory` - Reset conversations for specific user

#### Updated Endpoints

- `POST /chat` - Now accepts optional `user_id` parameter
- `WebSocket /ws/chat` - Now handles `user_id` in message payload

### 4. Frontend Integration

**Location**: `philoagents-ui/src/services/`

- **SessionService**: Manages client-side session state
- **Features**:
  - Automatic session creation on app start
  - Session persistence in localStorage
  - Session validation and refresh
  - Integration with API and WebSocket services

## Usage

### For Users

1. **Automatic Session Creation**: Sessions are created automatically when users start the application
2. **Session Persistence**: Sessions persist across browser refreshes for 24 hours
3. **Visual Indicator**: Session ID is displayed in the main menu (first 8 characters)
4. **Private Conversations**: Each user has completely isolated conversation history

### For Developers

#### Testing Multiplayer Functionality

Run the test script to verify multiplayer isolation:

```bash
python test_multiplayer.py
```

This script tests:

- Single user conversations
- Multiple users with same philosopher
- Conversation reset functionality
- Concurrent conversations

#### API Usage Examples

**Create Session**:

```javascript
const response = await fetch('/session', { method: 'POST' });
const session = await response.json();
// Returns: { user_id: "uuid", created_at: "timestamp", message: "..." }
```

**Send Message with Session**:

```javascript
const response = await fetch('/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Hello!",
    philosopher_id: "socrates",
    user_id: session.user_id
  })
});
```

**Reset User Conversations**:

```javascript
const response = await fetch('/reset-memory', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: session.user_id })
});
```

## Implementation Details

### Thread Isolation

1. **Composite Thread IDs**: Each conversation thread uses `user_id:philosopher_id` format
2. **MongoDB Storage**: Conversations are stored with user-specific thread IDs
3. **Automatic Cleanup**: Session manager handles expired session cleanup

### Session Lifecycle

1. **Creation**: New UUID generated for each user
2. **Persistence**: Stored in localStorage and server-side memory
3. **Validation**: Checked for expiration (24 hours client-side, 60 minutes server-side)
4. **Cleanup**: Automatic removal of expired sessions

### Error Handling

- **Fallback Sessions**: If server session creation fails, client creates temporary UUID
- **Session Recovery**: Automatic session refresh on expiration
- **Graceful Degradation**: Application works even if session service is unavailable

## Benefits

1. **True Multiplayer**: Multiple users can demo the application simultaneously
2. **Privacy**: Each user's conversations are completely isolated
3. **Scalability**: Session management scales with user count
4. **Backwards Compatibility**: Existing functionality preserved
5. **Easy Deployment**: No additional infrastructure required

## Configuration

### Session Timeout

Server-side timeout can be configured in `SessionManager`:

```python
session_manager = SessionManager(session_timeout_minutes=60)
```

Client-side timeout is set to 24 hours in `SessionService`.

### MongoDB Collections

The system uses existing MongoDB collections with enhanced thread ID format:

- `philosopher_state_checkpoints`
- `philosopher_state_writes`

## Monitoring

### Logs

Session activities are logged with user IDs:
```
Created new session for user: abc123...
Invalidated session for user: abc123...
Cleaned up 5 expired sessions
```

### Session Count

Get active session count:

```python
count = session_manager.get_active_session_count()
```

## Future Enhancements

1. **Persistent Sessions**: Store sessions in database for cross-device continuity
2. **User Profiles**: Add user names and preferences
3. **Conversation Sharing**: Allow users to share interesting conversations
4. **Analytics**: Track user engagement and conversation patterns
5. **Rate Limiting**: Implement per-user rate limiting for API calls
