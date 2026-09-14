#!/usr/bin/env python3
"""
Backend regression test for auth bug fix (CORS + signup flow)
Tests all endpoints with the external HTTPS URL to validate CORS + Kubernetes ingress
"""
import requests
import time
import json
from typing import Optional

# Base URL - external HTTPS endpoint
BASE_URL = "https://670954da-9ba9-4fe2-8afd-f854f05d69a1.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

# Admin credentials
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

# Test state
admin_token = None
admin_cookies = None
student_signup_key = None
pending_student_user_id = None
pending_student_email = None
pending_student_password = None
approved_student_user_id = None
approved_student_email = None
approved_student_password = None
rejected_student_user_id = None
test_grade_id = None
test_section_id = None

def print_test(name: str):
    """Print test name"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print('='*80)

def print_pass(msg: str):
    """Print pass message"""
    print(f"✅ PASS: {msg}")

def print_fail(msg: str, details: Optional[str] = None):
    """Print fail message"""
    print(f"❌ FAIL: {msg}")
    if details:
        print(f"   Details: {details}")

def print_info(msg: str):
    """Print info message"""
    print(f"ℹ️  INFO: {msg}")

# ============================================================================
# TEST 1: LOGIN
# ============================================================================

def test_login_success():
    """Test successful login with admin credentials"""
    global admin_token, admin_cookies
    
    print_test("1.1 - Login with valid admin credentials")
    
    url = f"{API_BASE}/auth/login"
    payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "remember": False
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        # Check response body
        if "user" not in data:
            print_fail("Response missing 'user' field", json.dumps(data, indent=2))
            return False
        
        if "access_token" not in data:
            print_fail("Response missing 'access_token' field", json.dumps(data, indent=2))
            return False
        
        user = data["user"]
        if user.get("role") != "DIRECTOR":
            print_fail(f"Expected role DIRECTOR, got {user.get('role')}")
            return False
        
        # Check Set-Cookie headers
        cookies = resp.cookies
        if "access_token" not in cookies:
            print_fail("Missing access_token cookie")
            return False
        
        if "refresh_token" not in cookies:
            print_fail("Missing refresh_token cookie")
            return False
        
        admin_token = data["access_token"]
        admin_cookies = resp.cookies
        
        print_pass("Login successful with user object, access_token, and cookies")
        return True
        
    except Exception as e:
        print_fail(f"Exception during login: {str(e)}")
        return False


def test_login_wrong_password():
    """Test login with wrong password"""
    print_test("1.2 - Login with wrong password")
    
    url = f"{API_BASE}/auth/login"
    payload = {
        "email": ADMIN_EMAIL,
        "password": "wrongpassword123",
        "remember": False
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 401:
            print_fail(f"Expected 401, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        detail = data.get("detail", "")
        
        # Check for Arabic error message
        if not detail or len(detail) < 5:
            print_fail("Expected Arabic error message in detail field", json.dumps(data, indent=2))
            return False
        
        print_pass(f"Login rejected with 401 and Arabic message: {detail}")
        return True
        
    except Exception as e:
        print_fail(f"Exception during wrong password test: {str(e)}")
        return False


def test_cors_preflight():
    """Test CORS preflight request"""
    print_test("1.3 - CORS preflight OPTIONS request")
    
    url = f"{API_BASE}/auth/login"
    headers = {
        "Origin": BASE_URL,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"
    }
    
    try:
        resp = requests.options(url, headers=headers, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        # Check CORS headers
        allow_origin = resp.headers.get("Access-Control-Allow-Origin", "")
        allow_credentials = resp.headers.get("Access-Control-Allow-Credentials", "")
        
        print_info(f"Access-Control-Allow-Origin: {allow_origin}")
        print_info(f"Access-Control-Allow-Credentials: {allow_credentials}")
        
        # Note: Testing against localhost:8001 shows FastAPI CORS is configured correctly
        # The issue is with Kubernetes ingress stripping the Access-Control-Allow-Origin header
        # This is an infrastructure issue, not a backend code issue
        
        if allow_origin == "*":
            print_fail("CRITICAL: Access-Control-Allow-Origin is '*' (wildcard) - incompatible with credentials")
            print_info("NOTE: Backend CORS config is correct (tested on localhost:8001). Issue is with ingress/proxy.")
            return False
        
        if allow_origin != BASE_URL:
            print_fail(f"CRITICAL: Access-Control-Allow-Origin should echo exact origin. Expected: {BASE_URL}, Got: {allow_origin}")
            print_info("NOTE: Backend CORS config is correct (tested on localhost:8001). Issue is with ingress/proxy.")
            return False
        
        if allow_credentials.lower() != "true":
            print_fail(f"CRITICAL: Access-Control-Allow-Credentials should be 'true', got: {allow_credentials}")
            return False
        
        print_pass("CORS preflight returns exact origin with allow-credentials:true")
        return True
        
    except Exception as e:
        print_fail(f"Exception during CORS preflight test: {str(e)}")
        return False


def test_auth_me():
    """Test /api/auth/me endpoint"""
    print_test("1.4 - GET /api/auth/me with Bearer token")
    
    if not admin_token:
        print_fail("No admin token available (login test must pass first)")
        return False
    
    url = f"{API_BASE}/auth/me"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        if data.get("email") != ADMIN_EMAIL:
            print_fail(f"Expected email {ADMIN_EMAIL}, got {data.get('email')}")
            return False
        
        if data.get("role") != "DIRECTOR":
            print_fail(f"Expected role DIRECTOR, got {data.get('role')}")
            return False
        
        print_pass("GET /api/auth/me returns correct user info")
        return True
        
    except Exception as e:
        print_fail(f"Exception during /auth/me test: {str(e)}")
        return False


# ============================================================================
# TEST 2: SCHOOL KEY + SIGNUP GATE
# ============================================================================

def test_school_info():
    """Test GET /api/auth/school-info"""
    print_test("2.1 - GET /api/auth/school-info")
    
    url = f"{API_BASE}/auth/school-info"
    
    try:
        resp = requests.get(url, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        required_fields = ["school_name_ar", "school_name_en", "signup_enabled"]
        for field in required_fields:
            if field not in data:
                print_fail(f"Missing field: {field}", json.dumps(data, indent=2))
                return False
        
        print_info(f"signup_enabled: {data['signup_enabled']}")
        print_pass("GET /api/auth/school-info returns required fields")
        return True
        
    except Exception as e:
        print_fail(f"Exception during school-info test: {str(e)}")
        return False


def test_rotate_signup_key():
    """Test POST /api/settings/rotate-signup-key"""
    global student_signup_key
    
    print_test("2.2 - POST /api/settings/rotate-signup-key (as admin)")
    
    if not admin_token:
        print_fail("No admin token available")
        return False
    
    url = f"{API_BASE}/settings/rotate-signup-key"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    
    try:
        resp = requests.post(url, headers=headers, cookies=admin_cookies, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        if "student_signup_key" not in data:
            print_fail("Response missing 'student_signup_key'", json.dumps(data, indent=2))
            return False
        
        student_signup_key = data["student_signup_key"]
        print_info(f"Generated key: {student_signup_key}")
        
        print_pass("Signup key rotated successfully")
        return True
        
    except Exception as e:
        print_fail(f"Exception during rotate-signup-key test: {str(e)}")
        return False


def test_public_structure_invalid_key():
    """Test GET /api/auth/public-structure with invalid key"""
    print_test("2.3 - GET /api/auth/public-structure with INVALID key")
    
    url = f"{API_BASE}/auth/public-structure"
    params = {"school_key": "INVALID-KEY-1234"}
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 403:
            print_fail(f"Expected 403, got {resp.status_code}", resp.text)
            return False
        
        print_pass("Invalid school key rejected with 403")
        return True
        
    except Exception as e:
        print_fail(f"Exception during invalid key test: {str(e)}")
        return False


def test_public_structure_valid_key():
    """Test GET /api/auth/public-structure with valid key"""
    global test_grade_id, test_section_id
    
    print_test("2.4 - GET /api/auth/public-structure with VALID key")
    
    if not student_signup_key:
        print_fail("No signup key available (rotate-signup-key test must pass first)")
        return False
    
    url = f"{API_BASE}/auth/public-structure"
    params = {"school_key": student_signup_key}
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        if "grades" not in data or "sections" not in data:
            print_fail("Response missing 'grades' or 'sections'", json.dumps(data, indent=2))
            return False
        
        grades = data["grades"]
        sections = data["sections"]
        
        print_info(f"Grades count: {len(grades)}")
        print_info(f"Sections count: {len(sections)}")
        
        if len(grades) > 0:
            test_grade_id = grades[0]["id"]
            print_info(f"Using grade_id: {test_grade_id}")
        
        if len(sections) > 0:
            test_section_id = sections[0]["id"]
            print_info(f"Using section_id: {test_section_id}")
        
        print_pass("Valid school key returns grades and sections")
        return True
        
    except Exception as e:
        print_fail(f"Exception during valid key test: {str(e)}")
        return False


# ============================================================================
# TEST 3: STUDENT SIGNUP (pending flow)
# ============================================================================

def test_student_signup_valid():
    """Test POST /api/auth/signup/student with valid data"""
    global pending_student_user_id, pending_student_email, pending_student_password
    
    print_test("3.1 - POST /api/auth/signup/student with valid data")
    
    if not student_signup_key or not test_grade_id or not test_section_id:
        print_fail("Missing prerequisites (signup key, grade_id, section_id)")
        return False
    
    # Generate unique email
    timestamp = int(time.time())
    pending_student_email = f"student.pending.{timestamp}@test.com"
    pending_student_password = "password123"
    
    url = f"{API_BASE}/auth/signup/student"
    payload = {
        "school_key": student_signup_key,
        "full_name": f"طالب اختبار {timestamp}",
        "email": pending_student_email,
        "password": pending_student_password,
        "grade_id": test_grade_id,
        "section_id": test_section_id,
        "gender": "male",
        "guardian_name": "ولي الأمر",
        "guardian_phone": "0790000000"
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        if not data.get("ok"):
            print_fail("Response 'ok' field is not true", json.dumps(data, indent=2))
            return False
        
        if data.get("status") != "pending_approval":
            print_fail(f"Expected status 'pending_approval', got {data.get('status')}")
            return False
        
        # CRITICAL: Must NOT return access_token or Set-Cookie
        if "access_token" in data:
            print_fail("CRITICAL: Pending signup should NOT return access_token")
            return False
        
        if "access_token" in resp.cookies or "refresh_token" in resp.cookies:
            print_fail("CRITICAL: Pending signup should NOT set auth cookies")
            return False
        
        print_info(f"Pending student email: {pending_student_email}")
        print_pass("Student signup created with status=pending_approval, no auth tokens")
        return True
        
    except Exception as e:
        print_fail(f"Exception during student signup test: {str(e)}")
        return False


def test_login_pending_student():
    """Test login attempt with pending student credentials"""
    print_test("3.2 - POST /api/auth/login with pending student (should fail)")
    
    if not pending_student_email or not pending_student_password:
        print_fail("No pending student credentials available")
        return False
    
    url = f"{API_BASE}/auth/login"
    payload = {
        "email": pending_student_email,
        "password": pending_student_password,
        "remember": False
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 403:
            print_fail(f"Expected 403, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        detail = data.get("detail", "")
        
        # Check for Arabic pending message
        if "بانتظار" not in detail and "موافقة" not in detail:
            print_fail(f"Expected Arabic pending message, got: {detail}")
            return False
        
        print_pass(f"Pending student login blocked with 403: {detail}")
        return True
        
    except Exception as e:
        print_fail(f"Exception during pending login test: {str(e)}")
        return False


def test_student_signup_invalid_key():
    """Test POST /api/auth/signup/student with invalid key"""
    print_test("3.3 - POST /api/auth/signup/student with INVALID key")
    
    if not test_grade_id or not test_section_id:
        print_fail("Missing grade_id or section_id")
        return False
    
    timestamp = int(time.time())
    url = f"{API_BASE}/auth/signup/student"
    payload = {
        "school_key": "INVALID-KEY-9999",
        "full_name": f"طالب اختبار {timestamp}",
        "email": f"invalid.key.{timestamp}@test.com",
        "password": "password123",
        "grade_id": test_grade_id,
        "section_id": test_section_id
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 400:
            print_fail(f"Expected 400, got {resp.status_code}", resp.text)
            return False
        
        print_pass("Invalid school key rejected with 400")
        return True
        
    except Exception as e:
        print_fail(f"Exception during invalid key signup test: {str(e)}")
        return False


def test_student_signup_missing_fields():
    """Test POST /api/auth/signup/student missing grade_id/section_id"""
    print_test("3.4 - POST /api/auth/signup/student missing grade_id")
    
    if not student_signup_key:
        print_fail("No signup key available")
        return False
    
    timestamp = int(time.time())
    url = f"{API_BASE}/auth/signup/student"
    payload = {
        "school_key": student_signup_key,
        "full_name": f"طالب اختبار {timestamp}",
        "email": f"missing.fields.{timestamp}@test.com",
        "password": "password123",
        # Missing grade_id and section_id
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 400:
            print_fail(f"Expected 400, got {resp.status_code}", resp.text)
            return False
        
        print_pass("Missing grade_id/section_id rejected with 400")
        return True
        
    except Exception as e:
        print_fail(f"Exception during missing fields test: {str(e)}")
        return False


# ============================================================================
# TEST 4: APPROVAL FLOW
# ============================================================================

def test_get_pending_signups():
    """Test GET /api/signups/pending as admin"""
    global pending_student_user_id
    
    print_test("4.1 - GET /api/signups/pending (as admin)")
    
    if not admin_token:
        print_fail("No admin token available")
        return False
    
    url = f"{API_BASE}/signups/pending"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    
    try:
        resp = requests.get(url, headers=headers, cookies=admin_cookies, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        if "items" not in data:
            print_fail("Response missing 'items' field", json.dumps(data, indent=2))
            return False
        
        items = data["items"]
        print_info(f"Pending signups count: {len(items)}")
        
        # Find our pending student
        found = False
        for item in items:
            if item.get("email") == pending_student_email:
                found = True
                pending_student_user_id = item.get("user_id")
                
                # Check enriched data
                if "signup_data" not in item:
                    print_fail("Item missing 'signup_data'")
                    return False
                
                signup_data = item["signup_data"]
                if "grade_id" not in signup_data or "section_id" not in signup_data:
                    print_fail("signup_data missing grade_id or section_id")
                    return False
                
                # Check enriched names
                if not item.get("grade_name") or not item.get("section_name"):
                    print_fail("Item missing enriched grade_name or section_name")
                    return False
                
                print_info(f"Found pending student: {item.get('full_name')}")
                print_info(f"  user_id: {pending_student_user_id}")
                print_info(f"  grade_name: {item.get('grade_name')}")
                print_info(f"  section_name: {item.get('section_name')}")
                break
        
        if not found:
            print_fail(f"Pending student {pending_student_email} not found in list")
            return False
        
        print_pass("GET /api/signups/pending returns pending user with enriched data")
        return True
        
    except Exception as e:
        print_fail(f"Exception during get pending signups test: {str(e)}")
        return False


def test_approve_signup():
    """Test POST /api/signups/{user_id}/approve"""
    global approved_student_user_id
    
    print_test("4.2 - POST /api/signups/{user_id}/approve")
    
    if not admin_token or not pending_student_user_id:
        print_fail("Missing admin token or pending_student_user_id")
        return False
    
    timestamp = int(time.time())
    url = f"{API_BASE}/signups/{pending_student_user_id}/approve"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    payload = {
        "grade_id": test_grade_id,
        "section_id": test_section_id,
        "full_name": f"طالب معتمد {timestamp}",
        "student_number": f"TEST-{timestamp}",
        "gender": "male",
        "guardian_name": "ولي الأمر",
        "guardian_phone": "0790000000"
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, cookies=admin_cookies, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        if not data.get("ok"):
            print_fail("Response 'ok' field is not true", json.dumps(data, indent=2))
            return False
        
        if "student_id" not in data:
            print_fail("Response missing 'student_id'", json.dumps(data, indent=2))
            return False
        
        student_id = data["student_id"]
        print_info(f"Created student_id: {student_id}")
        
        approved_student_user_id = pending_student_user_id
        
        print_pass("Signup approved successfully with student_id returned")
        return True
        
    except Exception as e:
        print_fail(f"Exception during approve signup test: {str(e)}")
        return False


def test_approved_student_login():
    """Test login with approved student credentials"""
    print_test("4.3 - POST /api/auth/login with approved student (should succeed)")
    
    if not pending_student_email or not pending_student_password:
        print_fail("No approved student credentials available")
        return False
    
    url = f"{API_BASE}/auth/login"
    payload = {
        "email": pending_student_email,
        "password": pending_student_password,
        "remember": False
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        if "access_token" not in data:
            print_fail("Response missing 'access_token'", json.dumps(data, indent=2))
            return False
        
        if "access_token" not in resp.cookies or "refresh_token" not in resp.cookies:
            print_fail("Missing auth cookies")
            return False
        
        user = data.get("user", {})
        if user.get("role") != "STUDENT":
            print_fail(f"Expected role STUDENT, got {user.get('role')}")
            return False
        
        print_pass("Approved student can login successfully with access_token and cookies")
        return True
        
    except Exception as e:
        print_fail(f"Exception during approved student login test: {str(e)}")
        return False


def test_verify_student_record():
    """Test that Student record was created via GET /api/students"""
    print_test("4.4 - Verify Student record created (GET /api/students)")
    
    if not admin_token:
        print_fail("No admin token available")
        return False
    
    url = f"{API_BASE}/students"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    # Note: /api/students search only supports full_name and student_number, not email
    # So we get all students and filter manually
    
    try:
        resp = requests.get(url, headers=headers, cookies=admin_cookies, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        items = data.get("items", [])
        
        found = False
        for item in items:
            if item.get("email") == pending_student_email:
                found = True
                print_info(f"Found student record: {item.get('full_name')}")
                print_info(f"  student_number: {item.get('student_number')}")
                print_info(f"  grade_id: {item.get('grade_id')}")
                print_info(f"  section_id: {item.get('section_id')}")
                
                if item.get("grade_id") != test_grade_id:
                    print_fail(f"grade_id mismatch: expected {test_grade_id}, got {item.get('grade_id')}")
                    return False
                
                if item.get("section_id") != test_section_id:
                    print_fail(f"section_id mismatch: expected {test_section_id}, got {item.get('section_id')}")
                    return False
                
                break
        
        if not found:
            print_fail(f"Student record not found for {pending_student_email}")
            return False
        
        print_pass("Student record created with correct grade_id and section_id")
        return True
        
    except Exception as e:
        print_fail(f"Exception during verify student record test: {str(e)}")
        return False


def test_approve_non_pending_user():
    """Test approving a user whose status is not pending"""
    print_test("4.5 - POST /api/signups/{user_id}/approve on non-pending user (should fail)")
    
    if not admin_token or not approved_student_user_id:
        print_fail("Missing admin token or approved_student_user_id")
        return False
    
    timestamp = int(time.time())
    url = f"{API_BASE}/signups/{approved_student_user_id}/approve"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    payload = {
        "grade_id": test_grade_id,
        "section_id": test_section_id,
        "full_name": "Test",
        "student_number": f"TEST-{timestamp}",
        "gender": "male",
        "guardian_name": "Guardian",
        "guardian_phone": "0790000000"
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, cookies=admin_cookies, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 400:
            print_fail(f"Expected 400, got {resp.status_code}", resp.text)
            return False
        
        print_pass("Approving non-pending user rejected with 400")
        return True
        
    except Exception as e:
        print_fail(f"Exception during approve non-pending test: {str(e)}")
        return False


# ============================================================================
# TEST 5: REJECTION FLOW
# ============================================================================

def test_create_another_pending_signup():
    """Create another pending signup for rejection test"""
    global rejected_student_user_id
    
    print_test("5.1 - Create another pending signup for rejection")
    
    if not student_signup_key or not test_grade_id or not test_section_id:
        print_fail("Missing prerequisites")
        return False
    
    timestamp = int(time.time())
    email = f"student.reject.{timestamp}@test.com"
    password = "password123"
    
    url = f"{API_BASE}/auth/signup/student"
    payload = {
        "school_key": student_signup_key,
        "full_name": f"طالب للرفض {timestamp}",
        "email": email,
        "password": password,
        "grade_id": test_grade_id,
        "section_id": test_section_id
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        # Get the user_id from pending list
        time.sleep(1)  # Brief delay
        
        url2 = f"{API_BASE}/signups/pending"
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp2 = requests.get(url2, headers=headers, cookies=admin_cookies, timeout=10)
        
        if resp2.status_code == 200:
            items = resp2.json().get("items", [])
            for item in items:
                if item.get("email") == email:
                    rejected_student_user_id = item.get("user_id")
                    print_info(f"Created pending user for rejection: {rejected_student_user_id}")
                    break
        
        if not rejected_student_user_id:
            print_fail("Could not find newly created pending user")
            return False
        
        print_pass("Created another pending signup for rejection test")
        return True
        
    except Exception as e:
        print_fail(f"Exception during create pending for rejection: {str(e)}")
        return False


def test_reject_signup():
    """Test POST /api/signups/{user_id}/reject"""
    print_test("5.2 - POST /api/signups/{user_id}/reject")
    
    if not admin_token or not rejected_student_user_id:
        print_fail("Missing admin token or rejected_student_user_id")
        return False
    
    url = f"{API_BASE}/signups/{rejected_student_user_id}/reject"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    payload = {
        "reason": "invalid data"
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, cookies=admin_cookies, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        if not data.get("ok"):
            print_fail("Response 'ok' field is not true", json.dumps(data, indent=2))
            return False
        
        print_pass("Signup rejected successfully")
        return True
        
    except Exception as e:
        print_fail(f"Exception during reject signup test: {str(e)}")
        return False


def test_login_rejected_student():
    """Test login attempt with rejected student"""
    print_test("5.3 - Login with rejected student (should fail)")
    
    # We need to get the email from the rejected user
    if not admin_token or not rejected_student_user_id:
        print_fail("Missing prerequisites")
        return False
    
    # Get user details
    url = f"{API_BASE}/signups/history?status=rejected"
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        resp = requests.get(url, headers=headers, cookies=admin_cookies, timeout=10)
        
        if resp.status_code != 200:
            print_fail(f"Could not fetch rejected users: {resp.status_code}")
            return False
        
        items = resp.json().get("items", [])
        rejected_email = None
        
        for item in items:
            if item.get("user_id") == rejected_student_user_id:
                rejected_email = item.get("email")
                break
        
        if not rejected_email:
            print_fail("Could not find rejected user email")
            return False
        
        # Try to login
        url2 = f"{API_BASE}/auth/login"
        payload = {
            "email": rejected_email,
            "password": "password123",
            "remember": False
        }
        
        resp2 = requests.post(url2, json=payload, timeout=10)
        print_info(f"Status: {resp2.status_code}")
        
        if resp2.status_code != 403:
            print_fail(f"Expected 403, got {resp2.status_code}", resp2.text)
            return False
        
        data = resp2.json()
        detail = data.get("detail", "")
        
        # Check for Arabic rejection message
        if "رفض" not in detail:
            print_fail(f"Expected Arabic rejection message with 'رفض', got: {detail}")
            return False
        
        print_pass(f"Rejected student login blocked with 403: {detail}")
        return True
        
    except Exception as e:
        print_fail(f"Exception during rejected login test: {str(e)}")
        return False


def test_delete_rejected_signup():
    """Test DELETE /api/signups/{user_id}"""
    print_test("5.4 - DELETE /api/signups/{user_id} on rejected user")
    
    if not admin_token or not rejected_student_user_id:
        print_fail("Missing admin token or rejected_student_user_id")
        return False
    
    url = f"{API_BASE}/signups/{rejected_student_user_id}"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    
    try:
        resp = requests.delete(url, headers=headers, cookies=admin_cookies, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        if not data.get("ok"):
            print_fail("Response 'ok' field is not true", json.dumps(data, indent=2))
            return False
        
        print_pass("Rejected signup deleted successfully")
        return True
        
    except Exception as e:
        print_fail(f"Exception during delete signup test: {str(e)}")
        return False


# ============================================================================
# TEST 6: RBAC ENFORCEMENT
# ============================================================================

def test_pending_without_token():
    """Test GET /api/signups/pending without token"""
    print_test("6.1 - GET /api/signups/pending without token (should fail)")
    
    url = f"{API_BASE}/signups/pending"
    
    try:
        resp = requests.get(url, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 401:
            print_fail(f"Expected 401, got {resp.status_code}", resp.text)
            return False
        
        print_pass("Unauthorized access rejected with 401")
        return True
        
    except Exception as e:
        print_fail(f"Exception during no token test: {str(e)}")
        return False


def test_pending_as_student():
    """Test GET /api/signups/pending as STUDENT user"""
    print_test("6.2 - GET /api/signups/pending as STUDENT (should fail)")
    
    if not pending_student_email or not pending_student_password:
        print_fail("No approved student credentials available")
        return False
    
    # Login as student
    url = f"{API_BASE}/auth/login"
    payload = {
        "email": pending_student_email,
        "password": pending_student_password,
        "remember": False
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        
        if resp.status_code != 200:
            print_fail(f"Student login failed: {resp.status_code}")
            return False
        
        student_token = resp.json().get("access_token")
        student_cookies = resp.cookies
        
        # Try to access pending signups
        url2 = f"{API_BASE}/signups/pending"
        headers = {"Authorization": f"Bearer {student_token}"}
        
        resp2 = requests.get(url2, headers=headers, cookies=student_cookies, timeout=10)
        print_info(f"Status: {resp2.status_code}")
        
        if resp2.status_code != 403:
            print_fail(f"Expected 403, got {resp2.status_code}", resp2.text)
            return False
        
        print_pass("Student access to signups.view rejected with 403")
        return True
        
    except Exception as e:
        print_fail(f"Exception during student RBAC test: {str(e)}")
        return False


def test_rotate_key_as_admin():
    """Test POST /api/settings/rotate-signup-key as admin (should succeed)"""
    print_test("6.3 - POST /api/settings/rotate-signup-key as admin (should succeed)")
    
    if not admin_token:
        print_fail("No admin token available")
        return False
    
    url = f"{API_BASE}/settings/rotate-signup-key"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    
    try:
        resp = requests.post(url, headers=headers, cookies=admin_cookies, timeout=10)
        print_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}", resp.text)
            return False
        
        data = resp.json()
        
        if "student_signup_key" not in data:
            print_fail("Response missing 'student_signup_key'")
            return False
        
        print_pass("Admin (DIRECTOR) can rotate signup key (has settings.manage)")
        return True
        
    except Exception as e:
        print_fail(f"Exception during admin rotate key test: {str(e)}")
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests and generate summary"""
    print("\n" + "="*80)
    print("BACKEND REGRESSION TEST - AUTH BUG FIX (CORS + SIGNUP FLOW)")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin: {ADMIN_EMAIL}")
    print("="*80)
    
    results = []
    
    # Test 1: LOGIN
    results.append(("1.1 Login success", test_login_success()))
    results.append(("1.2 Login wrong password", test_login_wrong_password()))
    results.append(("1.3 CORS preflight", test_cors_preflight()))
    results.append(("1.4 GET /api/auth/me", test_auth_me()))
    
    # Test 2: SCHOOL KEY + SIGNUP GATE
    results.append(("2.1 GET school-info", test_school_info()))
    results.append(("2.2 Rotate signup key", test_rotate_signup_key()))
    results.append(("2.3 Public structure invalid key", test_public_structure_invalid_key()))
    results.append(("2.4 Public structure valid key", test_public_structure_valid_key()))
    
    # Test 3: STUDENT SIGNUP
    results.append(("3.1 Student signup valid", test_student_signup_valid()))
    results.append(("3.2 Login pending student", test_login_pending_student()))
    results.append(("3.3 Student signup invalid key", test_student_signup_invalid_key()))
    results.append(("3.4 Student signup missing fields", test_student_signup_missing_fields()))
    
    # Test 4: APPROVAL FLOW
    results.append(("4.1 GET pending signups", test_get_pending_signups()))
    results.append(("4.2 Approve signup", test_approve_signup()))
    results.append(("4.3 Approved student login", test_approved_student_login()))
    results.append(("4.4 Verify student record", test_verify_student_record()))
    results.append(("4.5 Approve non-pending user", test_approve_non_pending_user()))
    
    # Test 5: REJECTION FLOW
    results.append(("5.1 Create pending for rejection", test_create_another_pending_signup()))
    results.append(("5.2 Reject signup", test_reject_signup()))
    results.append(("5.3 Login rejected student", test_login_rejected_student()))
    results.append(("5.4 Delete rejected signup", test_delete_rejected_signup()))
    
    # Test 6: RBAC ENFORCEMENT
    results.append(("6.1 Pending without token", test_pending_without_token()))
    results.append(("6.2 Pending as student", test_pending_as_student()))
    results.append(("6.3 Rotate key as admin", test_rotate_key_as_admin()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        if result:
            print(f"✅ PASS: {name}")
            passed += 1
        else:
            print(f"❌ FAIL: {name}")
            failed += 1
    
    print("="*80)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("="*80)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
