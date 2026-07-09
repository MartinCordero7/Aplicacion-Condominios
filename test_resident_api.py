import requests

API_URL = "https://condominio-api-2aef.onrender.com/api/v1"

# Try getting without token
print("Trying to get /residentes without token...")
try:
    r = requests.get(f"{API_URL}/residentes", timeout=15)
    print("Without token status:", r.status_code)
    print("Without token body:", r.text[:200])
except Exception as e:
    print("Without token error:", e)

# Try login
print("\nTrying to login...")
try:
    r = requests.post(f"{API_URL}/auth/login", json={"username": "admin", "password": "password"}, timeout=15)
    print("Login status:", r.status_code)
    if r.status_code in [200, 201]:
        token = r.json().get('data', {}).get('accessToken')
        print("Obtained token:", token[:20] + "..." if token else "None")
        
        # Try getting with token
        headers = {"Authorization": f"Bearer {token}"}
        print("\nTrying to get /residentes with token...")
        r2 = requests.get(f"{API_URL}/residentes", headers=headers, timeout=15)
        print("With token status:", r2.status_code)
        print("With token body:", r2.text[:500])
    else:
        print("Login body:", r.text)
except Exception as e:
    print("Login error:", e)
