# Video Call Feature - Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies
```bash
cd app
pip install -r requirements.txt
```

### 2. Update Your Database
The new VideoCall and CallHistory tables will be automatically created when you start the application.

### 3. Start the Application
```bash
python main.py
# or
uvicorn main:app --reload
```

### 4. Access Video Call Interface
- Open browser to: `http://localhost:8000/video-call`
- You should see a call setup form

## 📱 Basic Usage

### Making a Call
1. Enter your User ID (e.g., 1)
2. Enter Recipient's User ID (e.g., 2)
3. Click **"Start Call"**
4. Recipient will see a call interface with **"Accept"** button
5. Recipient clicks **"Accept"**
6. Video call begins!

### During the Call
- 🎤 **Audio**: Toggle microphone on/off
- 📹 **Video**: Toggle camera on/off
- 🖥️ **Share**: Share your screen
- 💬 **Chat**: Send text messages
- ✕ **End**: Hang up the call

### Call Statistics
Real-time metrics visible on the right sidebar:
- **Bitrate**: Data transmission speed
- **Packet Loss**: Lost data percentage
- **Latency**: Connection delay
- **Quality**: Call quality estimate

## 🔧 Testing (Local)

### Test with 2 Browser Windows

**Window 1:**
```
User ID: 1
Recipient ID: 2
Click "Start Call"
```

**Window 2:**
```
Wait for call interface
Click "Accept Call"
```

Both should now see video (if camera enabled) and can communicate.

## 📊 Features Included

### Core Features
- ✅ Real-time video/audio
- ✅ Peer-to-peer connection
- ✅ WebSocket signaling
- ✅ Call history tracking
- ✅ Quality monitoring
- ✅ Screen sharing
- ✅ In-call chat

### Security
- ✅ User ID verification
- ✅ Blocked user prevention
- ✅ Call participant validation
- ✅ WebSocket authentication

### Statistics & Monitoring
- ✅ Bitrate tracking
- ✅ Packet loss detection
- ✅ Latency measurement
- ✅ Quality estimation
- ✅ Call duration tracking

## 📡 API Endpoints

### Initiate a Call
```bash
POST /api/initiate-call
Content-Type: application/json

{
    "caller_id": 1,
    "callee_id": 2
}
```

### Accept a Call
```bash
POST /api/accept-call/{call_id}
```

### End/Reject a Call
```bash
POST /api/reject-call/{call_id}
```

### Get Call History
```bash
GET /api/call-history/{user_id}
```

### Access Video Call UI
```
GET /video-call
```

## 🌐 WebSocket Connection

Automatic connection to signaling server:
```
ws://localhost:8000/ws/video-call/{call_id}/{user_id}
```

The frontend automatically handles this connection.

## 🔌 Configuration Options

### Disable Features (in video_call.html)
```javascript
// Hide screen share button
elements.shareScreen.style.display = 'none';

// Disable chat
elements.chatInput.disabled = true;

// Set default video quality
{ video: { width: { ideal: 640 }, height: { ideal: 480 } } }
```

### Add TURN Servers (for better firewall traversal)
In `video_call.html`, modify CONFIG:
```javascript
const CONFIG = {
    iceServers: [
        { urls: ['stun:stun.l.google.com:19302'] },
        { 
            urls: ['turn:your-server.com:3478'],
            username: 'user',
            credential: 'password'
        }
    ]
};
```

## 🐛 Common Issues & Solutions

### "Camera/Microphone not working"
1. Check browser permissions
2. Ensure camera/mic not used elsewhere
3. Refresh browser
4. Check browser console for errors

### "No remote video"
1. Wait for remote user to connect
2. Check their camera is enabled
3. Verify both on same network (or have internet)
4. Check connection status in sidebar

### "Audio problems"
1. Check microphone is unmuted
2. Adjust system volume
3. Disable noise cancellation
4. Check speaker volume

### "Connection fails"
1. Verify user IDs are correct
2. Check both users exist in database
3. Ensure neither user is blocked
4. Check internet connection
5. Look at browser console logs

## 📈 Monitoring Calls

### Check Call History (via API)
```bash
curl http://localhost:8000/api/call-history/1
```

### Database Queries
```sql
-- View all active calls
SELECT * FROM video_calls WHERE status = 'ongoing';

-- Get user's call history
SELECT * FROM call_history WHERE caller_id = 1 ORDER BY start_time DESC;

-- Call statistics
SELECT 
    caller_id,
    COUNT(*) as total_calls,
    AVG(duration) as avg_duration
FROM call_history
GROUP BY caller_id;
```

## 🔐 Security Notes

1. **Only verified users** can initiate calls
2. **Blocked users** cannot call or receive calls
3. **User IDs must exist** in the database
4. **WebSocket validates** call participation
5. **No media relay** - peer-to-peer only (private)

## 📱 Mobile Support

The interface is responsive and works on mobile:
- iPhone/iPad (Safari)
- Android (Chrome, Firefox)
- Requires camera/microphone permissions

## ⚙️ Advanced Configuration

### Increase Video Quality
```javascript
{ 
    video: { 
        width: { ideal: 1920 }, 
        height: { ideal: 1080 },
        frameRate: { ideal: 30 }
    } 
}
```

### Enable Noise Cancellation
```javascript
audio: { 
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true
}
```

### Set Up Scalable Infrastructure
1. Add Redis for call state caching
2. Deploy TURN server for firewall traversal
3. Use load balancer for multiple FastAPI instances
4. Implement call recording service
5. Add metrics/monitoring

## 📞 Sample Workflow

```
1. User A logs in (ID: 1)
2. User B logs in (ID: 2)
3. User A goes to /video-call
4. User A enters: caller_id=1, callee_id=2
5. User A clicks "Start Call"
6. Server creates VideoCall record (ID: 123, status: pending)
7. WebSocket connection established
8. Server creates CallConnection
9. User A creates SDP offer
10. User B sees call interface with "Accept" button
11. User B clicks "Accept"
12. Server updates status to "ongoing"
13. User B creates SDP answer
14. Both exchange ICE candidates
15. Media streams connected
16. Video appears on both sides
17. Real-time statistics displayed
18. Users can chat, share screen, toggle audio/video
19. When done, click "End Call"
20. Server saves CallHistory record
21. Streams closed, WebSocket disconnected
```

## 🆘 Get Help

### Check Logs
```bash
# View FastAPI logs
python main.py
# Look for any error messages

# Browser console
F12 -> Console tab
Look for WebRTC or WebSocket errors
```

### Debug Mode
```python
# In main.py, add at the start:
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎉 You're Ready!

Your video call feature is now ready to use! 

Start by testing locally with two browser windows, then scale up to production with proper TURN server setup and SSL/TLS certificates.

For questions or customization, refer to `VIDEO_CALL_IMPLEMENTATION.md` for detailed technical documentation.

---

**Happy calling! 📹**
