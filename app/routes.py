import os
from dotenv import load_dotenv
from psql import is_already_queued, file_is_already_ready, get_dwh_table_info, mark_as_downloded
from flask import render_template, flash, redirect, url_for, request, send_file
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import (LoginForm, DownloadForRailwayForm, DownloadForStationForm, RegistrationForm, EditProfileForm,
                       EmptyForm, PostForm, ResetPasswordForm, ResetPasswordRequestForm, ClearTasksList)
from app.models import User, Post
from urllib.parse import urlsplit
from colorama import Fore
from datetime import datetime, timezone
# from app.email import send_password_reset_email
from psql import clear_if_complited, get_queued_posts_qty

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('.env'):
    load_dotenv(os.path.join(basedir, '.env'))
else:
    load_dotenv(os.path.join(basedir, '.envexample'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('download_for_railway'))
    form = LoginForm()
    

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))        
        if user is None or not user.check_password(form.password.data):
            flash('Неправильные username или password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('login')
        return redirect(url_for('login'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        if not os.path.exists(os.path.join('app','static','files_to_download')):
            os.mkdir(os.path.join('app','static','files_to_download'))
        if not os.path.exists(os.path.join('app','static','files_to_download', str(user.id))):
            os.mkdir(os.path.join('app','static','files_to_download', str(user.id)))

        flash('Новый пользователь успешно зарегистрирован!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/download-for-railway', methods=['GET','POST'])
@login_required
def download_for_railway():
    form = DownloadForRailwayForm() 
    form_class_name = (form.__class__.__name__)
    if form.validate_on_submit():

        file_to_download = (f"{form_class_name}_"
                            f"railway_name_{form.railway_name.data}_"
                            f"start_date_{form.start_date.data}_"
                            f"finish_date_{form.finish_date.data}.csv".replace('"',''))
        
        conditions = {'railway_name':form.railway_name.data,
                      'start_date':(form.start_date.data.strftime("%Y-%m-%d")),
                      'finish_date':(form.finish_date.data.strftime("%Y-%m-%d"))}
        
        if is_already_queued(current_user.id, form_class_name, conditions) > 0:
            flash(f'дорога: {form.railway_name.data}, '
                  f'начальная дата: {form.start_date.data}, '
                  f'конечная дата: {form.finish_date.data} - такая задача уже есть в очереди')
            
            return redirect(url_for('download_for_railway'))
        
        if file_is_already_ready(current_user.id, form_class_name, conditions) > 0:
            flash(f'дорога: {form.railway_name.data}, '
                  f'начальная дата: {form.start_date.data}, '
                  f'конечная дата: {form.finish_date.data} - файл для этой задачи уже подготовлен') 
            return redirect(url_for('download_for_railway'))

        p = Post(conditions=conditions,
                 form_name=form_class_name,
                 user_id=current_user.id,
                 task_status="в очереди",
                 file_to_download=file_to_download)
        db.session.add(p)
        db.session.commit()

        flash(f'дорога: {form.railway_name.data}, '
              f'начальная дата: {form.start_date.data}, '
              f'конечная дата: {form.finish_date.data} - '
              f'задача добавлена в очередь')

        return redirect(url_for('download_for_railway'))

    dwh_table_info_dict = get_dwh_table_info()
    railways_list = dwh_table_info_dict['railway_names'].split('|')
    min_date_in_dwh_table = datetime.strptime(dwh_table_info_dict['min_date'],
                                              "%Y-%m-%d %H:%M:%S").date()
    max_date_in_dwh_table = datetime.strptime(dwh_table_info_dict['max_date'],
                                              "%Y-%m-%d %H:%M:%S").date()

    current_user_posts = list(current_user.get_posts(form_class_name))

    # if current_user_posts:
    #     current_user_last_post = current_user_posts[0]
    # else:
    #     current_user_last_post = {"conditions": {"railway_name": railways_list[1],
    #                                              "start_date": min_date_in_dwh_table,
    #                                              "finish_date": max_date_in_dwh_table}}

    frame_in_page_height = len(current_user_posts)*60 + 190

    return render_template('download_for_railway.html',
                           form=form,
                           railways_list=railways_list,
                           frame_in_page_height=frame_in_page_height,
                           # current_user_last_post=current_user_last_post,
                           user_name=current_user,
                           debug_info=current_user)


@app.route('/download-for-station', methods=['GET', 'POST'])
@login_required
def download_for_station():
    form = DownloadForStationForm()
    form_class_name = (form.__class__.__name__)
    if form.validate_on_submit():

        file_to_download = (f"{form_class_name}_station_name_"
                            f"{form.station_name.data}_start_date_"
                            f"{form.start_date.data}_finish_date_{form.finish_date.data}.csv".replace('"', ''))

        conditions = {'station_name': form.station_name.data,
                      'start_date': (form.start_date.data.strftime("%Y-%m-%d")),
                      'finish_date': (form.finish_date.data.strftime("%Y-%m-%d"))}

        if is_already_queued(current_user.id, form_class_name, conditions) > 0:
            flash(f'станция: {form.station_name.data}, '
                  f'начальная дата: {form.start_date.data}, '
                  f'конечная дата: {form.finish_date.data} - такая задача уже есть в очереди')

            return redirect(url_for('download_for_station'))

        if file_is_already_ready(current_user.id, form_class_name, conditions) > 0:
            flash(f'станция: {form.station_name.data}, '
                  f'начальная дата: {form.start_date.data}, '
                  f'конечная дата: {form.finish_date.data} - файл для этой задачи уже подготовлен')

            return redirect(url_for('download_for_station'))

        p = Post(conditions=conditions,
                 form_name=form_class_name,
                 user_id=current_user.id,
                 task_status="в очереди",
                 file_to_download=file_to_download)

        db.session.add(p)
        db.session.commit()

        flash(f'станция: {form.station_name.data}, '
              f'начальная дата: {form.start_date.data}, '
              f'конечная дата: {form.finish_date.data} - задача добавлена в очередь')

        return redirect(url_for('download_for_station'))

    dwh_table_info_dict = get_dwh_table_info()
    stations_list = dwh_table_info_dict['station_names'].split('|')
    min_date_in_dwh_table = datetime.strptime(dwh_table_info_dict['min_date'], "%Y-%m-%d %H:%M:%S").date()
    max_date_in_dwh_table = datetime.strptime(dwh_table_info_dict['max_date'], "%Y-%m-%d %H:%M:%S").date()

    current_user_posts = list(current_user.get_posts(form_class_name))

    # if current_user_posts:
    #     current_user_last_post = current_user_posts[0]
    # else:
    #    current_user_last_post = {"conditions": {"station_name": stations_list[1],
    #                                             "start_date": min_date_in_dwh_table,
    #                                             "finish_date": max_date_in_dwh_table}}

    frame_in_page_height = len(current_user_posts)*60 + 190

    return render_template('download_for_station.html',
                           form=form,
                           stations_list=stations_list,
                           frame_in_page_height=frame_in_page_height,
                           # current_user_last_post=current_user_last_post,
                           user_name=current_user,
                           debug_info=(min_date_in_dwh_table))


@app.route('/frame-in-frame/<frame_class_name>', methods=['GET', 'POST'])
@login_required
def frame_in_frame(frame_class_name):
    current_user_posts = list(current_user.get_posts(frame_class_name))
    return render_template('frame_in_frame.html',
                           form_class_name=frame_class_name,
                           current_user_posts=current_user_posts)


@app.route('/frame-in-page/<form_class_name>', methods=['GET', 'POST'])
@login_required
def frame_in_page(form_class_name):

    form = ClearTasksList(current_user.username)

    if request.method == 'POST':
        clear_if_complited(current_user.id, form_class_name)
        return redirect(f"/frame-in-page/{form_class_name}")

    queued_posts_qty_dict = get_queued_posts_qty(current_user.id)
    frame_in_frame_height = len(list(current_user.get_posts(form_class_name)))*60+20
    return render_template('frame_in_page.html',
                           frame_in_frame_height=frame_in_frame_height,
                           form_class_name=form_class_name,
                           all_queued_posts_qty=queued_posts_qty_dict['all_queued_posts_qty'],
                           own_queued_posts_qty=queued_posts_qty_dict['own_queued_posts_qty'],
                           form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/download/<download_info>', methods=['GET', 'POST'])
def downloader(download_info):
    file_to_download_path = (f"/static/files_to_download/"
                             f"{download_info.split('&')[0]}/{download_info.split('&')[2]}")
    task_id = int(download_info.split("&")[1])
    mark_as_downloded(task_id)

    return redirect(file_to_download_path)
