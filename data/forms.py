from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (BooleanField, EmailField, PasswordField, SelectField,
                     StringField, SubmitField)
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                NumberRange)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[Length(max=100)])
    surname = StringField('Фамилия', validators=[Length(max=100)])
    phone = StringField('Номер телефона', validators=[Length(min=10, max=11)])
    city = StringField('Город', validators=[Length(max=100)])
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField(
        'Пароль', validators=[DataRequired(), Length(min=8)]
    )
    password_again = PasswordField(
        'Введите пароль',
        validators=[
            DataRequired(),
            EqualTo('password', message='Пароли не совпадают')
        ]
    )
    submit = SubmitField('Зарегистрироваться')


class CreateGoodForm(FlaskForm):
    title = StringField('Название', validators=[Length(min=1, max=100)])
    description = StringField('Описание', validators=[Length(min=1, max=100)])
    image_fn = FileField('Прикрепить картинку')
    price = IntegerField(
        'Стоимость', validators=[NumberRange(min=1, max=10**6)]
    )
    category_id = SelectField('Категория', coerce=int)
    submit = SubmitField('Готово')


class EditProfileForm(FlaskForm):
    name = StringField('Имя', validators=[Length(min=1, max=100)])
    surname = StringField('Фамилия', validators=[Length(min=1, max=100)])
    phone = StringField('Номер телефона', validators=[Length(min=10, max=11)])
    city = StringField('Город', validators=[Length(min=1, max=100)])
    address = StringField('Адрес', validators=[Length(min=1, max=200)])
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    submit = SubmitField('Редактировать')


class MessageForm(FlaskForm):
    text = TextAreaField(
        'Сообщение', validators=[DataRequired(), Length(min=1, max=2000)]
    )
    submit = SubmitField('Отправить')
