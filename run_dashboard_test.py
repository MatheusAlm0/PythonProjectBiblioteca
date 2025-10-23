import sys
from app import app


def run_test():
    client = app.test_client()
    r = client.get('/dashboard')
    print('GET /dashboard status:', r.status_code)
    if r.status_code != 200:
        print('ERROR: unexpected status code')
        return 1
    txt = r.get_data(as_text=True)
    if 'Dashboard' in txt and '<title>Dashboard - Biblioteca' in txt:
        print('DASHBOARD PAGE OK')
        return 0
    else:
        print('ERROR: dashboard content missing expected text')
        return 1


if __name__ == '__main__':
    sys.exit(run_test())

