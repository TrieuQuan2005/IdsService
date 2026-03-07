import queue
import threading
import time
from typing import Optional, Tuple

import pydivert


class PacketCaptureService:

    def __init__(self, filter_str: str = "ip and (tcp or udp)", queue_size: int = 10000):
        self.filter_str = filter_str
        self._queue: queue.Queue[Tuple[bytes, float]] = queue.Queue(maxsize=queue_size)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._divert: Optional[pydivert.WinDivert] = None
        self.dropped_packets = 0

    def start(self) -> None:
        self._stop_event.clear()
        self._divert = pydivert.WinDivert(self.filter_str, flags=pydivert.Flag.SNIFF)
        self._divert.open()

        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

        if self._divert:
            self._divert.close()
            self._divert = None

        if self._thread:
            self._thread.join()
            self._thread = None

    def next_packet(self, timeout: float = 1.0) -> Optional[Tuple[bytes, float]]:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def _capture_loop(self) -> None:
        assert self._divert is not None

        for packet in self._divert:
            if self._stop_event.is_set():
                break

            try:
                raw_bytes = packet.raw
                timestamp = time.time()

                self._queue.put_nowait((raw_bytes, timestamp))

            except queue.Full:
                self.dropped_packets += 1