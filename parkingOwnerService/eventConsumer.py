import aio_pika
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool
import asyncio
import os
from dotenv import load_dotenv
from eventCallback import callback

load_dotenv()

loop = asyncio.get_event_loop()

async def getConnection() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(
        host=os.getenv('RABBITMQ_HOST'),
        port=int(os.getenv('RABBITMQ_PORT')),
        login=os.getenv('RABBITMQ_USER'),
        password=os.getenv('RABBITMQ_PASSWORD')
    )

connectionPool : Pool = Pool(getConnection, max_size=10, loop=loop)


async def getChannel() -> aio_pika.Channel:
    async with connectionPool.acquire() as connection:
        return await connection.channel()


channelPool : Pool = Pool(getChannel, max_size=10, loop=loop)

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
    queueName  = 'parkingOwnerService'
    async with channelPool.acquire() as channel:
        await channel.set_qos(1)

        queue = await channel.declare_queue(queueName, durable=True)

        async with queue.iterator() as iterator:
            async for message in iterator:
                await callback(message.body)
                await message.ack()

if __name__ == "__main__":
    asyncio.run(consume())


