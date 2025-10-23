import sys
from app import app


def run_test():
    client = app.test_client()
    r = client.get('/')
    print('GET / status:', r.status_code)
    if r.status_code != 200:
        print('ERROR: unexpected status code')
        return 1
    txt = r.get_data(as_text=True)
    # check for title or heading
    if 'Biblioteca - Login' in txt or '<title>Login - Biblioteca' in txt or 'Biblioteca - Login/Registro' in txt:
        print('PAGE OK: contains login content')
        return 0
    else:
        print('ERROR: page content did not contain expected login text')
        return 1


if __name__ == '__main__':
    sys.exit(run_test())

