import pika

import logging
from ..config import AMENDEMENT_EXCHANGE, RABBIT_MQ_HOST

LOGGER = logging.getLogger(__name__)


def amendements_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_MQ_HOST))

    channel = connection.channel()

    channel.exchange_declare(exchange=AMENDEMENT_EXCHANGE, type='fanout')

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange=AMENDEMENT_EXCHANGE, queue=queue_name)

    LOGGER.info(' [*] Waiting for amendements')

    for method, properties, body in channel.consume(queue_name, no_ack=True):
        yield 'data: %s\n\n' % body
