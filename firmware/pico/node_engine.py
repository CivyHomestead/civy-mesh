import json
import quorum

class CivyNodeEngine:
    def __init__(self, config_path="config.json"):
        # Load local configuration
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
        self.node_name = self.config.get("node_name", "Civy Node")
        self.packet_buffer = []  # Ring buffer for local packet log
        self.buffer_max = 20
        
        print(f"[{self.node_name}] Engine initialized.")

    def process_incoming_raw(self, raw_bytes: bytes):
        """Decodes raw radio bytes and stores them in the local event ring buffer."""
        try:
            packet = quorum.unpack_payload(raw_bytes)
            
            # Store in ring buffer
            self.packet_buffer.append(packet)
            if len(self.packet_buffer) > self.buffer_max:
                self.packet_buffer.pop(0)  # Drop oldest
                
            print(f"[{self.node_name}] RX Packet from CIVY-{packet['node_id_hex']} (Type: {packet['msg_type']})")
            return packet
        except Exception as e:
            print(f"[{self.node_name}] Packet parse error: {e}")
            return None

    def trigger_button_action(self, press_type="SHORT", node_id_int=0xDFB3796E):
        """Simulates creating an outgoing packet based on physical button interactions."""
        if press_type == "SHORT":
            msg_type = quorum.TYPE_DINER_BELL
            payload_str = b"BELL!!"
        elif press_type == "LONG":
            msg_type = quorum.TYPE_EMERGENCY
            payload_str = b"SOS!!!"
        else:
            msg_type = quorum.TYPE_HEARTBEAT
            payload_str = b"PING!!"

        raw_packet = quorum.pack_payload(
            node_id_int=node_id_int,
            msg_type=msg_type,
            data_bytes=payload_str
        )
        
        print(f"[{self.node_name}] TX Action Generated: {press_type} PRESS ({len(raw_packet)} B)")
        return raw_packet