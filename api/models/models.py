# -*- coding: UTF-8 -*-
"""
models.py
- Data classes for the surveyapi application
"""
import json

from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask import current_app
from sqlalchemy import JSON

app = current_app
db = SQLAlchemy()


def row2dict(row):
    if row is None:
        return ""
    d = {}
    for column in row.__table__.columns:
        if isinstance(getattr(row, column.name), str):
            d[column.name] = getattr(row, column.name)
        elif isinstance(getattr(row, column.name), datetime):
            d[column.name] = str(getattr(row, column.name))
        else:
            # d[column.name] = str(getattr(row, column.name))
            d[column.name] = getattr(row, column.name)
    return d


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_on = db.Column(db.DateTime, default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)


class User(Base, db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))
    name = db.Column(db.String(32))
    email = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean, default=True)
    dept = db.column(db.String(32))
    # email = db.Column(db.String(32))
    mobile = db.Column(db.String(32))
    wxid = db.Column(db.String(128))
    xcxid = db.Column(db.String(128))
    UnionID = db.Column(db.String(128))
    wxName = db.Column(db.String(50))
    wxpicurl = db.Column(db.String(128))
    roles = db.relationship(
        'Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self):
        self.password = generate_password_hash(self.password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Role(Base, db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        # return '<role %r>' % self.name
        return self.name


# for flask-security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class Area(db.Model):
    """
    Area 包括：City 城市, City Code (考虑用城市的邮编）, 坐标（ 4个角，经纬度），区域中心点坐标（经纬度），区域代码，区域名称，区域说明，区域价格表（多个区域可以对应 一个价格表）
    """
    __tablename__ = 'areas'
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(80), nullable=False, unique=True)
    city_code = db.Column(db.String(10), unique=True)
    locations = db.Column(JSON())
    # center_axis = db.Column(db.String(80))
    area_num = db.Column(db.Integer, unique=True)
    area_description = db.Column(db.String(80))
    rate_id = db.Column(db.Integer, db.ForeignKey('rates.id'))

    def __repr__(self):
        return self.name


class Area_rate(Base, db.Model):
    __tablename__ = 'area_rates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    rate_level = db.Column(db.Float())
    area = db.relationship('Area', backref='rate', lazy='dynamic')

    def __repr__(self):
        return self.rate_level
