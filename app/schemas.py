from typing import Optional, List
from pydantic import BaseModel

class SignupSchema(BaseModel):
    email: str
    phone: str
    password: str
    role: str = "User"

class LoginSchema(BaseModel):
    email: str
    password: str

class CommentSchema(BaseModel):
    user_id: int
    comment: str

class ForgotPasswordSchema(BaseModel):
    email: str

class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str


class OTPResetSchema(BaseModel):
    email: str
    otp: str
    new_password: str


# OTP Request Model
class OTPVerify(BaseModel):
    email: str
    otp: str


# Video Call Schemas
class InitiateCallSchema(BaseModel):
    caller_id: int
    callee_id: int


class VideoCallSchema(BaseModel):
    id: int
    caller_id: int
    callee_id: int
    status: str
    start_time: str
    end_time: Optional[str] = None
    call_duration: int = 0


class SDPOfferSchema(BaseModel):
    sdp: str
    type: str = "offer"


class SDPAnswerSchema(BaseModel):
    sdp: str
    type: str = "answer"


class ICECandidateSchema(BaseModel):
    candidate: str
    sdpMLineIndex: int
    sdpMid: str


class CallHistorySchema(BaseModel):
    caller_id: int
    callee_id: int
    call_type: str = "video"
    start_time: str
    end_time: str
    duration: int
    status: str


# Post & Feed Schemas
class CreatePostSchema(BaseModel):
    user_id: int
    content: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None


class PostSchema(BaseModel):
    id: int
    user_id: int
    content: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    created_at: str
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    is_liked: bool = False
    user_email: Optional[str] = None


class CreateCommentSchema(BaseModel):
    post_id: int
    user_id: int
    content: str


class CommentResponseSchema(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    likes_count: int = 0
    created_at: str
    user_email: Optional[str] = None


class LikePostSchema(BaseModel):
    post_id: int
    user_id: int


class SharePostSchema(BaseModel):
    post_id: int
    user_id: int
    share_message: Optional[str] = None


class PostDetailSchema(BaseModel):
    id: int
    user_id: int
    content: Optional[str] = None
    created_at: str
    likes_count: int
    comments_count: int
    shares_count: int
    is_liked: bool = False
    user_email: Optional[str] = None
    comments: List = []


class SendMessageSchema(BaseModel):
    sender_id: int
    receiver_id: int
    message_text: Optional[str] = None
    shared_post_id: Optional[int] = None

