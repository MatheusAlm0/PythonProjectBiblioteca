import sys
import json
import uuid

from app import app


def run_tests():
    client = app.test_client()
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "pass1234"

    # Register
    r = client.post('/auth/register', json={'username': username, 'password': password})
    print('register status:', r.status_code, r.get_json())
    if r.status_code not in (200, 201):
        print('Register failed')
        return 1

    # Duplicate register
    r2 = client.post('/auth/register', json={'username': username, 'password': password})
    print('duplicate register status:', r2.status_code, r2.get_json())
    if r2.status_code == 201:
        print('Duplicate register unexpectedly succeeded')
        return 1

    # Wrong password login
    r3 = client.post('/auth/login', json={'username': username, 'password': 'wrong'})
    print('wrong login status:', r3.status_code, r3.get_json())
    if r3.status_code == 200:
        print('Login succeeded with wrong password')
        return 1

    # Correct login
    r4 = client.post('/auth/login', json={'username': username, 'password': password})
    print('login status:', r4.status_code, r4.get_json())
    if r4.status_code != 200:
        print('Login failed')
        return 1
    token = r4.get_json().get('token')
    if not token:
        print('No token returned')
        return 1

    # Access protected endpoint
    headers = {'Authorization': f'Bearer {token}'}
    r5 = client.get('/auth/me', headers=headers)
    print('me status:', r5.status_code, r5.get_json())
    if r5.status_code != 200:
        print('Protected endpoint failed')
        return 1
    if r5.get_json().get('username') != username:
        print('Returned username mismatch')
        return 1

    print('\nALL TESTS PASSED')
    return 0


if __name__ == '__main__':
    try:
        code = run_tests()
        sys.exit(code)
    except Exception as e:
        print('ERROR DURING TESTS:', e)
        raise

