import asyncio

class UpdateQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.process_queue())

    async def process_queue(self):
        while True:
            update = await self.queue.get()
            from bot_commands import handle_update
            await handle_update(update)
            self.queue.task_done()

    def put(self, update):
        self.loop.create_task(self.queue.put(update))
