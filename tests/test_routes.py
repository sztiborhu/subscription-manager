


def test_main_page(client):
    """Bejelentkezés nélkül a főoldalra visz"""
    response = client.get('/')
    assert response.status_code == 302

def test_login_page(client):
    """Megjelenik a bejelentkezési oldal"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Bejelentkez' in response.data

def test_login_system(client):
    """Felhasználó regisztrálása és bejelentkezése"""

    # Regisztráció
    register_response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'testpass',
        'password_again': 'testpass'
    }, follow_redirects=True)

    assert register_response.status_code == 200
    assert b'Bejelentkez' in register_response.data

    # Bejelentkezés
    login_response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpass'
    }, follow_redirects=True)
    assert login_response.status_code == 200

    # Sikeresen átvitte a főoldalra
    assert b'Statisztik' in login_response.data

def test_post_category(client):
    # Regisztráció
    register_response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'testpass',
        'password_again': 'testpass'
    }, follow_redirects=True)

    # Bejelentkezés
    login_response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpass'
    }, follow_redirects=True)


    # Kategória hozzáadása
    category_response = client.post('/categories/add', data={
        'name': 'cxctesztkategoriacxc'
    }, follow_redirects=True)

    assert category_response.status_code == 200
    assert b'ria hozz' in category_response.data # Kategória hozzáadva
    assert b'cxctesztkategoriacxc' in category_response.data

def test_post_subscription(client):
    # Regisztráció
    register_response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'testpass',
        'password_again': 'testpass'
    }, follow_redirects=True)

    # Bejelentkezés
    login_response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpass'
    }, follow_redirects=True)


    # Kategória hozzáadása
    category_response = client.post('/categories/add', data={
        'name': 'cxctesztkategoriacxc'
    }, follow_redirects=True)

    # Előfizetés hozzáadása
    subscription_response = client.post('/subscriptions/add', data={
        'name': 'cxctesztelofizetes',
        'price': 1000,
        'category': 1
    }, follow_redirects=True)

    assert subscription_response.status_code == 200
    assert b'cxctesztelofizetes' in subscription_response.data
    assert b'cxctesztkategoriacxc' in subscription_response.data
    assert b'1000' in subscription_response.data
    assert b's hozz' in subscription_response.data # Előfizetés hozzáadva

def test_statistics_page(client):
    # Regisztráció
    register_response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'testpass',
        'password_again': 'testpass'
    }, follow_redirects=True)

    # Bejelentkezés
    login_response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpass'
    }, follow_redirects=True)


    # Kategória hozzáadása
    category_response = client.post('/categories/add', data={
        'name': 'cxctesztkategoriacxc'
    }, follow_redirects=True)

    category_response = client.post('/categories/add', data={
        'name': 'cxctesztkategoriacxc2'
    }, follow_redirects=True)

    # Előfizetés hozzáadása
    subscription_response = client.post('/subscriptions/add', data={
        'name': 'cxctesztelofizetes',
        'price': 1000,
        'category': 1
    }, follow_redirects=True)

    # Főoldalra navigálás
    statistics_response = client.get('/')

    assert statistics_response.status_code == 200
    assert b'Statisztik' in statistics_response.data
    assert b'cxctesztelofizetes' in statistics_response.data
    assert b'cxctesztkategoriacxc' in statistics_response.data
    assert b'ma:</strong> 1' in statistics_response.data
    assert b'ma:</strong> 2' in statistics_response.data

