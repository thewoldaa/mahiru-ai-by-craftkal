from app import User


def test_user_model(client):
    user = User(username='u1', email='u1@mail.com', password_hash='x')
    assert user.username == 'u1'
