# @@@SNIPSTART python-project-template-run-workflow-hello-world
import asyncio

from run_worker import SayHello
from temporalio.client import Client
from config import TEMPORAL_HOST, TEMPORAL_NAMESPACE, TASK_QUEUE, TLS_CONFIG


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(
        TEMPORAL_HOST,
        namespace=TEMPORAL_NAMESPACE,
        tls=TLS_CONFIG
    )

    # Execute a workflow
    result = await client.execute_workflow(
        SayHello.run, "Temporal", id="hello-workflow", task_queue=TASK_QUEUE
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
# @@@SNIPEND
