import logging
import time
from typing import TYPE_CHECKING


from flask import Flask, jsonify
from utils import get_key
from tasks import create_hash_keys


from rmq_config import (
    get_connection,
    configure_logging,
    MQ_EXCHANGE,
    MQ_ROUTING_KEY,
)

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel

log = logging.getLogger(__name__)


def produce_message(channel: "BlockingChannel") -> None:
    queue = channel.queue_declare(queue=MQ_ROUTING_KEY)
    log.info("Declared queue %r %s", MQ_ROUTING_KEY, queue)
    message_body = get_key()
    log.info("Publish message %s", message_body)
    channel.basic_publish(
        exchange=MQ_EXCHANGE,
        routing_key=MQ_ROUTING_KEY,
        body=message_body,
    )
    log.warning("Published message %s", message_body)


app = Flask(__name__)

create_hash_keys.delay()

@app.route('/get_hash_key', methods=['GET'])
def get_hash_key():

    configure_logging(level=logging.WARNING)
    with get_connection() as connection:
        log.info("Created connection: %s", connection)
        with connection.channel() as channel:
            log.info("Created channel: %s", channel)
            produce_message(channel=channel)

    return ""


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
