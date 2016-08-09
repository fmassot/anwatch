# -*- coding: utf-8 -*-

import pika
import time
import requests
import logging
import json

from enum import Enum
from datetime import datetime
from playhouse.shortcuts import model_to_dict
from anpy.service import AmendementSearchService
from anpy.parsing.amendement_parser import parse_amendement

from ..models import AmendementSummary, Amendement
from ..config import AMENDEMENT_PARAMS, AMENDEMENT_EXCHANGE, SLEEP_TIME

LOGGER = logging.getLogger(__name__)

MAX_CRAWL_RETRY = 5


def crawl_amendement_summaries():
    retry_count = 0

    LOGGER.debug('init channel')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=AMENDEMENT_EXCHANGE, type='fanout')

    LOGGER.debug('start amendements crawling')

    while True and retry_count <= MAX_CRAWL_RETRY:
        try:
            it = AmendementSearchService().iterator(**AMENDEMENT_PARAMS)
            amendements = [row for searchResult in it for row in searchResult.results]

            LOGGER.info('crawled %s amendements', len(amendements))

            for event in make_diff_and_download(amendements):
                LOGGER.info('publish amendement event %s', event)
                channel.basic_publish(exchange=AMENDEMENT_EXCHANGE, routing_key='', body=event.to_json())

            LOGGER.info('sleep %s seconds', SLEEP_TIME)
            time.sleep(SLEEP_TIME)

        except Exception as e:
            retry_count += 1
            LOGGER.error("error when crawling amendements: %s", e)
            LOGGER.error("sleep 10 secondes before restarting", e)
            time.sleep(60)

    if retry_count >= MAX_CRAWL_RETRY:
        LOGGER.info("stop crawling because retry count is too high: %s", retry_count)


def make_diff_and_download(amendement_summaries):
    LOGGER.debug('make diff with amendement summaries in db')

    ids = [am.id for am in amendement_summaries]
    last_amendements_by_id = dict((am.id, am) for am in AmendementSummary.get_last(ids))

    for current_amendement_summary in amendement_summaries:
        last_amendement_summary = last_amendements_by_id.get(current_amendement_summary.id)

        event_type = get_event_type(last_amendement_summary, current_amendement_summary)

        if event_type != EventType.UNMODIFIED:
            LOGGER.debug('create amendement summary %s' % current_amendement_summary)
            current_amendement_summary = AmendementSummary.create(**current_amendement_summary.__dict__)

            download_response = None

            try:
                download_response = download(current_amendement_summary.url_amend)
            except Exception as e:
                LOGGER.warn("failed to download amendement %s, sleep 10 seconds", current_amendement_summary.url_amend)
                time.sleep(10)

            if download_response:
                amendement = parse_amendement(download_response.url, download_response.content)
                last_amendement = Amendement.get_last_by_url(current_amendement_summary.url_amend)

                LOGGER.debug('create amendement %s' % amendement)
                new_amendement = Amendement.create(**amendement.__dict__)

                event = CrawlEvent(event_type=event_type, previous=last_amendement, current=new_amendement)

                LOGGER.debug('amendement event %s' % event)

                yield event


def get_event_type(old_amendement_summary, new_amendement_summary):
    if old_amendement_summary is None:
        return EventType.NEW

    if old_amendement_summary.sort != new_amendement_summary.sort:
        return EventType.SORT_UPDATED

    return EventType.UNMODIFIED


def download(url):
    # TODO : add retry handler ?
    try:
        LOGGER.debug('download amendement %s', url)
        return ParsedResponse(url=url, content=requests.get(url).content)
    except Exception as e:
        LOGGER.debug('error when downloading amendement %s: %s', url, e)
        raise e


class ParsedResponse(object):
    def __init__(self, url, content=None, exception=None):
        self.url = url
        self.content = content
        self.exception = exception


class CrawlEvent(object):
    def __init__(self, event_type, previous=None, current=None):
        self.event_type = event_type
        self.previous = previous
        self.current = current

    def to_json(self):
        return JSONEncoder().encode({
            'event_type': self.event_type.value,
            'previous': None if self.previous is None else model_to_dict(self.previous),
            'current': None if self.current is None else model_to_dict(self.current),
        })

    def __repr__(self):
        return 'CrawlEvent(event_type=%s, previous=%s, current=%s)' % (self.event_type, self.previous, self.current)


class EventType(Enum):
    NEW = 'NEW'
    SORT_UPDATED = 'SORT_UPDATED'
    UNMODIFIED = 'UNMODIFIED'


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)