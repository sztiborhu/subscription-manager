from app import create_app, db
from app.models import User, Category, Subscription

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        pass