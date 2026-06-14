"""AWS IoT Core connection config (only needed for ``--transport aws``).

Resolved from an INI file (default ``config.ini``), overridable by environment
variables. The INI holds *paths* to the device credentials, never the
credentials themselves — the cert/key/CA files are gitignored.
"""

from __future__ import annotations

import configparser
import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(RuntimeError):
    """Raised when the AWS connection config is missing or incomplete."""


# INI key -> environment-variable override.
_ENV = {
    "endpoint": "LOADGEN_ENDPOINT",
    "port": "LOADGEN_PORT",
    "clientId": "LOADGEN_CLIENT_ID",
    "certFile": "LOADGEN_CERT",
    "keyFile": "LOADGEN_KEY",
    "caFile": "LOADGEN_CA",
    "garageId": "LOADGEN_GARAGE_ID",
    "sensorId": "LOADGEN_SENSOR_ID",
}


@dataclass(frozen=True)
class MqttConfig:
    endpoint: str
    client_id: str
    cert_file: str
    key_file: str
    ca_file: str
    port: int = 8883
    garage_id: str | None = None
    sensor_id: str | None = None


def _get(section: configparser.SectionProxy | dict, ini_key: str, default: str | None = None) -> str | None:
    env_key = _ENV.get(ini_key)
    if env_key and os.environ.get(env_key):
        return os.environ[env_key]
    value = section.get(ini_key, default)
    return value if value not in ("", None) else default


def load_mqtt_config(path: str | Path = "config.ini") -> MqttConfig:
    """Read the ``[aws]`` section, apply env overrides, and validate paths."""
    p = Path(path)
    parser = configparser.ConfigParser(interpolation=None)
    if p.exists():
        parser.read(p, encoding="utf-8")
    section = parser["aws"] if parser.has_section("aws") else {}

    endpoint = _get(section, "endpoint")
    cert_file = _get(section, "certFile")
    key_file = _get(section, "keyFile")
    ca_file = _get(section, "caFile")

    missing = [k for k, v in
               {"endpoint": endpoint, "certFile": cert_file,
                "keyFile": key_file, "caFile": ca_file}.items() if not v]
    if missing:
        raise ConfigError(
            f"missing AWS config: {', '.join(missing)} "
            f"(set them in {p} [aws] or via env {[_ENV[k] for k in missing]})"
        )

    for label, fpath in (("certFile", cert_file), ("keyFile", key_file), ("caFile", ca_file)):
        if not Path(fpath).exists():
            raise ConfigError(f"{label} not found at {fpath!r}")

    return MqttConfig(
        endpoint=endpoint,
        client_id=_get(section, "clientId", "virtual-loadgen"),
        cert_file=cert_file,
        key_file=key_file,
        ca_file=ca_file,
        port=int(_get(section, "port", "8883")),
        garage_id=_get(section, "garageId"),
        sensor_id=_get(section, "sensorId"),
    )
