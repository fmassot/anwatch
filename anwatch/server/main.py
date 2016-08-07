# -*- coding: utf-8 -*-

from flask import Flask, jsonify, Response, render_template
from playhouse.shortcuts import model_to_dict

from anwatch.server.stream import amendements_consumer
from ..models import Amendement


app = Flask(__name__)


@app.route("/api/amendements", methods=['GET'])
def get_last_amendements():
    app.logger.debug('get last amendements')
    amendements = [model_to_dict(a) for a in Amendement.select().order_by(Amendement.created_at.desc()).limit(10)]

    return jsonify({'amendements': amendements})


@app.route("/api/amendements/stream", methods=['GET'])
def stream_amendements():
    app.logger.debug('stream amendements')
    return Response(amendements_consumer(), content_type='text/event-stream')


@app.route("/amendements", methods=['GET'])
def amendements_home():
    return render_template('amendements_home.html')


