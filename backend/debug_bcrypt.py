import sys
import os

# Add the current directory to sys.path to ensure we can import app modules if needed
# But for this test we'll try to replicate the logic in security.py directly
sys.path.append(os.getcwd())

import bcrypt
from passlib.context import CryptContext

# Apply the monkeypatch
if not hasattr(bcrypt, "__about__"):
    try:
        bcrypt.__about__ = type("about", (object,), {"__version__": bcrypt.__version__})
        print(f"Applied monkeypatch. bcrypt version: {bcrypt.__version__}")
    except AttributeError:
        print("Failed to apply monkeypatch or version not found")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=False)

def test_hash(password: str):
    print(f"Testing password length: {len(password)}")
    try:
        # Replicating the logic from security.py
        password_bytes = password.encode('utf-8')[:72]
        print(f"Truncated bytes length: {len(password_bytes)}")
        decoded_password = password_bytes.decode('utf-8', errors='ignore')
        print(f"Decoded string length: {len(decoded_password)}")
        
        hashed = pwd_context.hash(decoded_password)
        print("Hash successful")
        return hashed
    except Exception as e:
        print(f"Hash failed: {e}")
        import traceback
        traceback.print_exc()

# Test cases
print("--- Test 1: Short password ---")
test_hash("password123")

print("\n--- Test 2: Long password (100 chars) ---")
test_hash("a" * 100)

print("\n--- Test 3: Korean password (long) ---")
test_hash("안녕하세요" * 20) # 3 bytes * 5 chars * 20 = 300 bytes
