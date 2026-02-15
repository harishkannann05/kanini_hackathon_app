"""Test patient my-records endpoint with token"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Register a patient
print("1. Registering test patient...")
register_data = {
    "email": "testpatient@test.com",
    "password": "testpass123",
    "full_name": "Test Patient",
    "role": "Patient"
}
r = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   Error: {r.text}")
else:
    print(f"   ✓ Registered")

# Login
print("\n2. Logging in...")
login_data = {
    "email": "testpatient@test.com",
    "password": "testpass123"
}
r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   Error: {r.text}")
else:
    token = r.json().get("access_token")
    print(f"   ✓ Got token: {token[:20]}...")
    
    # Test my-records endpoint
    print("\n3. Testing /patient/my-records...")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/patient/my-records", headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {json.dumps(r.json(), indent=2)}")
