from app import User, db
from werkzeug.security import generate_password_hash


def login(client):
    user = User(username='tester', email='t@example.com', password_hash=generate_password_hash('123456'))
    db.session.add(user)
    db.session.commit()
    return client.post('/login', data={'username': 'tester', 'password': '123456'}, follow_redirects=True)


def test_scene_requires_auth(client):
    rv = client.get('/api/scene/ch1_scene_1')
    assert rv.status_code in (302, 401)


def test_scene_after_login(client):
    login(client)
    rv = client.get('/api/scene/ch1_scene_1')
    assert rv.status_code == 200
