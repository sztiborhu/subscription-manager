from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required

import sqlalchemy as sa
from app import db
from app.forms import LoginForm, RegistrationForm, AddCategoryForm, EditCategoryForm, AddSubscriptionForm, \
    EditSubscriptionForm

from app.models import User, Category, Subscription

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def main_page():
    if not current_user.is_authenticated:
        return render_template('index.html', title="Főoldal")

    subscriptions = db.session.scalars(sa.select(Subscription).where(Subscription.user_id == current_user.id)).all()
    categories = db.session.scalars(sa.select(Category).where(Category.user_id == current_user.id)).all()

    total_subscriptions = len(subscriptions)
    total_cost = sum(sub.price for sub in subscriptions)
    avg_price = round(total_cost / total_subscriptions, 2) if total_subscriptions else 0
    num_categories = len(categories)

    most_expensive = max(subscriptions, key=lambda s: s.price, default=None)
    least_expensive = min(subscriptions, key=lambda s: s.price, default=None)

    category_spending = {}
    category_names = {cat.id: cat.name for cat in categories}
    for sub in subscriptions:
        cat_name = category_names.get(sub.category_id, 'Nincs kategória')
        category_spending[cat_name] = category_spending.get(cat_name, 0) + sub.price

    subs_per_category = {}
    for sub in subscriptions:
        cat_name = category_names.get(sub.category_id, 'Nincs kategória')
        subs_per_category[cat_name] = subs_per_category.get(cat_name, 0) + 1

    percent_per_category = {k: round(v/total_subscriptions*100, 1) for k, v in subs_per_category.items()} if total_subscriptions else {}

    most_popular_category = max(category_spending, key=category_spending.get) if category_spending else 'Nincs'

    return render_template(
        'index.html',
        title="Főoldal",
        total_subscriptions=total_subscriptions,
        total_cost=total_cost,
        avg_price=avg_price,
        num_categories=num_categories,
        most_expensive=most_expensive,
        least_expensive=least_expensive,
        category_spending=category_spending,
        most_popular_category=most_popular_category,
        subs_per_category=subs_per_category,
        percent_per_category=percent_per_category
    )

@bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.main_page'))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))

        if user is None or not user.check_password(form.password.data):
            flash('Hibás e-mail cím vagy jelszó', 'error')
            return redirect(url_for('main.login_page'))

        login_user(user)

        return redirect(url_for('main.main_page'))

    return render_template('login.html', title="Bejelentkezés", form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.main_page'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Sikeres regisztráció! Most már bejelentkezhetsz.', 'success')
        return redirect(url_for('main.login_page'))

    return render_template('register.html', title="Regisztráció", form=form)

"""Kategóriák kezelése"""
@bp.route('/categories')
@login_required
def categories_page():
    form = AddCategoryForm()
    categories = db.session.scalars(sa.select(Category).where(current_user.id == Category.user_id)).all()

    category_prices = {}
    category_quantity = {}

    for category in categories:
        subscriptions = db.session.scalars(sa.select(Subscription).where(
            Subscription.category_id == category.id,
            Subscription.user_id == current_user.id
        )).all()

        total_price = sum(sub.price for sub in subscriptions)
        category_prices[category.id] = total_price
        category_quantity[category.id] = len(subscriptions)


    return render_template('categories/categories.html', title="Kategóriák", categories=categories, category_prices=category_prices, category_quantity=category_quantity, form=form)

@bp.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    form = AddCategoryForm()

    if form.validate_on_submit():
        category = Category(user_id=current_user.id, name=form.name.data.strip())
        categories_name = db.session.scalars(sa.select(Category.name).where(current_user.id == Category.user_id)).all()

        if category.name not in categories_name:
            db.session.add(category)
            db.session.commit()

            flash('Kategória hozzáadva!', 'success')
            return redirect(url_for('main.categories_page'))
        else:
            flash('Már van ilyen nevű kategóriád!', 'error')

    return redirect(url_for('main.categories_page'))

@bp.route('/categories/delete/<int:category_id>', methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
    category = db.session.get(Category, category_id)

    if category is None or category.user_id != current_user.id:
        flash('Kategória nem található vagy nem jogosult a törlésére!', 'error')
        return redirect(url_for('main.categories_page'))

    # Update all subscriptions that reference this category
    subscriptions = db.session.scalars(sa.select(Subscription).where(
        Subscription.category_id == category_id,
        Subscription.user_id == current_user.id
    )).all()
    
    for subscription in subscriptions:
        subscription.category_id = None
    
    db.session.delete(category)
    db.session.commit()

    flash('Kategória törölve!', 'success')
    return redirect(url_for('main.categories_page'))

@bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = db.session.get(Category, category_id)

    if category is None or category.user_id != current_user.id:
        flash('Kategória nem található vagy nem jogosult a szerkesztésére!', 'error')
        return redirect(url_for('main.categories_page'))

    form = EditCategoryForm(obj=category)

    if form.validate_on_submit():
        form.populate_obj(category)
        categories_name = db.session.scalars(sa.select(Category.name).where(
            current_user.id == Category.user_id,
            Category.id != category_id
        )).all()

        if category.name not in categories_name:
            db.session.commit()

            flash('Kategória frissítve!', 'success')
            return redirect(url_for('main.categories_page'))
        else:
            flash('Már létezik ilyen nevű kategóriád!', 'error')

            return redirect(url_for('main.edit_category', category_id=category.id))

    return render_template('categories/edit_category.html', title="Kategória szerkesztése", form=form, category=category)

"""Előfizetések kezelése"""
@bp.route('/subscriptions')
@login_required
def subscriptions_page():
    subscriptions = db.session.scalars(sa.select(Subscription).where(current_user.id == Subscription.user_id)).all()
    categories = db.session.scalars(sa.select(Category).where(current_user.id == Category.user_id)).all()

    form = AddSubscriptionForm()

    category_names = {}
    for subscription in subscriptions:
        if subscription.category_id is None:
            category_names[subscription.id] = "Nincs kategória"
            break

        for category in categories:
            if subscription.category_id == category.id:
                category_names[subscription.id] = category.name
                break


    return render_template('subscriptions/subscriptions.html', title="Előfizetések", subscriptions=subscriptions, category_names=category_names, form=form)

@bp.route('/subscriptions/add', methods=['POST'])
@login_required
def add_subscription():
    form = AddSubscriptionForm()

    if form.validate_on_submit():
        subscription = Subscription(user_id=current_user.id, category_id=form.category.data, name=form.name.data, price=form.price.data)

        subscriptions_name = db.session.scalars(sa.select(Subscription.name).where(current_user.id == Subscription.user_id)).all()

        if subscription.name not in subscriptions_name:
            db.session.add(subscription)
            db.session.commit()

            flash('Előfizetés hozzáadva!', 'success')
            return redirect(url_for('main.subscriptions_page'))
        else:
            flash('Már van ilyen nevű előfizetésed!', 'error')


    return redirect(url_for('main.subscriptions_page'))


@bp.route('/subscriptions/delete/<int:subscription_id>', methods=['GET', 'POST'])
@login_required
def delete_subscription(subscription_id):
    subscription = db.session.get(Subscription, subscription_id)

    if subscription is None or subscription.user_id != current_user.id:
        flash('Az előfizetés nem található vagy nem jogosult a törlésére!', 'error')
        return redirect(url_for('main.subscriptions_page'))

    db.session.delete(subscription)
    db.session.commit()

    flash('Az előfizetés törölve!', 'success')
    return redirect(url_for('main.subscriptions_page'))


@bp.route('/subscriptions/edit/<int:subscription_id>', methods=['GET', 'POST'])
@login_required
def edit_subscription(subscription_id):
    subscription = db.session.get(Subscription, subscription_id)

    if subscription is None or subscription.user_id != current_user.id:
        flash('Az előfizetés nem található vagy nem jogosult a törlésére!', 'error')
        return redirect(url_for('main.subscriptions_page'))

    form = EditSubscriptionForm(obj=subscription)

    if form.validate_on_submit():
        form.populate_obj(subscription)
        subscription.category_id = form.category.data

        subscriptions_name = db.session.scalars(sa.select(Subscription.name).where(
            current_user.id == Subscription.user_id,
            Subscription.id != subscription_id
        )).all()

        if subscription.name not in subscriptions_name:
            db.session.commit()

            flash('Előfizetés frissítve!', 'success')
            return redirect(url_for('main.subscriptions_page'))
        else:
            flash('Már létezik ilyen nevű előfizetésed!', 'error')

            return redirect(url_for('main.edit_subscription', subscription_id=subscription.id))

    return render_template('subscriptions/edit_subscription.html', title="Előfizetés szerkesztése", form=form, subscription=subscription)


@bp.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html', title="Profil", user=current_user)

@bp.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for('main.main_page'))

@bp.errorhandler(404)
def page_not_found(e):
    return render_template('errors/error.html',
                           title="404 - Nem található",
                           code="404",
                           heading="Az oldal nem található",
                           description="Sajnáljuk, a keresett oldal nem létezik vagy már eltávolították."  ), 404

@bp.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/error.html',
                           title="500 - Belső szerverhiba",
                           code="500",
                           heading="Belső szerverhiba",
                           description="Sajnáljuk, de valami hiba történt a kiszolgálón."), 500

@bp.errorhandler(403)
def forbidden(e):
    return render_template('errors/error.html',
                           title="403 - Tiltott",
                           code="403",
                           heading="Tiltott hozzáférés",
                           description="Sajnáljuk, de nincs jogosultságod ehhez az oldalhoz."), 403

@bp.errorhandler(400)
def bad_request(e):
    return render_template('errors/error.html',
                           title="400 - Hibás kérés",
                           code="400",
                           heading="Hibás kérés",
                           description="Sajnáljuk, de a kérésed hibás volt."), 400

@bp.errorhandler(405)
def method_not_allowed(e):
    return render_template('errors/error.html',
                           title="405 - Nem engedélyezett",
                           code="405",
                           heading="Nem engedélyezett módszer",
                           description="Sajnáljuk, de a kért módszer nem engedélyezett."), 405

@bp.route('/help')
def help_page():
    return render_template('help.html') 

