import json
import urllib.request

base = 'http://127.0.0.1:8000'

# Test signup
print("Testing Sign Up...")
signup_data = json.dumps({
    "email": "testuser@example.com",
    "phone": "1234567890",
    "password": "password123"
}).encode('utf-8')

req = urllib.request.Request(
    base + '/signup',
    data=signup_data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"✓ Signup: {resp.status}")
        data = json.loads(resp.read().decode())
        print(f"  Token: {data['access_token'][:20]}...")
except Exception as e:
    print(f"✗ Signup failed: {e}")

# Test login
print("\nTesting Login...")
login_data = json.dumps({
    "email": "admin@example.com",
    "password": "password"
}).encode('utf-8')

req = urllib.request.Request(
    base + '/login',
    data=login_data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"✓ Login: {resp.status}")
        data = json.loads(resp.read().decode())
        print(f"  Token: {data['access_token'][:20]}...")
except Exception as e:
    print(f"✗ Login failed: {e}")

# Test forgot password
print("\nTesting Forgot Password...")
forgot_data = json.dumps({
    "email": "admin@example.com"
}).encode('utf-8')

req = urllib.request.Request(
    base + '/forgot-password',
    data=forgot_data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"✓ Forgot Password: {resp.status}")
        data = json.loads(resp.read().decode())
        print(f"  Reset URL: {data['reset_url']}")
except Exception as e:
    print(f"✗ Forgot Password failed: {e}")

# Test analyze
print("\nTesting Analyze...")
analyze_data = json.dumps({
    "user_id": 1,
    "comment": "This is a test"
}).encode('utf-8')

req = urllib.request.Request(
    base + '/analyze',
    data=analyze_data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"✓ Analyze: {resp.status}")
        data = json.loads(resp.read().decode())
        print(f"  Level: {data['level']}, Score: {data['score']:.4f}, Action: {data['action']}")
except Exception as e:
    print(f"✗ Analyze failed: {e}")

# Test admin stats
print("\nTesting Admin Stats...")
req = urllib.request.Request(base + '/admin/stats')

try:
    with urllib.request.urlopen(req) as resp:
        print(f"✓ Admin Stats: {resp.status}")
        data = json.loads(resp.read().decode())
        print(f"  Total Users: {data['total_users']}, Blocked: {data['blocked_users']}, Blacklisted: {data['blacklisted_users']}")
except Exception as e:
    print(f"✗ Admin Stats failed: {e}")

print("\n✅ All tests completed!")
