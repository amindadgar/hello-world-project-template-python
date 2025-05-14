# @@@SNIPSTART python-project-template-run-worker
import logging
import asyncio

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from activities import say_hello
from workflows import SayHello
from config import TEMPORAL_HOST, TEMPORAL_NAMESPACE, TASK_QUEUE, TLS_CONFIG

logging.basicConfig(level=logging.INFO)

async def main():
    client = await Client.connect(
        TEMPORAL_HOST,
        namespace=TEMPORAL_NAMESPACE,
        tls=TLS_CONFIG if TLS_CONFIG else False,
    )

    logging.info(f"Connected to Temporal server at {TEMPORAL_HOST}")

    # Run the worker
    worker = Worker(
        client, task_queue=TASK_QUEUE, workflows=[SayHello], activities=[say_hello]
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
# @@@SNIPEND
