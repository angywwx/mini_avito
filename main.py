import random

from flask import (Flask, jsonify, make_response, redirect, render_template,
                   request)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from sqlalchemy import or_

from data.forms import (CreateGoodForm, EditProfileForm, LoginForm,
                        MessageForm, RegisterForm)
from data.models import Category, Chats, Goods, Messages, User
from db import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    check = db_sess.query(Category).count()
    if check == 0:
        for i in [
            'Одежда',
            'Обувь',
            'Электроника',
            "Книги",
            "Для дома",
            "Спорт"
        ]:
            good = Category(category=i)
            db_sess.add(good)
            db_sess.commit()
    city = request.args.get('city', type=str)
    category = request.args.get('category', type=int)
    goods = db_sess.query(Goods).filter(
        Goods.is_active is True
    )
    if category:
        goods = goods.filter(Goods.category_id == category)
    if city:
        goods = goods.filter(Goods.city == city)
    goods = goods.order_by(Goods.created_at.desc()).all()
    categories = db_sess.query(Category).order_by(
        Category.category.asc()
    ).all()
    cities = db_sess.query(Goods.city).distinct().order_by(
        Goods.city.asc()
    ).all()
    sp = [city[0] for city in cities]
    return render_template(
        "index.html",
        title='Личный кабинет',
        goods=goods,
        cities=sp,
        categories=categories
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data
        ).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data
        ).first()
        if not user:
            new_user = User(
                name=form.name.data,
                surname=form.surname.data,
                city=form.city.data,
                email=form.email.data,
                phone=form.phone.data
            )
            new_user.set_password(form.password.data)
            db_sess.add(new_user)
            db_sess.commit()
            return redirect("/login")
        return render_template(
            'base_form.html',
            message="Пользователь с таким email уже существует",
            form=form,
            title='Регистрация'
        )
    return render_template('base_form.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile')
@login_required
def profile():
    db_sess = db_session.create_session()
    goods = db_sess.query(Goods).filter(Goods.user_id == current_user.id).all()
    return render_template("profile.html", title='Личный кабинет', goods=goods)


@app.route('/goods_create', methods=['GET', 'POST'])
@login_required
def create_good():
    form = CreateGoodForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    form.category_id.choices = [(i.id, i.category) for i in categories]
    if form.validate_on_submit():
        filename = None
        print(form.image_fn.data)
        if form.image_fn.data:
            img = form.image_fn.data
            filename = (f'{form.title.data}_{form.price.data}_'
                        f'{current_user.id}_{random.randint(1, 1000)}.jpg')
            img.save(f"static/img/{filename}")

        good = Goods(
            title=form.title.data,
            description=form.description.data,
            image_fn=filename,
            price=form.price.data,
            category_id=form.category_id.data,
            user_id=current_user.id,
            city=current_user.city
        )
        db_sess.add(good)
        db_sess.commit()
        return redirect("/profile")

    return render_template(
        "base_form.html",
        title='Создать объявление',
        form=form
    )


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    db_sess = db_session.create_session()
    edit_user = db_sess.query(User).filter(
        User.email == current_user.email
    ).first()
    if form.validate_on_submit():
        edit_user.name = form.name.data
        edit_user.surname = form.surname.data
        edit_user.city = form.city.data
        edit_user.address = form.address.data
        edit_user.email = form.email.data
        edit_user.phone = form.phone.data
        db_sess.commit()
        return redirect("/profile")
    else:
        form.name.data = edit_user.name
        form.surname.data = edit_user.surname
        form.city.data = edit_user.city
        form.address.data = edit_user.address
        form.email.data = edit_user.email
        form.phone.data = edit_user.phone
    return render_template(
        "base_form.html",
        title='Редактировать профиль',
        form=form
    )


@app.route('/goods_edit/<int:good_id>', methods=['GET', 'POST'])
@login_required
def edit_good(good_id):
    form = CreateGoodForm()
    db_sess = db_session.create_session()
    good = db_sess.query(Goods).filter(Goods.id == good_id).first()
    if not good or current_user.id != good.user_id:
        return redirect("/profile")
    categories = db_sess.query(Category).all()
    form.category_id.choices = [(i.id, i.category) for i in categories]
    if form.validate_on_submit():
        good.title = form.title.data
        good.description = form.description.data
        good.price = form.price.data
        good.category_id = form.category_id.data
        if form.image_fn.data:
            img = form.image_fn.data
            filename = (f'{form.title.data}_{form.price.data}_'
                        f'{current_user.id}_{random.randint(1, 1000)}.jpg')
            img.save(f"static/img/{filename}")
            good.image_fn = filename
        db_sess.commit()
        return redirect("/profile")
    else:
        form.title.data = good.title
        form.description.data = good.description
        form.price.data = good.price
        form.category_id.data = good.category_id
    return render_template(
        "base_form.html",
        title='Редактировать товар',
        form=form
    )


@app.route('/goods_disable/<int:good_id>', methods=['GET', 'POST'])
@login_required
def disable_good(good_id):
    db_sess = db_session.create_session()
    good = db_sess.query(Goods).filter(Goods.id == good_id).first()
    if not good or current_user.id != good.user_id:
        return redirect("/profile")
    good.is_active = not good.is_active
    db_sess.commit()
    return redirect("/profile")


@app.route('/goods/<int:good_id>')
def show_good(good_id):
    db_sess = db_session.create_session()
    good = db_sess.query(Goods).filter(
        Goods.id == good_id, Goods.is_active is True
    ).first()
    if not good:
        return redirect("/")
    return render_template(
        "goods_profile.html",
        title='Карточка товара',
        good=good
    )


@app.route('/goods/<int:good_id>/chat')
@login_required
def open_chat(good_id):
    db_sess = db_session.create_session()
    good = db_sess.query(Goods).filter(
        Goods.id == good_id, Goods.is_active is True
    ).first()
    if not good:
        return redirect("/")
    if good.user_id == current_user.id:
        return redirect(f"/goods/{good_id}")
    chat = db_sess.query(Chats).filter(
        Chats.good_id == good_id,
        Chats.buyer_id == current_user.id,
        Chats.seller_id == good.user_id
    ).first()
    if not chat:
        chat = Chats(
            seller_id=good.user_id,
            buyer_id=current_user.id,
            good_id=good_id
        )
        db_sess.add(chat)
        db_sess.commit()
    return redirect(f'/chat/{chat.id}')


@app.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def show_chat(chat_id):
    db_sess = db_session.create_session()
    form = MessageForm()
    chat = db_sess.query(Chats).filter(Chats.id == chat_id).first()
    if not chat or current_user.id not in [chat.buyer_id, chat.seller_id]:
        return redirect("/")
    if form.validate_on_submit():
        message = Messages(
            user_id=current_user.id,
            chat_id=chat.id,
            message=form.text.data
        )
        db_sess.add(message)
        db_sess.commit()
        return redirect(f'/chat/{chat.id}')
    messages = db_sess.query(Messages).filter(
        Messages.chat_id == chat.id
    ).order_by(Messages.created_date.asc()).all()
    return render_template(
        "chat.html",
        title="Чат",
        chat=chat,
        messages=messages,
        form=form
    )


@app.route('/my_chats')
@login_required
def my_chats():
    db_sess = db_session.create_session()
    chats = db_sess.query(Chats).filter(
        or_(
            Chats.buyer_id == current_user.id,
            Chats.seller_id == current_user.id
        )
    ).order_by(Chats.created_date.desc()).all()
    return render_template('my_chats.html', title='Мои чаты', chats=chats)


def main():
    db_session.global_init("db/avito.db")
    app.run()


if __name__ == '__main__':
    main()
