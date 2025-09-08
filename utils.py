import asyncio

async def show_typing(func, *args, **kwargs):
    """Mostra messaggio di attesa se la funzione impiega troppo"""
    task = asyncio.create_task(func(*args, **kwargs))
    await asyncio.sleep(1.5)  # messaggio attesa
    if not task.done():
        return "⏳ Attendi..."
    return await task
