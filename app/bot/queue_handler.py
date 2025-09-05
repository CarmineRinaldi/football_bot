# queue_handler.py
import asyncio

class UpdateQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False

    async def process_queue(self):
        """Processa gli aggiornamenti nella coda."""
        self.running = True
        while self.running:
            item = await self.queue.get()
            try:
                # Qui puoi gestire il tuo item (es. invio webhook, logging, ecc.)
                print(f"Processing item: {item}")
            except Exception as e:
                print(f"Errore durante il processing: {e}")
            finally:
                self.queue.task_done()

    async def add_to_queue(self, item):
        """Aggiunge un item alla coda in modo sicuro."""
        await self.queue.put(item)

    async def stop(self):
        """Ferma il processing della coda."""
        self.running = False
        await self.queue.join()  # Aspetta che tutti gli item siano processati

# Esempio di utilizzo (non da lanciare in Render direttamente)
# async def main():
#     uq = UpdateQueue()
#     asyncio.create_task(uq.process_queue())
#     await uq.add_to_queue("Test item")
#     await asyncio.sleep(1)
#     await uq.stop()
#
# asyncio.run(main())
