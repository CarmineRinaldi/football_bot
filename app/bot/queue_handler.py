# queue_handler.py
import asyncio

class UpdateQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False
        self._task = None  # Salviamo il task per poterlo fermare correttamente

    async def _process_queue(self):
        """Processa gli aggiornamenti nella coda."""
        while self.running:
            item = await self.queue.get()
            try:
                # Qui puoi gestire il tuo item (es. invio webhook, logging, ecc.)
                print(f"Processing item: {item}")
            except Exception as e:
                print(f"Errore durante il processing: {e}")
            finally:
                self.queue.task_done()

    async def start(self):
        """Avvia il processing della coda."""
        if not self.running:
            self.running = True
            self._task = asyncio.create_task(self._process_queue())

    async def add_to_queue(self, item):
        """Aggiunge un item alla coda in modo sicuro."""
        await self.queue.put(item)

    async def stop(self):
        """Ferma il processing della coda."""
        self.running = False
        if self._task:
            await self.queue.join()  # Aspetta che tutti gli item siano processati
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

# Creiamo un'istanza globale per usarla nel bot
update_queue = UpdateQueue()
