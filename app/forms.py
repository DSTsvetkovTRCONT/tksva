from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField
from wtforms.validators import  ValidationError, DataRequired, Email, EqualTo, Length, InputRequired, AnyOf
from app.validators import DownloadForRailway1048575, DownloadForStation1048575, DateInRange
import sqlalchemy as sa
from app import db
from app.models import User
from datetime import datetime
from psql import get_dwh_table_info


class DownloadForRailwayForm(FlaskForm):
    try:
        table_info_dict = get_dwh_table_info()
    except Exception:
        table_info_dict = {'railway_names': '',
                           'min_date': '1970-01-01 00:00:00',
                           'max_date': '1970-01-01 00:00:00'}

    railways_list = table_info_dict['railway_names'].split('|')
    min_date_in_dwh_table = datetime.strptime(table_info_dict['min_date'],
                                              "%Y-%m-%d %H:%M:%S")
    max_date_in_dwh_table = datetime.strptime(table_info_dict['max_date'],
                                              "%Y-%m-%d %H:%M:%S")

    railway_name = StringField(label='Выберите дорогу',
                               validators=[InputRequired("Выберите дорогу!"),
                                           AnyOf(values=railways_list,
                                                 message="Выбранное значение отсутствует в списке дорог!")])

    start_date = DateField(label=f'Введите начальную дату (первая в DWH: {min_date_in_dwh_table})',
                           validators=[DataRequired(message="Дата не введена или введена неверно!"),
                                       DateInRange()])

    finish_date = DateField(label=f'Введите конечную дату (последняя в DWH: {max_date_in_dwh_table})',
                            validators=[DataRequired(message="Дата не введена или введена неверно!"),
                                        DateInRange(),
                                        DownloadForRailway1048575()])

    railway_name_input_title = ("Введите несколько любых идущих подряд букв из любой части "
                                "названия дороги. Выберите нужную станцию в выпадающем списке.")
    submit = SubmitField('Сформировать выгрузку')


class DownloadForStationForm(FlaskForm):

    table_info_dict = get_dwh_table_info()
    stations_list = table_info_dict['station_names'].split('|')
    min_date_in_dwh_table = table_info_dict['min_date']
    max_date_in_dwh_table = table_info_dict['max_date']

    station_name = StringField(label='Выберите станцию',
                               validators=[InputRequired("Выберите станцию!"),
                                           AnyOf(values=stations_list,
                                                 message="Выбранное значение отсутствует в списке станций!")])

    start_date = DateField(label=f'Введите начальную дату (первая в DWH: {min_date_in_dwh_table})',
                           validators=[DataRequired(message="Дата не введена или введена неверно!"),
                                       DateInRange()])

    finish_date = DateField(label=f'Введите конечную дату (последняя в DWH: {max_date_in_dwh_table})',
                            validators=[DataRequired(message="Дата не введена или введена неверно!"),
                                        DateInRange(),
                                        DownloadForStation1048575()])

    station_name_input_title = ("Введите несколько любых идущих подряд букв "
                                "из любой части названия станции. "
                                "Выберите нужную станцию в выпадающем списке.")

    submit = SubmitField('Сформировать выгрузку')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Подключиться')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == self.username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class ClearTasksList(FlaskForm):
    submit = SubmitField('Очистить информацию о загруженных')
