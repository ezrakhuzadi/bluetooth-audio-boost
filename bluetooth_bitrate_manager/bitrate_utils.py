"""
Utility helpers for decoding SBC codec information and bitrate calculations.
Shared by both GUI and CLI tooling so we have a single source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
import subprocess
import sys
from typing import Iterable, Optional


def _ceil_div(numerator: int, denominator: int) -> int:
    """Integer ceiling division."""
    return (numerator + denominator - 1) // denominator


FREQUENCY_CODES = {
    0x08: 16000,
    0x04: 32000,
    0x02: 44100,
    0x01: 48000,
}

CHANNEL_MODE_CODES = {
    0x08: "mono",
    0x04: "dual_channel",
    0x02: "stereo",
    0x01: "joint_stereo",
}

BLOCK_LENGTH_CODES = {
    0x08: 4,
    0x04: 8,
    0x02: 12,
    0x01: 16,
}

SUBBAND_CODES = {
    0x02: 4,
    0x01: 8,
}

ALLOCATION_CODES = {
    0x02: "snr",
    0x01: "loudness",
}


@dataclass
class SBCConfiguration:
    """Decoded SBC configuration blob from BlueZ MediaTransport."""

    sample_rate: Optional[int]
    channel_mode: Optional[str]
    block_length: Optional[int]
    subbands: Optional[int]
    allocation: Optional[str]
    min_bitpool: Optional[int]
    max_bitpool: Optional[int]
    transport_path: Optional[str]
    raw_bytes: tuple[int, ...]

    @property
    def effective_bitpool(self) -> Optional[int]:
        """Return the negotiated bitpool value we should use for bitrate estimates."""
        if self.max_bitpool is not None:
            return self.max_bitpool
        return self.min_bitpool


def parse_sbc_configuration(raw_bytes: Iterable[int], transport_path: Optional[str] = None) -> Optional[SBCConfiguration]:
    """
    Convert the raw bytes from org.bluez.MediaTransport1.Configuration into structured fields.
    The configuration is defined in the A2DP spec (Section 4.3.2.5, SBC codec).
    """
    raw = tuple(int(b) & 0xFF for b in raw_bytes)
    if len(raw) < 4:
        return None

    first, second = raw[0], raw[1]
    min_bitpool = raw[2]
    max_bitpool = raw[3]

    sample_rate = None
    for code in ((first >> 4) & 0x0F, first & 0x0F):
        sample_rate = FREQUENCY_CODES.get(code)
        if sample_rate:
            break

    channel_mode = None
    for code in (first & 0x0F, (first >> 4) & 0x0F):
        channel_mode = CHANNEL_MODE_CODES.get(code)
        if channel_mode:
            break

    block_length = BLOCK_LENGTH_CODES.get((second >> 4) & 0x0F)
    subbands = SUBBAND_CODES.get((second >> 2) & 0x03)
    allocation = ALLOCATION_CODES.get(second & 0x03)

    return SBCConfiguration(
        sample_rate=sample_rate if isinstance(sample_rate, int) else None,
        channel_mode=channel_mode if isinstance(channel_mode, str) else None,
        block_length=block_length if isinstance(block_length, int) else None,
        subbands=subbands if isinstance(subbands, int) else None,
        allocation=allocation if isinstance(allocation, str) else None,
        min_bitpool=min_bitpool,
        max_bitpool=max_bitpool,
        transport_path=transport_path,
        raw_bytes=raw,
    )


def calculate_sbc_bitrate(
    *,
    bitpool: int,
    sample_rate: int,
    channel_mode: str,
    block_length: int,
    subbands: int,
) -> Optional[int]:
    """
    Calculate the nominal SBC bitrate (bits per second) for the provided parameters.

    The formulas follow the A2DP specification. ``channel_mode`` should be one of:
    ``mono``, ``dual_channel``, ``stereo``, ``joint_stereo``.
    """
    if bitpool <= 0 or sample_rate <= 0 or block_length <= 0 or subbands <= 0:
        return None

    channels = 1 if channel_mode == "mono" else 2

    if channel_mode == "dual_channel":
        payload_bits = block_length * bitpool * channels
    elif channel_mode == "joint_stereo":
        payload_bits = block_length * bitpool - subbands
        if payload_bits <= 0:
            payload_bits = block_length * bitpool
    else:
        payload_bits = block_length * bitpool

    header_bytes = 4
    scale_factor_bytes = (4 * subbands * channels) // 8
    frame_length = header_bytes + scale_factor_bytes + _ceil_div(payload_bits, 8)

    samples_per_frame = block_length * subbands
    numerator = frame_length * 8 * sample_rate
    denominator = samples_per_frame
    bitrate = (numerator + denominator // 2) // denominator
    return int(bitrate)


def sbc_bitrate_from_config(config: SBCConfiguration, bitpool: Optional[int] = None) -> Optional[int]:
    """Convenience wrapper to compute the bitrate directly from a parsed configuration."""
    effective_bitpool = bitpool if bitpool is not None else config.effective_bitpool
    if effective_bitpool is None or config.sample_rate is None or config.channel_mode is None:
        return None

    block_length = config.block_length if config.block_length is not None else 16
    subbands = config.subbands if config.subbands is not None else 8

    return calculate_sbc_bitrate(
        bitpool=effective_bitpool,
        sample_rate=config.sample_rate,
        channel_mode=config.channel_mode,
        block_length=block_length,
        subbands=subbands,
    )


def _parse_busctl_string(output: str) -> Optional[str]:
    """Extract the value from busctl string responses like `s "active"`."""
    text = output.strip()
    if not text:
        return None
    if " " in text:
        _, value = text.split(" ", 1)
    else:
        value = text
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    return value or None


def fetch_sbc_configuration(device_address: str, timeout: float = 2.0) -> Optional[SBCConfiguration]:
    """
    Locate the MediaTransport path for the given device and return the parsed SBC configuration.
    """
    try:
        addr_formatted = device_address.replace(":", "_")
        tree = subprocess.run(
            ["busctl", "--system", "tree", "org.bluez"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if tree.returncode != 0:
            return None

        transport_paths = []
        for line in tree.stdout.splitlines():
            if addr_formatted in line and "/sep" in line and "fd" in line:
                parts = line.strip().split()
                if parts:
                    transport_paths.append(parts[-1])

        if not transport_paths:
            return None

        selected_path: Optional[str] = None
        candidate_states = []
        for path in transport_paths:
            try:
                state_proc = subprocess.run(
                    [
                        "busctl",
                        "--system",
                        "get-property",
                        "org.bluez",
                        path,
                        "org.bluez.MediaTransport1",
                        "State",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                if state_proc.returncode == 0:
                    state = _parse_busctl_string(state_proc.stdout)
                    candidate_states.append((path, state))
                    if state and state.lower() == "active":
                        selected_path = path
                        break
            except subprocess.TimeoutExpired:
                continue
            except FileNotFoundError:
                break

        if not selected_path:
            selected_path = transport_paths[0]

        config = subprocess.run(
            [
                "busctl",
                "--system",
                "get-property",
                "org.bluez",
                selected_path,
                "org.bluez.MediaTransport1",
                "Configuration",
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if config.returncode != 0:
            return None

        tokens = config.stdout.strip().split()
        if len(tokens) < 3 or tokens[0] != "ay":
            return None

        try:
            length = int(tokens[1], 0)
        except ValueError:
            length = len(tokens) - 2

        raw_bytes = []
        for raw in tokens[2:2 + length]:
            try:
                raw_bytes.append(int(raw, 0))
            except ValueError:
                # busctl may emit values like "0x3f"; int(..., 0) already handles this,
                # so hitting this branch means the field is something unexpected.
                pass

        if not raw_bytes:
            return None

        return parse_sbc_configuration(raw_bytes, transport_path=selected_path)

    except FileNotFoundError:
        # busctl is not available in this environment.
        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"Error fetching SBC configuration: {exc}", file=sys.stderr)
        return None


def format_channel_mode(mode: Optional[str]) -> Optional[str]:
    """Human-readable label for an SBC channel mode identifier."""
    if not mode:
        return None
    mapping = {
        "mono": "Mono",
        "dual_channel": "Dual Channel",
        "stereo": "Stereo",
        "joint_stereo": "Joint Stereo",
    }
    return mapping.get(mode, mode.replace("_", " ").title())


def format_bitrate(bps: Optional[int]) -> str:
    """Format bits-per-second as a human-friendly kbps string."""
    if bps is None:
        return "Unknown kbps"
    return f"{bps / 1000:.1f} kbps"
