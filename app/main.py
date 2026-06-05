import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from datetime import datetime, timedelta
import uuid

try:
    from .database import engine, Base, SessionLocal
    from .models import User, Violation, VideoCall, CallHistory, Post, PostLike, PostComment, PostShare, DirectMessage, MailLog
    from .schemas import (
        LoginSchema,
        CommentSchema,
        SignupSchema,
        ForgotPasswordSchema,
        ResetPasswordSchema,
        OTPResetSchema,
        OTPVerify,
        InitiateCallSchema,
        SDPOfferSchema,
        SDPAnswerSchema,
        ICECandidateSchema,
        CreatePostSchema,
        PostSchema,
        CreateCommentSchema,
        CommentResponseSchema,
        LikePostSchema,
        SharePostSchema,
        PostDetailSchema,
        SendMessageSchema,
    )
    from .ai_engine import analyze_text
    from .auth import create_token
    from .otp import generate_otp, otp_storage
    from .email_service import send_otp_email, send_spam_report_email, send_warning_email_to_user
    from .video_call_manager import video_call_manager
except (ImportError, ValueError):
    from database import engine, Base, SessionLocal
    from models import User, Violation, VideoCall, CallHistory, Post, PostLike, PostComment, PostShare, DirectMessage, MailLog
    from schemas import (
        LoginSchema,
        CommentSchema,
        SignupSchema,
        ForgotPasswordSchema,
        ResetPasswordSchema,
        OTPResetSchema,
        OTPVerify,
        InitiateCallSchema,
        SDPOfferSchema,
        SDPAnswerSchema,
        ICECandidateSchema,
        CreatePostSchema,
        PostSchema,
        CreateCommentSchema,
        CommentResponseSchema,
        LikePostSchema,
        SharePostSchema,
        PostDetailSchema,
        SendMessageSchema,
    )
    from ai_engine import analyze_text
    from auth import create_token
    from otp import generate_otp, otp_storage
    from email_service import send_otp_email, send_spam_report_email, send_warning_email_to_user
    from video_call_manager import video_call_manager

import secrets

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
MEDIA_DIR = ROOT_DIR / "media"

# Create media directory if it doesn't exist
MEDIA_DIR.mkdir(exist_ok=True)

# Mount static files for media
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")


def get_html_file(filename: str):
    path = FRONTEND_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Page not found")
    return FileResponse(path)


def seed_demo_user():
    db = SessionLocal()
    try:
        # Create admin if no admin user exists yet
        admin = db.query(User).filter(User.email == "admin@cyberwatch.com").first()
        if not admin:
            admin = User(
                email="admin@cyberwatch.com",
                phone="0000000000",
                password="Admin@2024",
                role="Admin"
            )
            db.add(admin)
            db.commit()
        else:
            if admin.role != "Admin":
                admin.role = "Admin"
                db.commit()

        # Create admin2 if no second admin user exists yet
        admin2 = db.query(User).filter(User.email == "admin2@cyberwatch.com").first()
        if not admin2:
            admin2 = User(
                email="admin2@cyberwatch.com",
                phone="1111111111",
                password="Admin@2024",
                role="Admin"
            )
            db.add(admin2)
            db.commit()
        else:
            if admin2.role != "Admin":
                admin2.role = "Admin"
                db.commit()
    finally:
        db.close()


seed_demo_user()


@app.get("/")
def home():
    return get_html_file("login.html")


@app.get("/signup")
def signup_page():
    return get_html_file("signup.html")


@app.get("/forgot-password")
def forgot_password_page():
    return get_html_file("forgot_password.html")


@app.get("/reset-password")
def reset_password_page():
    return get_html_file("reset_password.html")


@app.get("/dashboard")
def dashboard():
    return get_html_file("dashboard.html")


@app.get("/analytics")
def analytics():
    return get_html_file("analytics.html")


@app.get("/feed")
def feed_page():
    return get_html_file("feed.html")


@app.post("/signup")
def signup(data: SignupSchema):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = User(
            email=data.email,
            phone=data.phone,
            password=data.password,
            role=data.role if data.role in ["Admin", "User"] else "User"
        )
        db.add(new_user)
        db.commit()
        token = create_token({"sub": data.email, "user_id": new_user.id, "role": new_user.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": new_user.id,
            "role": new_user.role,
            "message": "Account created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.post("/forgot-password")
def forgot_password(data: ForgotPasswordSchema, background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
        email = data.email.strip().lower()
        user = db.query(User).filter(func.lower(User.email) == email).first()
        if user is None:
            raise HTTPException(status_code=404, detail="Email not found")

        # Generate an OTP, store it temporarily and email it to the user.
        otp_code = generate_otp()
        otp_storage[email] = otp_code

        # Print to console for fast local developer debugging
        print("\n" + "="*60)
        print(f"[SECURITY DEV LOG] GENERATED FORGOT PASSWORD OTP FOR {email}: {otp_code}")
        print("="*60 + "\n")

        # Send OTP via email and SMS fallback as requested
        from .email_service import send_otp_email, send_otp_sms
        background_tasks.add_task(send_otp_email, user.email, otp_code)
        if user.phone:
            background_tasks.add_task(send_otp_sms, user.phone, otp_code)

        return {"message": "OTP sent to your email successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/forgot-password/otp")
def forgot_password_get(email: str, background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
        email_clean = email.strip().lower()
        user = db.query(User).filter(func.lower(User.email) == email_clean).first()
        if user is None:
            raise HTTPException(status_code=404, detail="Email not found")

        otp_code = generate_otp()
        otp_storage[email_clean] = otp_code

        # Print to console for fast local developer debugging
        print("\n" + "="*60)
        print(f"[SECURITY DEV LOG] GENERATED FORGOT PASSWORD OTP FOR {email_clean}: {otp_code}")
        print("="*60 + "\n")

        # Send OTP via email and SMS fallback as requested
        from .email_service import send_otp_email, send_otp_sms
        background_tasks.add_task(send_otp_email, user.email, otp_code)
        if user.phone:
            background_tasks.add_task(send_otp_sms, user.phone, otp_code)

        return {"message": "OTP sent to your email successfully!"}
    finally:
        db.close()


@app.post("/reset-password")
def reset_password(data: ResetPasswordSchema):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.password_reset_token == data.token).first()
        if user is None:
            raise HTTPException(status_code=404, detail="Invalid or expired reset token")

        user.password = data.new_password
        user.password_reset_token = None
        db.commit()

        return {"message": "Password reset successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()



@app.post("/verify-otp")
def verify_otp(data: OTPVerify):
    db = SessionLocal()
    try:
        email = data.email.strip().lower()
        expected = otp_storage.get(email)
        if expected is None or expected != data.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        user = db.query(User).filter(func.lower(User.email) == email).first()
        if user is None:
            raise HTTPException(status_code=404, detail="Email not found")

        # Create a reset token and clear stored OTP
        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        db.commit()
        try:
            del otp_storage[email]
        except KeyError:
            pass

        return {
            "message": "OTP verified",
            "reset_token": reset_token,
            "reset_url": f"/reset-password?token={reset_token}"
        }
    finally:
        db.close()


@app.post("/login")
def login(data: LoginSchema):
    db = SessionLocal()
    try:
        email = data.email.strip().lower()
        user = db.query(User).filter(func.lower(User.email) == email).first()
        if user is None or user.password != data.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if user.status == "blocked":
            raise HTTPException(status_code=403, detail="Account blocked due to policy violation")
        token = create_token({"sub": user.email, "user_id": user.id, "role": user.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "role": user.role
        }
    finally:
        db.close()


@app.get("/user-status")
def user_status(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user_id": user.id, "status": user.status}
    finally:
        db.close()


@app.post("/analyze")
def analyze(data: CommentSchema, background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == data.user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        score, level = analyze_text(data.comment)
        action = "Monitor"
        if level == "HIGH" or level == "CRITICAL":
            action = "Immediate Block"
            user.status = "blocked"
            try:
                from .email_service import send_spam_report_email
                background_tasks.add_task(send_spam_report_email, user.email, score, level, data.comment)
            except Exception as e:
                print("Spam report email failed scheduling:", repr(e))

        user.threat_score = score
        violation = Violation(
            user_id=user.id,
            comment=data.comment,
            toxicity_score=score,
            level=level,
        )
        db.add(violation)
        db.commit()

        return {"score": score, "level": level, "action": action}
    finally:
        db.close()


@app.get("/api/users/search")
def search_users(q: str = "", limit: int = 10):
    """Search users by email (live search)"""
    db = SessionLocal()
    try:
        if not q.strip():
            return {"users": []}
        results = db.query(User).filter(
            User.email.ilike(f"%{q.strip()}%")
        ).limit(limit).all()
        return {
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "status": u.status,
                    "threat_score": round(u.threat_score or 0, 2),
                }
                for u in results
            ]
        }
    finally:
        db.close()


@app.get("/admin/stats")
def admin_stats():
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        blocked_users = db.query(User).filter(User.status == "blocked").count()
        blacklisted_users = db.query(User).filter(User.threat_score >= 0.85).count()
        blocked_emails = [user.email for user in db.query(User).filter(User.status == "blocked").all()]
        return {
            "total_users": total_users,
            "blocked_users": blocked_users,
            "blacklisted_users": blacklisted_users,
            "blocked_emails": blocked_emails,
        }
    finally:
        db.close()


@app.get("/api/admin/mail-logs")
def get_mail_logs():
    """Retrieve system mail logs for admin visualization"""
    db = SessionLocal()
    try:
        logs = db.query(MailLog).order_by(MailLog.timestamp.desc()).limit(30).all()
        return [
            {
                "id": log.id,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "",
                "sender": log.sender,
                "receiver": log.receiver,
                "subject": log.subject,
                "body": log.body,
                "status": log.status
            }
            for log in logs
        ]
    finally:
        db.close()


@app.get("/api/admin/dashboard-stats")
def admin_dashboard_stats():
    """Full admin dashboard statistics"""
    db = SessionLocal()
    try:
        # User stats
        total_users = db.query(User).count()
        blocked_users = db.query(User).filter(User.status == "blocked").count()
        active_users = db.query(User).filter(User.status == "active").count()
        high_risk_users = db.query(User).filter(User.threat_score >= 0.7).count()

        # Post stats
        total_posts = db.query(Post).filter(Post.is_deleted == False).count()
        total_likes = db.query(func.sum(Post.likes_count)).filter(Post.is_deleted == False).scalar() or 0
        total_comments = db.query(func.sum(Post.comments_count)).filter(Post.is_deleted == False).scalar() or 0
        total_shares = db.query(func.sum(Post.shares_count)).filter(Post.is_deleted == False).scalar() or 0
        posts_with_images = db.query(Post).filter(Post.is_deleted == False, Post.image_url != None).count()

        # Recent posts (latest 20 with user info)
        recent_posts = db.query(Post).filter(Post.is_deleted == False).order_by(
            Post.created_at.desc()
        ).limit(20).all()

        posts_list = []
        for post in recent_posts:
            creator = db.query(User).filter(User.id == post.user_id).first()
            posts_list.append({
                "id": post.id,
                "user_id": post.user_id,
                "user_email": creator.email if creator else "Unknown",
                "content": post.content,
                "image_url": post.image_url,
                "created_at": post.created_at.isoformat(),
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "shares_count": post.shares_count,
            })

        # All users list
        all_users = db.query(User).order_by(User.id.desc()).all()
        users_list = [
            {
                "id": u.id,
                "email": u.email,
                "status": u.status,
                "threat_score": round(u.threat_score or 0, 2),
                "role": u.role or "User",
            }
            for u in all_users
        ]

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "blocked": blocked_users,
                "high_risk": high_risk_users,
            },
            "posts": {
                "total": total_posts,
                "total_likes": int(total_likes),
                "total_comments": int(total_comments),
                "total_shares": int(total_shares),
                "with_images": posts_with_images,
            },
            "recent_posts": posts_list,
            "all_users": users_list,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.delete("/api/admin/posts/{post_id}")
def admin_delete_post(post_id: int, user_id: int):
    """Admin/User: delete a post. Admin can delete any post. Users can only delete their own posts."""
    db = SessionLocal()
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if user.role != "Admin" and post.user_id != user_id:
            raise HTTPException(status_code=403, detail="Can only delete own posts")
            
        post.is_deleted = True
        db.commit()
        return {"message": f"Post {post_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.post("/api/admin/users/{user_id}/unblock")
def admin_unblock_user(user_id: int):
    """Admin: unblock a user by ID and reset their warnings"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.status = "active"
        user.threat_score = 0.0
        user.warnings_count = 0  # Reset strike counter for fresh start
        db.commit()
        return {"message": f"User {user.email} has been unblocked successfully", "email": user.email}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.post("/api/admin/users/{user_id}/block")
def admin_block_user(user_id: int):
    """Admin: manually block a user by ID"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.role == "Admin":
            raise HTTPException(status_code=400, detail="Cannot block an administrator")
        user.status = "blocked"
        user.threat_score = 1.0  # Set threat score to high threat level
        db.commit()
        return {"message": f"User {user.email} has been blocked manually", "email": user.email}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.post("/admin/unblock")
def admin_unblock(data: dict):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    db = SessionLocal()
    try:
        user = db.query(User).filter(func.lower(User.email) == email.strip().lower()).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if user.status != "blocked":
            return {"message": "User is not blocked", "status": user.status}

        user.status = "active"
        db.commit()
        return {"message": "User unblocked successfully", "email": user.email}
    finally:
        db.close()


# ==================== VIDEO CALL ENDPOINTS ====================

@app.get("/video-call")
def video_call_page():
    """Serve the video call HTML page"""
    return get_html_file("video_call.html")


@app.post("/api/initiate-call")
def initiate_call(data: InitiateCallSchema):
    """Initiate a video call between two users"""
    db = SessionLocal()
    try:
        caller = db.query(User).filter(User.id == data.caller_id).first()
        callee = db.query(User).filter(User.id == data.callee_id).first()
        
        if not caller or not callee:
            raise HTTPException(status_code=404, detail="One or both users not found")
        
        if caller.status == "blocked":
            raise HTTPException(status_code=403, detail="Caller account is blocked")
        
        if callee.status == "blocked":
            raise HTTPException(status_code=403, detail="Callee account is blocked")
        
        # Create video call record
        video_call = VideoCall(
            caller_id=data.caller_id,
            callee_id=data.callee_id,
            status="pending"
        )
        db.add(video_call)
        db.commit()
        
        # Create call connection in manager
        video_call_manager.create_call(video_call.id, data.caller_id, data.callee_id)
        
        return {
            "call_id": video_call.id,
            "caller_id": data.caller_id,
            "callee_id": data.callee_id,
            "status": "pending",
            "message": "Call initiated"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.post("/api/accept-call/{call_id}")
def accept_call(call_id: int):
    """Accept a pending video call"""
    db = SessionLocal()
    try:
        video_call = db.query(VideoCall).filter(VideoCall.id == call_id).first()
        if not video_call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        if video_call.status != "pending":
            raise HTTPException(status_code=400, detail="Call is not pending")
        
        video_call.status = "ongoing"
        db.commit()
        video_call_manager.update_call_status(call_id, "ongoing")
        
        return {
            "call_id": call_id,
            "status": "ongoing",
            "message": "Call accepted"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.post("/api/reject-call/{call_id}")
def reject_call(call_id: int):
    """Reject or end a video call"""
    db = SessionLocal()
    try:
        video_call = db.query(VideoCall).filter(VideoCall.id == call_id).first()
        if not video_call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        video_call.status = "ended"
        video_call.end_time = datetime.utcnow()
        video_call.call_duration = int((video_call.end_time - video_call.start_time).total_seconds())
        db.commit()
        
        # Save to call history
        call_history = CallHistory(
            caller_id=video_call.caller_id,
            callee_id=video_call.callee_id,
            call_type="video",
            start_time=video_call.start_time,
            end_time=video_call.end_time,
            duration=video_call.call_duration,
            status="rejected" if video_call.status == "pending" else "completed"
        )
        db.add(call_history)
        db.commit()
        
        video_call_manager.end_call(call_id)
        
        return {
            "call_id": call_id,
            "status": "ended",
            "message": "Call ended"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/call-history/{user_id}")
def get_call_history(user_id: int):
    """Get call history for a user"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get recent calls (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        calls = db.query(CallHistory).filter(
            ((CallHistory.caller_id == user_id) | (CallHistory.callee_id == user_id)) &
            (CallHistory.start_time >= thirty_days_ago)
        ).order_by(CallHistory.start_time.desc()).all()
        
        return {
            "user_id": user_id,
            "call_count": len(calls),
            "calls": [
                {
                    "caller_id": call.caller_id,
                    "callee_id": call.callee_id,
                    "call_type": call.call_type,
                    "start_time": call.start_time.isoformat(),
                    "end_time": call.end_time.isoformat() if call.end_time else None,
                    "duration": call.duration,
                    "status": call.status
                }
                for call in calls
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.websocket("/ws/video-call/{call_id}/{user_id}")
async def websocket_video_call(websocket: WebSocket, call_id: int, user_id: int):
    """WebSocket endpoint for video call signaling"""
    db = SessionLocal()
    try:
        # Verify call exists
        video_call = db.query(VideoCall).filter(VideoCall.id == call_id).first()
        if not video_call:
            await websocket.close(code=4004, reason="Call not found")
            return
        
        # Verify user is part of this call
        if user_id != video_call.caller_id and user_id != video_call.callee_id:
            await websocket.close(code=4003, reason="Unauthorized")
            return
        
        # Get or create call connection
        call = video_call_manager.get_call(call_id)
        if not call:
            call = video_call_manager.create_call(call_id, video_call.caller_id, video_call.callee_id)
        
        # Connect user to WebSocket
        if user_id == call.caller_id:
            await call.connect_caller(websocket)
        else:
            await call.connect_callee(websocket)
        
        try:
            while True:
                # Receive message from WebSocket
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "offer":
                    # Forward SDP offer to callee
                    await video_call_manager.send_offer(call_id, data.get("sdp"))
                
                elif message_type == "answer":
                    # Forward SDP answer to caller
                    await video_call_manager.send_answer(call_id, data.get("sdp"))
                
                elif message_type == "ice_candidate":
                    # Forward ICE candidate to other party
                    await video_call_manager.send_ice_candidate(
                        call_id,
                        user_id,
                        data.get("candidate")
                    )
                
                elif message_type == "call_quality":
                    # Update call quality metric
                    video_call.call_quality = data.get("quality", "unknown")
                    db.commit()
        
        except WebSocketDisconnect:
            # Handle disconnection
            if user_id == call.caller_id:
                await call.disconnect_caller()
            else:
                await call.disconnect_callee()
            
            # If both parties disconnected, end the call
            if not call.caller_websocket and not call.callee_websocket:
                video_call.status = "ended"
                video_call.end_time = datetime.utcnow()
                video_call.call_duration = int((video_call.end_time - video_call.start_time).total_seconds())
                db.commit()
                
                # Save to call history
                call_history = CallHistory(
                    caller_id=video_call.caller_id,
                    callee_id=video_call.callee_id,
                    call_type="video",
                    start_time=video_call.start_time,
                    end_time=video_call.end_time,
                    duration=video_call.call_duration,
                    status="completed"
                )
                db.add(call_history)
                db.commit()
                
                video_call_manager.end_call(call_id)
        
        except Exception as e:
            print(f"WebSocket error: {e}")
            video_call_manager.end_call(call_id)
    
    finally:
        db.close()


# ==================== POST & FEED ENDPOINTS ====================

@app.post("/api/posts/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image for a post"""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed")
        
        # Validate file size (5MB max)
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 5MB")
        
        # Generate unique filename
        file_ext = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = MEDIA_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Return image URL
        image_url = f"/media/{unique_filename}"
        return {"image_url": image_url, "filename": unique_filename}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@app.post("/api/posts/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """Upload a video for a post (MP4, WebM, MOV, OGV, MKV, FLV, 3GP — max 100 MB)"""
    try:
        allowed_types = [
            "video/mp4", "video/webm", "video/quicktime",
            "video/ogg", "video/x-msvideo", "video/mpeg",
            "application/octet-stream",  # some browsers/phones use this for .mp4
        ]
        allowed_exts = {".mp4", ".webm", ".mov", ".ogv", ".ogg", ".avi", ".mpeg", ".mpg", ".mkv", ".m4v", ".flv", ".3gp", ".3gpp"}

        # Get the file extension from the original filename
        file_ext = ("." + file.filename.rsplit(".", 1)[-1].lower()) if "." in file.filename else ""

        # Accept if MIME type is valid OR if extension is valid
        is_video_mime = file.content_type and (file.content_type.startswith("video/") or file.content_type in allowed_types)
        if not is_video_mime and file_ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type '{file.content_type}' with extension '{file_ext}'. Only video files (MP4, WebM, MOV, OGV, AVI, MKV, FLV, 3GP) are allowed."
            )

        # Reject if extension is clearly not a video (security check)
        if file_ext and file_ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"File extension '{file_ext}' is not allowed for video uploads."
            )

        contents = await file.read()
        if len(contents) > 100 * 1024 * 1024:  # 100 MB
            raise HTTPException(status_code=400, detail="Video must be less than 100 MB")

        safe_ext = file_ext.lstrip(".") if file_ext else "mp4"
        unique_filename = f"{uuid.uuid4()}.{safe_ext}"
        file_path = MEDIA_DIR / unique_filename

        with open(file_path, "wb") as f:
            f.write(contents)

        video_url = f"/media/{unique_filename}"
        return {"video_url": video_url, "filename": unique_filename}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {str(e)}")




@app.post("/api/posts/create")
def create_post(data: CreatePostSchema, background_tasks: BackgroundTasks):
    """Create a new post — auto-checks toxicity and issues warnings"""
    db = SessionLocal()
    try:
        # Verify user exists and is active
        user = db.query(User).filter(User.id == data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is blocked
        if user.status == "blocked":
            raise HTTPException(status_code=403, detail="Blocked users cannot create posts")
        
        # Validate content
        if (not data.content or len(data.content.strip()) == 0) and not data.image_url and not data.video_url:
            raise HTTPException(status_code=400, detail="Post content cannot be empty. Please write a message or attach an image/video.")
        
        # ---- TOXICITY CHECK ----
        warning_issued = False
        is_blocked = False
        toxicity_score = 0.0
        threat_level = "LOW"

        try:
            toxicity_score, threat_level = analyze_text(data.content)
        except Exception as e:
            print(f"Error analyzing post toxicity: {e}")

        TOXIC_THRESHOLD = 0.6  # score >= 0.6 triggers a warning
        MAX_WARNINGS = 3

        if toxicity_score >= TOXIC_THRESHOLD:
            warning_issued = True
            user.warnings_count = (user.warnings_count or 0) + 1
            user.threat_score = max(user.threat_score or 0, toxicity_score)

            # Log the violation
            violation = Violation(
                user_id=user.id,
                comment=data.content,
                toxicity_score=toxicity_score,
                level=threat_level,
            )
            db.add(violation)

            # Block after 3 warnings
            if user.warnings_count >= MAX_WARNINGS:
                user.status = "blocked"
                is_blocked = True

            # Send email notifications asynchronously using background tasks
            try:
                from .email_service import send_warning_email_to_user, send_spam_report_email
                background_tasks.add_task(
                    send_warning_email_to_user,
                    user_email=user.email,
                    warnings_count=user.warnings_count or 0,
                    comment=data.content,
                    is_blocked=is_blocked
                )
                background_tasks.add_task(
                    send_spam_report_email,
                    user_email=user.email,
                    score=toxicity_score,
                    level=threat_level,
                    comment=data.content
                )
            except Exception as email_err:
                print(f"Failed to schedule toxicity emails: {email_err}")

        # Create post
        post = Post(
            user_id=data.user_id,
            content=data.content,
            image_url=data.image_url,
            video_url=data.video_url,
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        
        return {
            "id": post.id,
            "user_id": post.user_id,
            "content": post.content,
            "image_url": post.image_url,
            "video_url": post.video_url,
            "created_at": post.created_at.isoformat(),
            "likes_count": 0,
            "comments_count": 0,
            "shares_count": 0,
            "message": "Post created successfully",
            # Warning fields
            "warning_issued": warning_issued,
            "warnings_count": user.warnings_count or 0,
            "is_blocked": is_blocked,
            "toxicity_score": round(toxicity_score, 2),
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/media/gallery")
def get_media_gallery(user_id: int):
    """List only the uploaded media files belonging to the logged-in user"""
    db = SessionLocal()
    try:
        # Query database for all posts belonging to this user that have images
        posts_with_images = db.query(Post).filter(
            Post.user_id == user_id,
            Post.image_url.isnot(None),
            Post.is_deleted == False
        ).all()
        
        # Build set of image URLs that are owned by this user
        user_image_urls = {post.image_url for post in posts_with_images}
        
        images = []
        for f in MEDIA_DIR.iterdir():
            if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                url = f"/media/{f.name}"
                if url in user_image_urls:
                    images.append({
                        "filename": f.name,
                        "url": url,
                        "size": f.stat().st_size,
                        "type": "image",
                    })

        # Also include user's videos
        posts_with_videos = db.query(Post).filter(
            Post.user_id == user_id,
            Post.video_url.isnot(None),
            Post.is_deleted == False
        ).all()
        user_video_urls = {post.video_url for post in posts_with_videos}
        for f in MEDIA_DIR.iterdir():
            if f.is_file() and f.suffix.lower() in [".mp4", ".webm", ".mov", ".ogv", ".avi"]:
                url = f"/media/{f.name}"
                if url in user_video_urls:
                    images.append({
                        "filename": f.name,
                        "url": url,
                        "size": f.stat().st_size,
                        "type": "video",
                    })

        # Sort newest first by file mtime
        images.sort(key=lambda x: (MEDIA_DIR / x["filename"]).stat().st_mtime, reverse=True)
        return {"images": images, "total": len(images)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load gallery: {str(e)}")
    finally:
        db.close()



@app.delete("/api/media/{filename}")
def delete_media_file(filename: str):
    """Delete an uploaded media file from disk and clear references in posts"""
    try:
        # Security: only allow safe filenames (no path traversal)
        if "/" in filename or "\\" in filename or ".." in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        file_path = MEDIA_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Remove from disk
        file_path.unlink()

        # Also clear image_url on any posts that referenced this file
        db = SessionLocal()
        try:
            image_url = f"/media/{filename}"
            posts = db.query(Post).filter(Post.image_url == image_url).all()
            for post in posts:
                post.image_url = None
            db.commit()
        finally:
            db.close()

        return {"message": f"{filename} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@app.get("/api/posts/feed")
def get_feed(user_id: int, limit: int = 20, offset: int = 0):
    """Get feed of posts with engagement info"""
    db = SessionLocal()
    try:
        # Verify user exists — return empty feed gracefully if not found
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"user_id": user_id, "posts": [], "total": 0}
        
        # Get posts (most recent first)
        posts = db.query(Post).filter(Post.is_deleted == False).order_by(
            Post.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Get user likes for current user
        user_likes = db.query(PostLike.post_id).filter(
            PostLike.user_id == user_id
        ).all()
        liked_post_ids = {like[0] for like in user_likes}
        
        # Build response
        feed = []
        for post in posts:
            post_creator = db.query(User).filter(User.id == post.user_id).first()
            feed.append({
                "id": post.id,
                "user_id": post.user_id,
                "user_email": post_creator.email if post_creator else "Unknown",
                "content": post.content,
                "image_url": post.image_url,
                "video_url": post.video_url,
                "created_at": post.created_at.isoformat(),
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "shares_count": post.shares_count,
                "is_liked": post.id in liked_post_ids
            })
        
        return {
            "user_id": user_id,
            "posts": feed,
            "total": len(feed)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/posts/user/{user_id}")
def get_user_posts(user_id: int):
    """Get all posts created by a specific user (for My Posts tab)"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        posts = db.query(Post).filter(
            Post.user_id == user_id,
            Post.is_deleted == False
        ).order_by(Post.created_at.desc()).all()
        return {
            "posts": [
                {
                    "id": p.id,
                    "content": p.content,
                    "image_url": p.image_url,
                    "video_url": p.video_url,
                    "created_at": p.created_at.isoformat(),
                    "likes_count": p.likes_count,
                    "comments_count": p.comments_count,
                    "shares_count": p.shares_count,
                }
                for p in posts
            ],
            "total": len(posts)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/posts/{post_id}")
def get_post_detail(post_id: int, user_id: int):
    """Get detailed view of a post with all comments"""
    db = SessionLocal()
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get post
        post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Check if current user liked this post
        user_like = db.query(PostLike).filter(
            PostLike.post_id == post_id,
            PostLike.user_id == user_id
        ).first()
        is_liked = user_like is not None
        
        # Get post creator info
        post_creator = db.query(User).filter(User.id == post.user_id).first()
        
        # Get comments
        comments = db.query(PostComment).filter(
            PostComment.post_id == post_id,
            PostComment.is_deleted == False
        ).order_by(PostComment.created_at.desc()).all()
        
        comments_list = []
        for comment in comments:
            comment_author = db.query(User).filter(User.id == comment.user_id).first()
            comments_list.append({
                "id": comment.id,
                "user_id": comment.user_id,
                "user_email": comment_author.email if comment_author else "Unknown",
                "content": comment.content,
                "likes_count": comment.likes_count,
                "created_at": comment.created_at.isoformat()
            })
        
        return {
            "id": post.id,
            "user_id": post.user_id,
            "user_email": post_creator.email if post_creator else "Unknown",
            "content": post.content,
            "created_at": post.created_at.isoformat(),
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "shares_count": post.shares_count,
            "is_liked": is_liked,
            "comments": comments_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.post("/api/posts/{post_id}/like")
def like_post(post_id: int, data: LikePostSchema):
    """Like a post - only active users can like"""
    db = SessionLocal()
    try:
        # Verify user exists and is active
        user = db.query(User).filter(User.id == data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.status == "blocked":
            raise HTTPException(status_code=403, detail="Blocked users cannot like posts")
        
        # Verify post exists
        post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Check if already liked
        existing_like = db.query(PostLike).filter(
            PostLike.post_id == post_id,
            PostLike.user_id == data.user_id
        ).first()
        
        if existing_like:
            # Unlike
            db.delete(existing_like)
            post.likes_count = max(0, post.likes_count - 1)
            action = "unliked"
        else:
            # Like
            like = PostLike(post_id=post_id, user_id=data.user_id)
            db.add(like)
            post.likes_count += 1
            action = "liked"
        
        db.commit()
        
        return {
            "post_id": post_id,
            "user_id": data.user_id,
            "action": action,
            "likes_count": post.likes_count,
            "message": f"Post {action} successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.post("/api/posts/{post_id}/comment")
def comment_post(post_id: int, data: CreateCommentSchema, background_tasks: BackgroundTasks):
    """Add comment to post — auto-checks toxicity and issues warnings"""
    db = SessionLocal()
    try:
        # Verify user
        user = db.query(User).filter(User.id == data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.status == "blocked":
            raise HTTPException(status_code=403, detail="Your account is blocked. You cannot comment.")

        # Verify post
        post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if not data.content or len(data.content.strip()) == 0:
            raise HTTPException(status_code=400, detail="Comment cannot be empty")

        # ---- TOXICITY CHECK ----
        warning_issued = False
        is_blocked = False
        toxicity_score = 0.0
        threat_level = "LOW"

        try:
            toxicity_score, threat_level = analyze_text(data.content)
        except Exception as e:
            print(f"Error analyzing comment toxicity: {e}")
            pass  # If AI fails, still allow comment

        TOXIC_THRESHOLD = 0.6  # score >= 0.6 triggers a warning
        MAX_WARNINGS = 3

        if toxicity_score >= TOXIC_THRESHOLD:
            warning_issued = True
            user.warnings_count = (user.warnings_count or 0) + 1
            user.threat_score = max(user.threat_score or 0, toxicity_score)

            # Log the violation
            violation = Violation(
                user_id=user.id,
                comment=data.content,
                toxicity_score=toxicity_score,
                level=threat_level,
            )
            db.add(violation)

            # Block after 3 warnings
            if user.warnings_count >= MAX_WARNINGS:
                user.status = "blocked"
                is_blocked = True

            # Send email notifications asynchronously using background tasks
            try:
                from .email_service import send_warning_email_to_user, send_spam_report_email
                background_tasks.add_task(
                    send_warning_email_to_user,
                    user_email=user.email,
                    warnings_count=user.warnings_count or 0,
                    comment=data.content,
                    is_blocked=is_blocked
                )
                background_tasks.add_task(
                    send_spam_report_email,
                    user_email=user.email,
                    score=toxicity_score,
                    level=threat_level,
                    comment=data.content
                )
            except Exception as email_err:
                print(f"Failed to schedule toxicity emails: {email_err}")

        # Save comment
        comment = PostComment(
            post_id=post_id,
            user_id=data.user_id,
            content=data.content
        )
        db.add(comment)
        post.comments_count += 1
        db.commit()
        db.refresh(comment)

        return {
            "id": comment.id,
            "post_id": post_id,
            "user_id": data.user_id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
            "message": "Comment added successfully",
            # Warning fields
            "warning_issued": warning_issued,
            "warnings_count": user.warnings_count or 0,
            "is_blocked": is_blocked,
            "toxicity_score": round(toxicity_score, 2),
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()



@app.post("/api/posts/{post_id}/share")
def share_post(post_id: int, data: SharePostSchema):
    """Share a post - only active users can share"""
    db = SessionLocal()
    try:
        # Verify user exists and is active
        user = db.query(User).filter(User.id == data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.status == "blocked":
            raise HTTPException(status_code=403, detail="Blocked users cannot share posts")
        
        # Verify post exists
        post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Create share record
        share = PostShare(
            post_id=post_id,
            user_id=data.user_id,
            share_message=data.share_message
        )
        db.add(share)
        post.shares_count += 1

        # Reshare/Repost: Create a new Post record referencing the original post
        original_creator = db.query(User).filter(User.id == post.user_id).first()
        original_author_email = original_creator.email if original_creator else "Unknown"

        reshare_content = f"Shared from {original_author_email}:\n{post.content or ''}"
        if data.share_message:
            reshare_content = f"{data.share_message}\n\n" + reshare_content

        new_post = Post(
            user_id=data.user_id,
            content=reshare_content.strip(),
            image_url=post.image_url,
            video_url=post.video_url
        )
        db.add(new_post)
        db.commit()
        
        return {
            "post_id": post_id,
            "user_id": data.user_id,
            "shares_count": post.shares_count,
            "message": "Post shared successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, user_id: int):
    """Delete own post - only post creator can delete"""
    db = SessionLocal()
    try:
        # Get post
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Verify ownership
        if post.user_id != user_id:
            raise HTTPException(status_code=403, detail="Can only delete own posts")
        
        # Soft delete
        post.is_deleted = True
        db.commit()
        
        return {
            "post_id": post_id,
            "message": "Post deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.delete("/api/comments/{comment_id}")
def delete_comment(comment_id: int, user_id: int):
    """Delete own comment - only comment author can delete"""
    db = SessionLocal()
    try:
        # Get comment
        comment = db.query(PostComment).filter(PostComment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify ownership
        if comment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Can only delete own comments")
        
        # Update post comment count
        post = db.query(Post).filter(Post.id == comment.post_id).first()
        if post:
            post.comments_count = max(0, post.comments_count - 1)
        
        # Soft delete
        comment.is_deleted = True
        db.commit()
        
        return {
            "comment_id": comment_id,
            "message": "Comment deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/posts/user/{user_id}/posts")
def get_user_posts(user_id: int, limit: int = 20, offset: int = 0):
    """Get all posts by a specific user"""
    db = SessionLocal()
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's posts
        posts = db.query(Post).filter(
            Post.user_id == user_id,
            Post.is_deleted == False
        ).order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
        
        posts_list = []
        for post in posts:
            posts_list.append({
                "id": post.id,
                "user_id": post.user_id,
                "content": post.content,
                "created_at": post.created_at.isoformat(),
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "shares_count": post.shares_count
            })
        
        return {
            "user_id": user_id,
            "user_email": user.email,
            "posts": posts_list,
            "total": len(posts_list)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.post("/api/messages/send")
def send_message(data: SendMessageSchema):
    """Send a direct message (text and/or shared post) to a user"""
    db = SessionLocal()
    try:
        # Verify sender and receiver exist
        sender = db.query(User).filter(User.id == data.sender_id).first()
        receiver = db.query(User).filter(User.id == data.receiver_id).first()
        if not sender or not receiver:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Blocked users cannot send messages
        if sender.status == "blocked":
            raise HTTPException(status_code=403, detail="Blocked users cannot send messages")
        
        if not data.message_text and not data.shared_post_id:
            raise HTTPException(status_code=400, detail="Cannot send an empty message")
        
        # Verify post if shared
        if data.shared_post_id:
            post = db.query(Post).filter(Post.id == data.shared_post_id, Post.is_deleted == False).first()
            if not post:
                raise HTTPException(status_code=404, detail="Shared post not found or has been deleted")
        
        message = DirectMessage(
            sender_id=data.sender_id,
            receiver_id=data.receiver_id,
            message_text=data.message_text,
            shared_post_id=data.shared_post_id
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "message_text": message.message_text,
            "shared_post_id": message.shared_post_id,
            "created_at": message.created_at.isoformat(),
            "is_read": message.is_read
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/messages/history/{other_user_id}")
def get_chat_history(other_user_id: int, user_id: int):
    """Get chat history between current user and another user"""
    db = SessionLocal()
    try:
        # Verify current user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        messages = db.query(DirectMessage).filter(
            ((DirectMessage.sender_id == user_id) & (DirectMessage.receiver_id == other_user_id)) |
            ((DirectMessage.sender_id == other_user_id) & (DirectMessage.receiver_id == user_id))
        ).order_by(DirectMessage.created_at.asc()).all()
        
        history = []
        for msg in messages:
            msg_dict = {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "message_text": msg.message_text,
                "shared_post_id": msg.shared_post_id,
                "created_at": msg.created_at.isoformat(),
                "is_read": msg.is_read,
                "shared_post": None
            }
            
            # If shared post is attached, load its details
            if msg.shared_post_id:
                post = db.query(Post).filter(Post.id == msg.shared_post_id, Post.is_deleted == False).first()
                if post:
                    post_author = db.query(User).filter(User.id == post.user_id).first()
                    msg_dict["shared_post"] = {
                        "id": post.id,
                        "user_id": post.user_id,
                        "user_email": post_author.email if post_author else "Unknown",
                        "content": post.content,
                        "image_url": post.image_url,
                        "video_url": post.video_url,
                        "created_at": post.created_at.isoformat()
                    }
            history.append(msg_dict)
            
        # Automatically mark incoming messages as read
        incoming_unread = db.query(DirectMessage).filter(
            DirectMessage.sender_id == other_user_id,
            DirectMessage.receiver_id == user_id,
            DirectMessage.is_read == False
        ).all()
        if incoming_unread:
            for msg in incoming_unread:
                msg.is_read = True
            db.commit()
            
        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/messages/chats")
def get_user_chats(user_id: int):
    """Get active conversation list for the sidebar"""
    db = SessionLocal()
    try:
        # Find all unique user IDs we have exchanged messages with
        sent_to = db.query(DirectMessage.receiver_id).filter(DirectMessage.sender_id == user_id).distinct().all()
        received_from = db.query(DirectMessage.sender_id).filter(DirectMessage.receiver_id == user_id).distinct().all()
        
        chat_user_ids = {u[0] for u in sent_to}.union({u[0] for u in received_from})
        
        chats_list = []
        for other_id in chat_user_ids:
            other_user = db.query(User).filter(User.id == other_id).first()
            if not other_user:
                continue
                
            # Get latest message
            latest_msg = db.query(DirectMessage).filter(
                ((DirectMessage.sender_id == user_id) & (DirectMessage.receiver_id == other_id)) |
                ((DirectMessage.sender_id == other_id) & (DirectMessage.receiver_id == user_id))
            ).order_by(DirectMessage.created_at.desc()).first()
            
            unread_count = db.query(DirectMessage).filter(
                DirectMessage.sender_id == other_id,
                DirectMessage.receiver_id == user_id,
                DirectMessage.is_read == False
            ).count()
            
            chats_list.append({
                "user_id": other_user.id,
                "email": other_user.email,
                "threat_score": other_user.threat_score,
                "status": other_user.status,
                "role": other_user.role,
                "unread_count": unread_count,
                "latest_message": {
                    "text": latest_msg.message_text if latest_msg else "",
                    "is_share": latest_msg.shared_post_id is not None if latest_msg else False,
                    "created_at": latest_msg.created_at.isoformat() if latest_msg else None,
                    "sender_id": latest_msg.sender_id if latest_msg else None
                }
            })
            
        # Sort chats by latest message time
        chats_list.sort(key=lambda x: x["latest_message"]["created_at"] or "", reverse=True)
        return chats_list
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.post("/api/messages/read/{message_id}")
def mark_message_read(message_id: int):
    """Mark a direct message as read"""
    db = SessionLocal()
    try:
        msg = db.query(DirectMessage).filter(DirectMessage.id == message_id).first()
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found")
        msg.is_read = True
        db.commit()
        return {"message_id": message_id, "is_read": True}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

