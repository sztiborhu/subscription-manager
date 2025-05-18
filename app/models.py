from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

from app import login

@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.email)

class Category(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), nullable=False)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), index=True, nullable=False)

    def __repr__(self):
        return '<Category {}>'.format(self.name)

class Subscription(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), nullable=False)
    category_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey(Category.id), nullable=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), index=True, nullable=False)
    price: so.Mapped[int] = so.mapped_column(nullable=False)

    def __repr__(self):
        return '<Subscription {}>'.format(self.name)

