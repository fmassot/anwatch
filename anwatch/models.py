# -*- coding: utf-8 -*-

import datetime
from peewee import Model, CharField, DateTimeField, CompositeKey, TextField

from .db import database


class BaseModel(Model):
    class Meta:
        database = database


class AmendementSummary(BaseModel):
    id = CharField()
    created_at = DateTimeField(default=datetime.datetime.now())
    date_depot = CharField()
    designation_alinea = CharField()
    designation_article = CharField()
    instance = CharField()
    legislature = CharField()
    mission_visee = CharField(null=True)
    num_amend = CharField()
    num_init = CharField()
    signataires = CharField()
    sort = CharField(null=True)
    titre_dossier_legislatif = CharField()
    url_dossier_legislatif = CharField()
    url_amend = CharField()

    class Meta:
        primary_key = CompositeKey('id', 'created_at')

    @classmethod
    def get_last(cls, _id):
        return cls.select().where(AmendementSummary.id == _id) \
            .order_by(AmendementSummary.created_at.desc()) \
            .first()


class Amendement(BaseModel):
    created_at = DateTimeField(default=datetime.datetime.now())
    url = CharField()
    num_amtxt = CharField()
    amend_parent = CharField(null=True)
    url_dossier = CharField()
    num_init = CharField()
    etape = CharField()
    deliberation = CharField(null=True)
    titre_init = CharField()
    num_partie = CharField()
    designation_article = CharField()
    url_division = CharField()
    designation_alinea = CharField(null=True)
    mission = CharField(null=True)
    auteurs = CharField(null=True)
    auteur_id = CharField()
    groupe_id = CharField()
    cosignataires_id = CharField(null=True)
    seance = CharField()
    sort = CharField(null=True)
    date_badage = CharField(null=True)
    date_sort = CharField(null=True)
    ordre_texte = CharField(null=True)
    code = CharField(null=True)
    refcode = CharField(null=True)
    legislature = CharField()
    dispositif = TextField()
    expose = TextField()
    num_amend = CharField()

    @classmethod
    def get_last_by_url(cls, url):
        return cls.select().where(Amendement.url == url) \
            .order_by(Amendement.created_at.desc()) \
            .first()
