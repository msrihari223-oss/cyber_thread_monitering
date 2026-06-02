from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from datetime import datetime

try:
    from .database import Base
except (ImportError, ValueError):
    from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    phone = Column(String)
    password = Column(String)
    threat_score = Column(Float, default=0)
    status = Column(String, default="active")
    password_reset_token = Column(String, nullable=True)
    warnings_count = Column(Integer, default=0)
    role = Column(String, default="User")


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    comment = Column(String)
    toxicity_score = Column(Float)
    level = Column(String)


class VideoCall(Base):
    __tablename__ = "video_calls"

    id = Column(Integer, primary_key=True)
    caller_id = Column(Integer)
    callee_id = Column(Integer)
    status = Column(String, default="pending")  # pending, ongoing, ended
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    call_duration = Column(Integer, default=0)  # in seconds
    call_quality = Column(String, default="unknown")  # good, fair, poor


class CallHistory(Base):
    __tablename__ = "call_history"

    id = Column(Integer, primary_key=True)
    caller_id = Column(Integer)
    callee_id = Column(Integer)
    call_type = Column(String, default="video")  # video, audio
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)  # in seconds
    status = Column(String)  # completed, missed, rejected


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)  # Post creator
    content = Column(Text)  # Post content
    image_url = Column(String, nullable=True)  # URL to the uploaded image
    video_url = Column(String, nullable=True)  # URL to the uploaded video
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)


class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer)
    user_id = Column(Integer)  # User who liked
    created_at = Column(DateTime, default=datetime.utcnow)


class PostComment(Base):
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer)
    user_id = Column(Integer)  # Comment author
    content = Column(Text)
    likes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)


class PostShare(Base):
    __tablename__ = "post_shares"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer)
    user_id = Column(Integer)  # User who shared
    share_message = Column(Text, nullable=True)  # Optional message with share
    created_at = Column(DateTime, default=datetime.utcnow)


class DirectMessage(Base):
    __tablename__ = "direct_messages"

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer)
    receiver_id = Column(Integer)
    message_text = Column(Text, nullable=True)
    shared_post_id = Column(Integer, nullable=True)  # References posts.id
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)