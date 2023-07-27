import aio_pika
import asyncio
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool
import os
from dotenv import load_dotenv
from eventCallback import callback

load_dotenv()

loop = asyncio.get_event_loop()

async def get_connection() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(
        host=os.getenv('RABBITMQ_HOST'),
        port=int(os.getenv('RABBITMQ_PORT')),
        login=os.getenv('RABBITMQ_USER'),
        password=os.getenv('RABBITMQ_PASSWORD')
    )

connectionPool: Pool = Pool(get_connection, loop=loop, max_size=10)


async def get_channel() -> aio_pika.channel:
    async with connectionPool.acquire() as connection:
        return await connection.channel()

channelPool : Pool = Pool(get_channel, loop=loop, max_size=10)

async def publish(queueName, message):
    async with channelPool.acquire() as channel:
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message,
                delivery_mode=2,
                content_type="text/plain",
                content_encoding="utf-8"
            ),
            routing_key=queueName
        )

async def consume():
    queueName = 'notificationService'
    async with channelPool.acquire() as channel:
        await channel.set_qos(1)

        queue = await channel.declare_queue(queueName, durable=True)

        async with queue.iterator() as iterator:
            async for message in iterator:
                callback(message.body)
                await message.ack()

if __name__ == "__main__":
    asyncio.run(consume())








