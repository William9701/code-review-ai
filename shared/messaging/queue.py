"""
Message queue abstraction for RabbitMQ
"""
import os
import json
import logging
from typing import Callable, Any, Optional, Dict
from functools import wraps
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


class MessageQueue:
    """
    RabbitMQ message queue wrapper
    """

    def __init__(self, connection_url: Optional[str] = None):
        """
        Initialize message queue connection

        Args:
            connection_url: RabbitMQ connection URL (amqp://user:pass@host:port/)
        """
        self.connection_url = connection_url or os.getenv(
            "RABBITMQ_URL",
            "amqp://codereview:changeme@localhost:5672/"
        )
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[BlockingChannel] = None
        self._setup_connection()

    def _setup_connection(self) -> None:
        """Establish connection to RabbitMQ"""
        try:
            parameters = pika.URLParameters(self.connection_url)
            parameters.heartbeat = 600
            parameters.blocked_connection_timeout = 300

            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare exchanges
            self._declare_exchanges()

            # Declare queues
            self._declare_queues()

            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def _declare_exchanges(self) -> None:
        """Declare exchanges"""
        if not self.channel:
            return

        exchanges = [
            ("pr.events", "topic"),  # Pull request events
            ("analysis.events", "topic"),  # Analysis events
            ("github.events", "topic"),  # GitHub API events
            ("notifications", "fanout"),  # Notification broadcasts
        ]

        for exchange_name, exchange_type in exchanges:
            self.channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_type,
                durable=True
            )

    def _declare_queues(self) -> None:
        """Declare queues"""
        if not self.channel:
            return

        queues = [
            # Webhook events
            "webhook.pr.opened",
            "webhook.pr.synchronized",
            "webhook.pr.closed",

            # Analysis queues
            "analysis.static",
            "analysis.llm",
            "analysis.results",

            # GitHub operations
            "github.comments",
            "github.status",

            # Notifications
            "notifications.email",
            "notifications.slack",

            # Dead letter queue
            "dlq",
        ]

        for queue_name in queues:
            self.channel.queue_declare(
                queue=queue_name,
                durable=True,
                arguments={
                    "x-message-ttl": 86400000,  # 24 hours
                    "x-max-length": 10000,
                }
            )

        # Bind queues to exchanges
        self._bind_queues()

    def _bind_queues(self) -> None:
        """Bind queues to exchanges with routing keys"""
        if not self.channel:
            return

        bindings = [
            ("webhook.pr.opened", "pr.events", "pr.opened"),
            ("webhook.pr.synchronized", "pr.events", "pr.synchronized"),
            ("webhook.pr.closed", "pr.events", "pr.closed"),
            ("analysis.static", "analysis.events", "analysis.static.*"),
            ("analysis.llm", "analysis.events", "analysis.llm.*"),
            ("analysis.results", "analysis.events", "analysis.completed"),
            ("github.comments", "github.events", "github.comment.*"),
            ("github.status", "github.events", "github.status.*"),
        ]

        for queue, exchange, routing_key in bindings:
            self.channel.queue_bind(
                queue=queue,
                exchange=exchange,
                routing_key=routing_key
            )

    def publish(
        self,
        exchange: str,
        routing_key: str,
        message: Dict[str, Any],
        priority: int = 5
    ) -> None:
        """
        Publish message to exchange

        Args:
            exchange: Exchange name
            routing_key: Routing key
            message: Message payload (will be JSON serialized)
            priority: Message priority (0-9, default 5)
        """
        if not self.channel:
            raise RuntimeError("Channel not initialized")

        try:
            properties = BasicProperties(
                delivery_mode=2,  # Persistent
                priority=priority,
                content_type="application/json",
            )

            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=properties
            )

            logger.debug(f"Published message to {exchange}/{routing_key}")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise

    def consume(
        self,
        queue: str,
        callback: Callable[[Dict[str, Any]], None],
        prefetch_count: int = 1
    ) -> None:
        """
        Consume messages from queue

        Args:
            queue: Queue name
            callback: Callback function to process messages
            prefetch_count: Number of messages to prefetch
        """
        if not self.channel:
            raise RuntimeError("Channel not initialized")

        self.channel.basic_qos(prefetch_count=prefetch_count)

        def on_message(
            ch: BlockingChannel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes
        ) -> None:
            """Message handler"""
            try:
                message = json.loads(body)
                logger.debug(f"Received message from {queue}")

                # Process message
                callback(message)

                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        self.channel.basic_consume(
            queue=queue,
            on_message_callback=on_message
        )

        logger.info(f"Started consuming from {queue}")
        self.channel.start_consuming()

    def close(self) -> None:
        """Close connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")


# Singleton instance
_queue_instance: Optional[MessageQueue] = None


def get_message_queue() -> MessageQueue:
    """
    Get or create message queue singleton

    Returns:
        MessageQueue instance
    """
    global _queue_instance

    if _queue_instance is None:
        _queue_instance = MessageQueue()

    return _queue_instance


def queue_task(exchange: str, routing_key: str):
    """
    Decorator to publish function result to queue

    Usage:
        @queue_task("analysis.events", "analysis.static.python")
        def analyze_python_code(code: str):
            return {"result": "..."}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            queue = get_message_queue()
            queue.publish(exchange, routing_key, result)
            return result
        return wrapper
    return decorator
