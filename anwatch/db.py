
from peewee import SqliteDatabase
from .config import DATABASE

database = SqliteDatabase(DATABASE)