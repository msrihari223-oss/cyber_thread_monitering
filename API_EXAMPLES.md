# Video Call API Examples & Usage

## 🔧 Quick API Examples

### 1. Initiate a Video Call

**Endpoint**: `POST /api/initiate-call`

**Request**:
```bash
curl -X POST http://localhost:8000/api/initiate-call \
  -H "Content-Type: application/json" \
  -d '{
    "caller_id": 1,
    "callee_id": 2
  }'
```

**Python Example**:
```python
import requests

response = requests.post(
    'http://localhost:8000/api/initiate-call',
    json={
        'caller_id': 1,
        'callee_id': 2
    }
)

call_data = response.json()
print(f"Call ID: {call_data['call_id']}")
print(f"Status: {call_data['status']}")
```

**JavaScript Example**:
```javascript
const response = await fetch('/api/initiate-call', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        caller_id: 1,
        callee_id: 2
    })
});

const callData = await response.json();
console.log('Call ID:', callData.call_id);
```

**Expected Response**:
```json
{
    "call_id": 123,
    "caller_id": 1,
    "callee_id": 2,
    "status": "pending",
    "message": "Call initiated"
}
```

---

### 2. Accept a Call

**Endpoint**: `POST /api/accept-call/{call_id}`

**Request**:
```bash
curl -X POST http://localhost:8000/api/accept-call/123
```

**Python Example**:
```python
call_id = 123
response = requests.post(f'http://localhost:8000/api/accept-call/{call_id}')
result = response.json()
print(f"Call accepted: {result['message']}")
```

**JavaScript Example**:
```javascript
const callId = 123;
const response = await fetch(`/api/accept-call/${callId}`, {
    method: 'POST'
});
const result = await response.json();
console.log('Result:', result);
```

**Expected Response**:
```json
{
    "call_id": 123,
    "status": "ongoing",
    "message": "Call accepted"
}
```

---

### 3. End/Reject a Call

**Endpoint**: `POST /api/reject-call/{call_id}`

**Request**:
```bash
curl -X POST http://localhost:8000/api/reject-call/123
```

**Python Example**:
```python
call_id = 123
response = requests.post(f'http://localhost:8000/api/reject-call/{call_id}')
result = response.json()
print(f"Call status: {result['status']}")
```

**Expected Response**:
```json
{
    "call_id": 123,
    "status": "ended",
    "message": "Call ended"
}
```

---

### 4. Get Call History

**Endpoint**: `GET /api/call-history/{user_id}`

**Request**:
```bash
curl http://localhost:8000/api/call-history/1
```

**Python Example**:
```python
user_id = 1
response = requests.get(f'http://localhost:8000/api/call-history/{user_id}')
history = response.json()

print(f"Total calls: {history['call_count']}")
for call in history['calls']:
    print(f"  - {call['caller_id']} → {call['callee_id']}: {call['duration']}s")
```

**JavaScript Example**:
```javascript
const userId = 1;
const response = await fetch(`/api/call-history/${userId}`);
const history = await response.json();

history.calls.forEach(call => {
    console.log(`${call.status}: ${call.duration} seconds`);
});
```

**Expected Response**:
```json
{
    "user_id": 1,
    "call_count": 3,
    "calls": [
        {
            "caller_id": 1,
            "callee_id": 2,
            "call_type": "video",
            "start_time": "2026-06-01T10:30:00",
            "end_time": "2026-06-01T10:35:00",
            "duration": 300,
            "status": "completed"
        },
        {
            "caller_id": 1,
            "callee_id": 3,
            "call_type": "video",
            "start_time": "2026-06-01T11:00:00",
            "end_time": "2026-06-01T11:02:00",
            "duration": 120,
            "status": "completed"
        },
        {
            "caller_id": 1,
            "callee_id": 4,
            "call_type": "video",
            "start_time": "2026-06-01T11:30:00",
            "end_time": "2026-06-01T11:30:00",
            "duration": 0,
            "status": "rejected"
        }
    ]
}
```

---

## 🌐 WebSocket Examples

### Connect to WebSocket

**Endpoint**: `ws://localhost:8000/ws/video-call/{call_id}/{user_id}`

**JavaScript Example**:
```javascript
const callId = 123;
const userId = 1;

const ws = new WebSocket(
    `ws://localhost:8000/ws/video-call/${callId}/${userId}`
);

ws.onopen = () => {
    console.log('WebSocket connected');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data.type);
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('WebSocket disconnected');
};
```

### Send SDP Offer

```javascript
// Create and send offer
const offer = await peerConnection.createOffer();
await peerConnection.setLocalDescription(offer);

ws.send(JSON.stringify({
    type: 'offer',
    sdp: offer.sdp
}));
```

### Send SDP Answer

```javascript
// Create and send answer
const answer = await peerConnection.createAnswer();
await peerConnection.setLocalDescription(answer);

ws.send(JSON.stringify({
    type: 'answer',
    sdp: answer.sdp
}));
```

### Send ICE Candidate

```javascript
peerConnection.onicecandidate = (event) => {
    if (event.candidate) {
        ws.send(JSON.stringify({
            type: 'ice_candidate',
            candidate: event.candidate
        }));
    }
};
```

---

## 💻 Complete Integration Example

### Full Video Call Flow

```python
# 1. Get users from database
user1_id = 1
user2_id = 2

# 2. Initiate call
import requests
call_response = requests.post(
    'http://localhost:8000/api/initiate-call',
    json={'caller_id': user1_id, 'callee_id': user2_id}
)
call_data = call_response.json()
call_id = call_data['call_id']
print(f"Call initiated with ID: {call_id}")

# 3. Check call status
import time
time.sleep(2)

# 4. Accept call (user 2)
accept_response = requests.post(
    f'http://localhost:8000/api/accept-call/{call_id}'
)
print(f"Call accepted: {accept_response.json()}")

# 5. Simulate call duration
time.sleep(5)

# 6. End call
end_response = requests.post(
    f'http://localhost:8000/api/reject-call/{call_id}'
)
print(f"Call ended: {end_response.json()}")

# 7. Get call history
history_response = requests.get(
    f'http://localhost:8000/api/call-history/{user1_id}'
)
history = history_response.json()
print(f"Total calls for user {user1_id}: {history['call_count']}")

# Print latest call details
if history['calls']:
    latest = history['calls'][0]
    print(f"Latest call: {latest['status']}, Duration: {latest['duration']}s")
```

---

## 🧪 Testing with cURL

### Test Scenario

```bash
#!/bin/bash

# Start call from user 1 to user 2
echo "1. Initiating call..."
CALL_RESPONSE=$(curl -s -X POST http://localhost:8000/api/initiate-call \
  -H "Content-Type: application/json" \
  -d '{"caller_id": 1, "callee_id": 2}')

CALL_ID=$(echo $CALL_RESPONSE | grep -o '"call_id":[0-9]*' | grep -o '[0-9]*')
echo "Call ID: $CALL_ID"
echo "Response: $CALL_RESPONSE"

# Wait a bit
echo "2. Waiting for user 2 to accept..."
sleep 2

# Accept call as user 2
echo "3. Accepting call..."
curl -s -X POST http://localhost:8000/api/accept-call/$CALL_ID | jq .

# Simulate call duration
echo "4. Call active..."
sleep 5

# End call
echo "5. Ending call..."
curl -s -X POST http://localhost:8000/api/reject-call/$CALL_ID | jq .

# Get call history
echo "6. Retrieving call history..."
curl -s http://localhost:8000/api/call-history/1 | jq .
```

---

## 📊 Database Query Examples

### Get All Active Calls

```sql
SELECT id, caller_id, callee_id, status, start_time 
FROM video_calls 
WHERE status = 'ongoing' 
ORDER BY start_time DESC;
```

### Get User's Call History

```sql
SELECT * FROM call_history 
WHERE caller_id = 1 OR callee_id = 1 
ORDER BY start_time DESC 
LIMIT 10;
```

### Get Call Statistics

```sql
SELECT 
    caller_id,
    COUNT(*) as total_calls,
    AVG(duration) as avg_duration,
    SUM(duration) as total_minutes,
    MAX(duration) as longest_call
FROM call_history 
WHERE caller_id = 1
GROUP BY caller_id;
```

### Find Missed Calls

```sql
SELECT * FROM call_history 
WHERE (caller_id = 1 OR callee_id = 1) 
  AND status = 'rejected' 
ORDER BY start_time DESC;
```

### Get Call Quality Stats

```sql
SELECT 
    call_quality,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()) as percentage
FROM video_calls 
GROUP BY call_quality;
```

---

## 🔍 Monitoring & Debugging

### Monitor Active WebSocket Connections

```python
# Add to backend for monitoring
from fastapi import FastAPI
from fastapi.responses import JSONResponse

@app.get("/api/call-stats")
def get_call_stats():
    active_calls = len(video_call_manager.calls)
    active_connections = sum(
        1 for call in video_call_manager.calls.values() 
        if call.caller_websocket or call.callee_websocket
    )
    
    return {
        "active_calls": active_calls,
        "active_websockets": active_connections
    }
```

### Browser Console Debugging

```javascript
// Check connection state
console.log('Peer state:', peerConnection.connectionState);

// Log WebSocket messages
const originalSend = ws.send;
ws.send = function(data) {
    console.log('Sending:', JSON.parse(data));
    originalSend.call(ws, data);
};

ws.addEventListener('message', (event) => {
    console.log('Received:', JSON.parse(event.data));
});

// Get WebRTC stats
peerConnection.getStats().then(stats => {
    stats.forEach(report => {
        console.log(report.type, report);
    });
});
```

---

## 🎯 Error Handling Examples

### Handle Failed Call Initiation

```javascript
async function initiateCallWithRetry(callerId, calleeId, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch('/api/initiate-call', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    caller_id: callerId,
                    callee_id: calleeId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`Attempt ${i + 1} failed:`, error);
            if (i < maxRetries - 1) {
                await new Promise(r => setTimeout(r, 1000));
            }
        }
    }
    throw new Error('Failed after retries');
}
```

### Handle WebSocket Reconnection

```javascript
function createWebSocketWithReconnect(url, maxAttempts = 5) {
    let attempts = 0;
    
    function connect() {
        attempts++;
        const ws = new WebSocket(url);
        
        ws.onclose = () => {
            if (attempts < maxAttempts) {
                console.log(`Reconnecting... (${attempts}/${maxAttempts})`);
                setTimeout(connect, 1000 * attempts);
            } else {
                console.error('Max reconnection attempts reached');
            }
        };
        
        return ws;
    }
    
    return connect();
}
```

---

## 📈 Performance Testing

### Load Test Script

```bash
#!/bin/bash
# Simple load test - initiate multiple calls

for i in {1..10}; do
    caller=$((i + 1))
    callee=$(((i + 2) % 10))
    
    curl -X POST http://localhost:8000/api/initiate-call \
        -H "Content-Type: application/json" \
        -d "{\"caller_id\": $caller, \"callee_id\": $callee}" \
        &
done
wait
echo "Load test complete"
```

---

## ✅ Validation Checklist

- [ ] Can initiate call with valid user IDs
- [ ] Cannot call with invalid user IDs
- [ ] Cannot call to blocked users
- [ ] Blocked users cannot initiate calls
- [ ] Call history is recorded correctly
- [ ] Call duration is calculated accurately
- [ ] WebSocket connects successfully
- [ ] SDP offer/answer exchanged correctly
- [ ] ICE candidates processed properly
- [ ] Video/audio streams established
- [ ] Call can be ended gracefully
- [ ] Resources cleaned up after disconnect

---

**Ready to test!** Start with simple cURL examples, then integrate into your application.
