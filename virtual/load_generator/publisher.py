"""MQTT publishing — the I/O boundary.

Two sinks behind one tiny interface:

* :class:`DryRunPublisher` — prints/counts messages, no network. Used for
  testing the model and pre-estimating volume/cost.
* :class:`MqttPublisher` — paho-mqtt over mutual TLS to AWS IoT Core.

``paho-mqtt`` is imported lazily so the simulator and ``--dry-run`` work even
when it is not installed.
"""

from __future__ import annotations

import ssl
import sys
from typing import Protocol, TextIO


class Publisher(Protocol):
    def publish(self, topic: str, payload: str, qos: int = 0) -> None: ...
    def close(self) -> None: ...


class DryRunPublisher:
    """Echo (and count) messages instead of sending them. Not a network transport."""

    def __init__(self, out: TextIO | None = None, *, echo: bool = True) -> None:
        self._out = out or sys.stdout
        self._echo = echo
        self.count = 0

    def publish(self, topic: str, payload: str, qos: int = 0) -> None:
        self.count += 1
        if self._echo:
            print(f"{topic} {payload}", file=self._out)

    def close(self) -> None:  # nothing to tear down
        pass


class MqttPublisher:
    """Publish to AWS IoT Core over mutual TLS (port 8883)."""

    def __init__(
        self,
        *,
        endpoint: str,
        client_id: str,
        cert_file: str,
        key_file: str,
        ca_file: str,
        port: int = 8883,
        keepalive: int = 60,
    ) -> None:
        try:
            import paho.mqtt.client as mqtt
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise RuntimeError(
                "paho-mqtt is required for --transport aws (pip install paho-mqtt)"
            ) from exc

        # paho 2.x requires an explicit callback API version; 1.x does not.
        if hasattr(mqtt, "CallbackAPIVersion"):
            client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=client_id,
                protocol=mqtt.MQTTv311,
                clean_session=True,
            )
        else:  # pragma: no cover - legacy paho
            client = mqtt.Client(
                client_id=client_id, protocol=mqtt.MQTTv311, clean_session=True
            )

        client.on_connect = lambda *a, **k: print(
            f"[mqtt] connected to {endpoint}:{port} as {client_id}", file=sys.stderr
        )
        client.on_disconnect = lambda *a, **k: print("[mqtt] disconnected", file=sys.stderr)

        # Mutual TLS with the device certificate. Port 8883 needs no ALPN.
        client.tls_set(
            ca_certs=ca_file,
            certfile=cert_file,
            keyfile=key_file,
            tls_version=ssl.PROTOCOL_TLS_CLIENT,
        )
        client.connect(endpoint, port, keepalive)
        client.loop_start()
        self._client = client

    def publish(self, topic: str, payload: str, qos: int = 0) -> None:
        info = self._client.publish(topic, payload, qos=qos)
        if qos > 0:
            info.wait_for_publish(timeout=10)

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()
