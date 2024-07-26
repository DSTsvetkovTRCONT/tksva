import os
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from time import time
from typing import Optional
from flask_login import UserMixin
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db, login
from hashlib import md5


'''
followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True)
)
'''

class DwhTablesInfo(db.Model):
    dwh_table_name: so.Mapped[str] = so.mapped_column(sa.String(140), primary_key=True)
    table_info = sa.Column('table_info', sa.JSON)
    timestamp: so.Mapped[datetime] = so.mapped_column(nullable=True)

    wants_to_refresh: so.Mapped[str] = so.mapped_column(sa.Boolean, default=False)
    wants_to_refresh_timestamp: so.Mapped[datetime] = so.mapped_column(nullable=True)

    gives_information: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    gives_information_timestamp: so.Mapped[datetime] = so.mapped_column(nullable=True)


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return 'Текущий пользователь: {}'.format(self.username)

    def get_posts(self, form_name):
        query = self.posts.select().where(User.id == self.id,
                                          Post.form_name == form_name,
                                          Post.task_status != "скрыта пользователем",
                                          Post.task_status != "скрыта менеджером очереди").order_by((Post.timestamp.desc()))
        files_to_download = [{"user_id": item.user_id,
                              "file_to_download": item.file_to_download,
                              "download_info": f"/download/{item.user_id}&{item.id}&{item.file_to_download}",
                              "file_to_download_path": os.path.join("static",
                                                                    "files_to_download",
                                                                    str(item.user_id),
                                                                    item.file_to_download),
                              "conditions": item.conditions,
                              "task_status": item.task_status} for item in db.session.scalars(query)]
        return files_to_download

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return

        return db.session.get(User, id)


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    form_name: so.Mapped[str] = so.mapped_column(sa.String(140))
    conditions = sa.Column('conditions', sa.JSON)
    task_status: so.Mapped[str] = so.mapped_column(sa.String(140))
    file_to_download: so.Mapped[str] = so.mapped_column(sa.String(140))

    task_status_timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))

    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.conditions)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
