from app.models import User, db, Category, Subscription
import sqlalchemy as sa


def test_create_user(app):
    """Felhasználó feltöltése adatbázisba"""
    with app.app_context():
        user = User(email='tesztuser@teszt.hu')
        user.set_password('jojelszo')
        db.session.add(user)
        db.session.commit()

        user_db = db.session.scalar(sa.select(User).where(User.email == user.email))
        
        assert user_db.id is not None
        assert user_db.email == 'tesztuser@teszt.hu'
        assert user_db.check_password('jojelszo')
        assert not user.check_password('rosszjelszo')

def test_create_category(app):
    """Kategória feltöltése adatbázisba"""
    with app.app_context():
        user = User(email='tesztuser@teszt.hu')
        user.set_password('jojelszo')
        db.session.add(user)
        db.session.commit()

        category = Category(user_id=user.id, name='Teszt Kategória')
        db.session.add(category)
        db.session.commit()

        category_db = db.session.scalar(sa.select(Category).where(Category.name == category.name))
        assert category_db.id is not None
        assert category_db.name == 'Teszt Kategória'
        assert category_db.user_id is not None
        assert category_db.user_id == user.id

def test_create_subscription(app):
    """Előfizetés feltöltése adatbázisba"""
    with app.app_context():
        user = User(email='tesztuser@teszt.hu')
        user.set_password('jojelszo')
        db.session.add(user)
        db.session.commit()

        category = Category(user_id=user.id, name='Teszt Kategória')
        db.session.add(category)
        db.session.commit()

        subscription = Subscription(user_id=user.id, category_id=category.id, name='Teszt Előfizetés', price=1000)
        db.session.add(subscription)
        db.session.commit()
        subscription_db = db.session.scalar(sa.select(Subscription).where(Subscription.name == subscription.name))

        assert subscription_db.id is not None
        assert subscription_db.name == 'Teszt Előfizetés'
        assert subscription_db.price == 1000
        assert subscription_db.user_id is not None
        assert subscription_db.user_id == user.id