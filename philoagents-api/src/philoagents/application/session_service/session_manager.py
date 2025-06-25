import uuid
from typing import Optional
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
import asyncio
from loguru import logger


@dataclass
class UserSession:
    """Represents a user session with unique identifier and metadata."""
    
    user_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    
    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
    
    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if the session has expired based on inactivity."""
        timeout_delta = timedelta(minutes=timeout_minutes)
        return datetime.now(timezone.utc) - self.last_activity > timeout_delta


class SessionManager:
    """Manages user sessions for the philoagents application."""
    
    def __init__(self, session_timeout_minutes: int = 60):
        """Initialize the session manager.
        
        Args:
            session_timeout_minutes: Minutes of inactivity before session expires
        """
        self._sessions: dict[str, UserSession] = {}
        self._session_timeout_minutes = session_timeout_minutes
        self._cleanup_task: Optional[asyncio.Task] = None
        logger.info(f"SessionManager __init__ called. Instance id: {id(self)}")
        # Do not start cleanup task here; must be started from async context

    def start_cleanup_task(self) -> None:
        """Start the background task for cleaning up expired sessions from an async context."""
        try:
            loop = asyncio.get_running_loop()
            if self._cleanup_task is None or self._cleanup_task.done():
                self._cleanup_task = loop.create_task(self._cleanup_expired_sessions())
                logger.info("Session cleanup task started.")
        except RuntimeError:
            logger.warning("No running event loop; cleanup task not started. Call start_cleanup_task() from an async context.")

    def create_session(self, user_id: Optional[str] = None) -> UserSession:
        """Create a new user session with a unique or provided identifier.
        
        Args:
            user_id: Optional user ID to use for the session
        Returns:
            UserSession: The newly created session
        """
        if user_id is None:
            user_id = str(uuid.uuid4())
        session = UserSession(user_id=user_id)
        self._sessions[user_id] = session
        logger.info(f"Created new session for user: {user_id}")
        logger.info(f"[create_session] Instance id: {id(self)} | user_id: {user_id} | Current sessions: {list(self._sessions.keys())}")
        return session

    def get_session(self, user_id: str) -> Optional[UserSession]:
        """Retrieve a session by user ID.
        
        Args:
            user_id: The unique user identifier
            
        Returns:
            UserSession if found and active, None otherwise
        """
        session = self._sessions.get(user_id)
        logger.info(f"[get_session] Instance id: {id(self)} | user_id: {user_id} | Current sessions: {list(self._sessions.keys())}")
        if session is None:
            return None
            
        if session.is_expired(self._session_timeout_minutes):
            self.invalidate_session(user_id)
            return None
            
        session.update_activity()
        return session
    
    def get_or_create_session(self, user_id: Optional[str] = None) -> UserSession:
        """Get an existing session or create a new one.
        
        Args:
            user_id: Optional user ID to retrieve existing session
            
        Returns:
            UserSession: Existing session or newly created one
        """
        logger.info(f"[get_or_create_session] Instance id: {id(self)} | user_id: {user_id} | Current sessions: {list(self._sessions.keys())}")
        if user_id:
            session = self.get_session(user_id)
            logger.info(f"Session: {session}")
            if session:
                return session
            # If session does not exist, create with provided user_id
            return self.create_session(user_id=user_id)
        return self.create_session()
    
    def invalidate_session(self, user_id: str) -> bool:
        """Invalidate and remove a session.
        
        Args:
            user_id: The user ID whose session to invalidate
            
        Returns:
            bool: True if session was found and removed, False otherwise
        """
        logger.info(f"[invalidate_session] Instance id: {id(self)} | user_id: {user_id} | Current sessions before: {list(self._sessions.keys())}")
        session = self._sessions.pop(user_id, None)
        if session:
            session.is_active = False
            logger.info(f"Invalidated session for user: {user_id}")
            logger.info(f"[invalidate_session] Instance id: {id(self)} | user_id: {user_id} | Current sessions after: {list(self._sessions.keys())}")
            return True
        logger.info(f"[invalidate_session] Instance id: {id(self)} | user_id: {user_id} | Current sessions after: {list(self._sessions.keys())}")
        return False
    
    def get_active_session_count(self) -> int:
        """Get the number of currently active sessions.
        
        Returns:
            int: Number of active sessions
        """
        return len(self._sessions)
    
    def create_thread_id(self, user_id: str, philosopher_id: str) -> str:
        """Create a composite thread ID for conversation isolation.
        
        Args:
            user_id: The unique user identifier
            philosopher_id: The philosopher identifier
            
        Returns:
            str: Composite thread ID in format "user_id:philosopher_id"
        """
        return f"{user_id}:{philosopher_id}"
    
    async def _cleanup_expired_sessions(self) -> None:
        """Background task to periodically clean up expired sessions."""
        while True:
            try:
                expired_users = [
                    user_id for user_id, session in self._sessions.items()
                    if session.is_expired(self._session_timeout_minutes)
                ]
                
                for user_id in expired_users:
                    self.invalidate_session(user_id)
                
                if expired_users:
                    logger.info(f"Cleaned up {len(expired_users)} expired sessions")
                
                # Run cleanup every 10 minutes
                await asyncio.sleep(600)
                
            except Exception as e:
                logger.error(f"Error in session cleanup task: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    def shutdown(self) -> None:
        """Shutdown the session manager and cleanup resources."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
        
        self._sessions.clear()
        logger.info("Session manager shutdown complete")


# Global session manager instance
session_manager = SessionManager()
