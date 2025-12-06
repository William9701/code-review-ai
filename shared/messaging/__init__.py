"""
Messaging shared module
"""

from .queue import MessageQueue, get_message_queue, queue_task

__all__ = ["MessageQueue", "get_message_queue", "queue_task"]
