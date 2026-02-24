import queue
import threading
import time
from typing import Optional, Tuple
from scapy.all import AsyncSniffer, raw


class PacketCaptureService:

    def __init__(self, iface: str, queue_size: int = 10000):
        self.iface = iface
        self._queue: queue.Queue[Tuple[bytes, float]] = queue.Queue(maxsize=queue_size)
        self._stop_event = threading.Event()
        self._sniffer: Optional[AsyncSniffer] = None
        self.dropped_packets = 0

    def start(self) -> None:
        self._stop_event.clear()
        self._sniffer = AsyncSniffer(
            iface=self.iface,
            prn=self._on_packet,
            store=False,
        )
        self._sniffer.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._sniffer:
            self._sniffer.stop()
            self._sniffer = None

    def next_packet(self, timeout: float = 1.0) -> Optional[Tuple[bytes, float]]:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def _on_packet(self, pkt) -> None:
        if self._stop_event.is_set():
            return

        try:
            raw_bytes = raw(pkt)
            timestamp = getattr(pkt, "time", None) or time.time()
            self._queue.put_nowait((raw_bytes, timestamp))
        except queue.Full:
            self.dropped_packets += 1
