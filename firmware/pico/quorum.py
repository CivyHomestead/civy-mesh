import struct
import time

# Packet Types
TYPE_HEARTBEAT  = 0x01  # Quorum status ping
TYPE_DINER_BELL = 0x02  # Short-press "poke"
TYPE_EMERGENCY  = 0x03  # 3-second hold SOS

# Binary Layout: [NodeID: 4B][Type: 1B][Timestamp: 4B][Flags: 1B][Data: 6B] = 16 Bytes
PACK_FORMAT = "!IBIB6s"
PACKET_SIZE = struct.calcsize(PACK_FORMAT)

def pack_payload(node_id_int: int, msg_type: int, data_bytes: bytes = b"\x00"*6, flags: int = 0) -> bytes:
    """Packs node state into a fixed 16-byte binary payload for minimum radio airtime."""
    timestamp = int(time.time())
    
    # Ensure data field is exactly 6 bytes
    data_padded = (data_bytes + b"\x00" * 6)[:6]
    
    return struct.pack(
        PACK_FORMAT,
        node_id_int,
        msg_type,
        timestamp,
        flags,
        data_padded
    )

def unpack_payload(raw_bytes: bytes) -> dict:
    """Unpacks a 16-byte raw radio frame back into a structured dictionary."""
    if len(raw_bytes) != PACKET_SIZE:
        raise ValueError(f"Invalid packet length: expected {PACKET_SIZE} bytes, got {len(raw_bytes)}")
        
    node_id, msg_type, timestamp, flags, data = struct.unpack(PACK_FORMAT, raw_bytes)
    
    return {
        "node_id_hex": f"{node_id:08X}",
        "msg_type": msg_type,
        "timestamp": timestamp,
        "flags": flags,
        "data_raw": data
    }