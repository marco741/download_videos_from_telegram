from telethon import TelegramClient
import config
import time
from os import path
from pathlib import Path
import asyncio

client = TelegramClient('anon', config.API_ID, config.API_HASH)


class ProgressPool:
    def __init__(self):
        self._current = 0
        self.last_current = 0
        self.last_time = 0
        self.progress = {}

    @property
    def total(self):
        return sum(p['total'] for p in self.progress.values())

    @property
    def current(self):
        self.last_current = self._current
        self._current = sum(p['current'] for p in self.progress.values())
        return self._current

    def calculate_speed(self, current_time, current=None):
        if current == None:
            current = self.current
        return (current - self.last_current) / (current_time - self.last_time)

    @property
    def downloading(self):
        return sum([p['total'] != p['current'] or p['total'] == 0 for p in self.progress.values()])

    def __call__(self, msg_id):
        self.progress[msg_id] = dict(current=0, total=0)

        def callback(current, total):
            self.progress[msg_id]["time"] = time.time()
            self.progress[msg_id]["current"] = current
            if self.progress[msg_id]["total"] == 0:
                self.progress[msg_id]["total"] = total
            self.debounced_print_status()
        return callback

    def debounced_print_status(self):
        current_time = time.time()
        if current_time - self.last_time < config.PRINT_INTERVAL:
            return
        total = self.total
        if total == 0:
            print("Waiting for files to start downloading...")
            return
        current = self.current
        speed = self.calculate_speed(current_time, current)
        print(f'\r{current/config.MB:8.1f} of {total/config.MB:8.1f} MB ({current / total:6.2%}) --- {speed/config.MB:8.2f} MB/s --- {self.downloading} of {len(self.progress)} files downloading', end="")
        self.last_time = current_time


async def main():
    save_path = Path(path.join(".", config.VIDEO_DIRECTORY, config.SEARCH_TEXT))

    progress_pool = ProgressPool()

    tasks = []
    async for msg in client.iter_messages(config.CHANNEL_ID, limit=50, search=config.SEARCH_TEXT, wait_time=0):
        if msg.media is not None:
            tasks.append(client.download_media(msg, file=save_path.joinpath(msg.message), progress_callback=progress_pool(msg.id)))

    await asyncio.gather(*tasks)

with client:
    client.loop.run_until_complete(main())
