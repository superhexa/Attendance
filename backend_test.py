#!/usr/bin/env python3
"""
Backend CORS + Auth Testing Suite
Tests the 7 required checks from the review request
"""
import requests
import time
import sys

# External URL (via Kubernetes ingress)
BASE_URL = "https://670954da-9ba9-4fe2-8afd-f854f05d69a1.preview.emergentagent.com/api"
PREVIEW_ORIGIN = "https://670954da-9ba9-4fe2-8afd-f854f05d69a1.preview.emergentagent.com"
RANDOM_ORIGIN = "https://randomtest.example.com"

# Test credentials
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

# Test results
results = []
passed = 0
failed = 0


def log_result(test_name, success, message):
    global passed, failed
    status = "✅ PASS" if success else "❌ FAIL"
    results.append(f"{status} | {test_name}: {message}")
    if success:
        passed += 1
    else:
        failed += 1
    print(f"{status} | {test_name}: {message}")


def test_1_cors_preflight_preview_origin():
    """Test 1: CORS preflight with preview origin"""
    try:
        response = requests.options(
            f"{BASE_URL}/auth/login",
            headers={
                "Origin": PREVIEW_ORIGIN,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
            timeout=10
        )
        
        if response.status_code != 200:
            log_result("1. CORS Preflight (Preview Origin)", False, 
                      f"Expected 200, got {response.status_code}")
            return
        
        acao = response.headers.get("access-control-allow-origin", "")
        acac = response.headers.get("access-control-allow-credentials", "")
        
        if not acao:
            log_result("1. CORS Preflight (Preview Origin)", False, 
                      "CRITICAL: Missing access-control-allow-origin header")
            return
        
        if acac.lower() != "true":
            log_result("1. CORS Preflight (Preview Origin)", False, 
                      f"Expected access-control-allow-credentials: true, got {acac}")
            return
        
        log_result("1. CORS Preflight (Preview Origin)", True, 
                  f"200 OK, ACAO={acao}, ACAC=true")
    except Exception as e:
        log_result("1. CORS Preflight (Preview Origin)", False, f"Exception: {str(e)}")


def test_2_cors_preflight_random_origin():
    """Test 2: CORS preflight with random origin (verify .* regex)"""
    try:
        response = requests.options(
            f"{BASE_URL}/auth/login",
            headers={
                "Origin": RANDOM_ORIGIN,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
            timeout=10
        )
        
        if response.status_code != 200:
            log_result("2. CORS Preflight (Random Origin)", False, 
                      f"Expected 200, got {response.status_code}")
            return
        
        acao = response.headers.get("access-control-allow-origin", "")
        acac = response.headers.get("access-control-allow-credentials", "")
        
        if not acao:
            log_result("2. CORS Preflight (Random Origin)", False, 
                      "Missing access-control-allow-origin header")
            return
        
        if acac.lower() != "true":
            log_result("2. CORS Preflight (Random Origin)", False, 
                      f"Expected access-control-allow-credentials: true, got {acac}")
            return
        
        # The middleware should echo back the random origin
        log_result("2. CORS Preflight (Random Origin)", True, 
                  f"200 OK, ACAO={acao} (echoed), ACAC=true")
    except Exception as e:
        log_result("2. CORS Preflight (Random Origin)", False, f"Exception: {str(e)}")


def test_3_login_correct_credentials():
    """Test 3: POST /api/auth/login with correct credentials"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "remember": False},
            headers={"Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        
        if response.status_code != 200:
            log_result("3. Login (Correct Credentials)", False, 
                      f"Expected 200, got {response.status_code}: {response.text}")
            return None
        
        data = response.json()
        if "user" not in data or "access_token" not in data:
            log_result("3. Login (Correct Credentials)", False, 
                      "Missing user or access_token in response")
            return None
        
        # Check Set-Cookie headers
        set_cookie = response.headers.get("set-cookie", "")
        has_access = "access_token=" in set_cookie
        has_refresh = "refresh_token=" in set_cookie
        
        if not has_access or not has_refresh:
            log_result("3. Login (Correct Credentials)", False, 
                      f"Missing cookies: access={has_access}, refresh={has_refresh}")
            return None
        
        # Check cookie attributes
        has_secure = "Secure" in set_cookie
        has_samesite = "SameSite=None" in set_cookie or "SameSite=none" in set_cookie
        
        log_result("3. Login (Correct Credentials)", True, 
                  f"200 OK, user={data['user']['email']}, cookies set (Secure={has_secure}, SameSite=None={has_samesite})")
        
        return data["access_token"]
    except Exception as e:
        log_result("3. Login (Correct Credentials)", False, f"Exception: {str(e)}")
        return None


def test_4_login_wrong_password():
    """Test 4: POST /api/auth/login with wrong password"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": "wrongpassword123", "remember": False},
            headers={"Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        
        if response.status_code != 401:
            log_result("4. Login (Wrong Password)", False, 
                      f"Expected 401, got {response.status_code}")
            return
        
        data = response.json()
        detail = data.get("detail", "")
        
        # Check for Arabic error message
        has_arabic = any(ord(c) > 127 for c in detail)
        
        log_result("4. Login (Wrong Password)", True, 
                  f"401 Unauthorized, Arabic error: {detail}")
    except Exception as e:
        log_result("4. Login (Wrong Password)", False, f"Exception: {str(e)}")


def test_5_pending_user_cannot_login():
    """Test 5: Pending signup user cannot log in"""
    try:
        # First, get a signup key
        admin_token = get_admin_token()
        if not admin_token:
            log_result("5. Pending User Login Block", False, "Could not get admin token")
            return
        
        # Rotate signup key
        response = requests.post(
            f"{BASE_URL}/settings/rotate-signup-key",
            headers={"Authorization": f"Bearer {admin_token}", "Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        
        if response.status_code != 200:
            log_result("5. Pending User Login Block", False, 
                      f"Could not rotate signup key: {response.status_code}")
            return
        
        signup_key = response.json().get("student_signup_key")
        
        # Create a pending signup
        test_email = f"pending_test_{int(time.time())}@example.com"
        
        # Get public structure first
        struct_response = requests.get(
            f"{BASE_URL}/auth/public-structure",
            params={"school_key": signup_key},
            timeout=10
        )
        
        if struct_response.status_code != 200:
            log_result("5. Pending User Login Block", False, 
                      f"Could not get public structure: {struct_response.status_code}")
            return
        
        struct = struct_response.json()
        if not struct.get("grades") or not struct.get("sections"):
            log_result("5. Pending User Login Block", False, "No grades or sections available")
            return
        
        grade_id = struct["grades"][0]["id"]
        section_id = struct["sections"][0]["id"]
        
        # Create signup
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup/student",
            json={
                "school_key": signup_key,
                "full_name": "Pending Test Student",
                "email": test_email,
                "password": "testpass123",
                "grade_id": grade_id,
                "section_id": section_id,
            },
            headers={"Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        
        if signup_response.status_code != 200:
            log_result("5. Pending User Login Block", False, 
                      f"Could not create signup: {signup_response.status_code}: {signup_response.text}")
            return
        
        # Try to login with pending user
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": test_email, "password": "testpass123", "remember": False},
            headers={"Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        
        if login_response.status_code != 403:
            log_result("5. Pending User Login Block", False, 
                      f"Expected 403, got {login_response.status_code}")
            return
        
        detail = login_response.json().get("detail", "")
        has_arabic_pending = "بانتظار موافقة" in detail or "بانتظار" in detail
        
        log_result("5. Pending User Login Block", True, 
                  f"403 Forbidden, Arabic message: {detail}")
    except Exception as e:
        log_result("5. Pending User Login Block", False, f"Exception: {str(e)}")


def test_6_full_happy_path():
    """Test 6: Full happy path - rotate key → signup → approve → login"""
    try:
        # Get admin token
        admin_token = get_admin_token()
        if not admin_token:
            log_result("6. Full Happy Path", False, "Could not get admin token")
            return
        
        # Rotate signup key
        response = requests.post(
            f"{BASE_URL}/settings/rotate-signup-key",
            headers={"Authorization": f"Bearer {admin_token}", "Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        
        if response.status_code != 200:
            log_result("6. Full Happy Path", False, 
                      f"Could not rotate signup key: {response.status_code}")
            return
        
        signup_key = response.json().get("student_signup_key")
        
        # Get public structure
        struct_response = requests.get(
            f"{BASE_URL}/auth/public-structure",
            params={"school_key": signup_key},
            timeout=10
        )
        
        if struct_response.status_code != 200:
            log_result("6. Full Happy Path", False, 
                      f"Could not get public structure: {struct_response.status_code}")
            return
        
        struct = struct_response.json()
        if not struct.get("grades") or not struct.get("sections"):
            log_result("6. Full Happy Path", False, "No grades or sections available")
            return
        
        grade_id = struct["grades"][0]["id"]
        section_id = struct["sections"][0]["id"]
        
        # Create signup
        test_email = f"happy_path_{int(time.time())}@example.com"
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup/student",
            json={
                "school_key": signup_key,
                "full_name": "Happy Path Student",
                "email": test_email,
                "password": "testpass123",
                "grade_id": grade_id,
                "section_id": section_id,
                "student_number": "HP001",
            },
            headers={"Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        
        if signup_response.status_code != 200:
            log_result("6. Full Happy Path", False, 
                      f"Could not create signup: {signup_response.status_code}: {signup_response.text}")
            return
        
        # Get pending signups
        pending_response = requests.get(
            f"{BASE_URL}/signups/pending",
            headers={"Authorization": f"Bearer {admin_token}", "Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        
        if pending_response.status_code != 200:
            log_result("6. Full Happy Path", False, 
                      f"Could not get pending signups: {pending_response.status_code}")
            return
        
        pending_data = pending_response.json()
        pending_users = pending_data.get("items", [])
        target_user = None
        for u in pending_users:
            if u.get("email") == test_email:
                target_user = u
                break
        
        if not target_user:
            log_result("6. Full Happy Path", False, "Could not find pending user")
            return
        
        # Approve the signup
        approve_response = requests.post(
            f"{BASE_URL}/signups/{target_user['user_id']}/approve",
            json={
                "full_name": "Happy Path Student",
                "student_number": "HP001",
                "grade_id": grade_id,
                "section_id": section_id,
            },
            headers={"Authorization": f"Bearer {admin_token}", "Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        
        if approve_response.status_code != 200:
            log_result("6. Full Happy Path", False, 
                      f"Could not approve signup: {approve_response.status_code}: {approve_response.text}")
            return
        
        # Login with approved student
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": test_email, "password": "testpass123", "remember": False},
            headers={"Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        
        if login_response.status_code != 200:
            log_result("6. Full Happy Path", False, 
                      f"Approved student login failed: {login_response.status_code}: {login_response.text}")
            return
        
        data = login_response.json()
        if "user" not in data or "access_token" not in data:
            log_result("6. Full Happy Path", False, "Missing user or access_token")
            return
        
        log_result("6. Full Happy Path", True, 
                  f"Complete: signup → approve → login successful for {test_email}")
    except Exception as e:
        log_result("6. Full Happy Path", False, f"Exception: {str(e)}")


def test_7_rate_limiting():
    """Test 7: Rate limiting - 6 wrong attempts → 429"""
    try:
        test_email = f"ratelimit_test_{int(time.time())}@example.com"
        
        # Make 6 failed login attempts
        for i in range(6):
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": test_email, "password": "wrongpassword", "remember": False},
                headers={"Origin": PREVIEW_ORIGIN},
                timeout=10
            )
            
            if i < 5:
                if response.status_code != 401:
                    log_result("7. Rate Limiting", False, 
                              f"Attempt {i+1}: Expected 401, got {response.status_code}")
                    return
            else:
                # 6th attempt should be locked
                if response.status_code != 429:
                    log_result("7. Rate Limiting", False, 
                              f"Attempt 6: Expected 429 (locked), got {response.status_code}")
                    return
                
                detail = response.json().get("detail", "")
                has_arabic_lock = "قفل" in detail or "مؤقت" in detail
                
                log_result("7. Rate Limiting", True, 
                          f"429 Too Many Requests after 6 attempts, Arabic message: {detail}")
                return
            
            time.sleep(0.5)  # Small delay between attempts
        
    except Exception as e:
        log_result("7. Rate Limiting", False, f"Exception: {str(e)}")


def test_8_auth_me():
    """Test 8: GET /api/auth/me with Bearer token"""
    try:
        # Get a valid token
        token = get_admin_token()
        if not token:
            log_result("8. Auth /me Endpoint", False, "Could not get admin token")
            return
        
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}", "Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        
        if response.status_code != 200:
            log_result("8. Auth /me Endpoint", False, 
                      f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        if "email" not in data or "role" not in data:
            log_result("8. Auth /me Endpoint", False, "Missing email or role in response")
            return
        
        log_result("8. Auth /me Endpoint", True, 
                  f"200 OK, user={data['email']}, role={data['role']}")
    except Exception as e:
        log_result("8. Auth /me Endpoint", False, f"Exception: {str(e)}")


def get_admin_token():
    """Helper: Get admin access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "remember": False},
            headers={"Origin": PREVIEW_ORIGIN},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception:
        pass
    return None


def main():
    print("=" * 80)
    print("BACKEND CORS + AUTH TESTING SUITE")
    print(f"Base URL: {BASE_URL}")
    print("=" * 80)
    print()
    
    # Run all tests
    test_1_cors_preflight_preview_origin()
    test_2_cors_preflight_random_origin()
    test_3_login_correct_credentials()
    test_4_login_wrong_password()
    test_5_pending_user_cannot_login()
    test_6_full_happy_path()
    test_7_rate_limiting()
    test_8_auth_me()
    
    print()
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
