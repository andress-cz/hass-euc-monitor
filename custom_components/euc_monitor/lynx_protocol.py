"""Protocol decoder for Leaperkim Lynx EUC."""
import struct
import logging

_LOGGER = logging.getLogger(__name__)

# CRC32 Table (from VeteranDecoder.mc)
CRC32_TABLE = [
    0x00000000, 0x77073096, 0xee0e612c, 0x990951ba, 0x076dc419, 0x706af48f,
    0xe963a535, 0x9e6495a3, 0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988,
    0x09b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91, 0x1db71064, 0x6ab020f2,
    0xf3b97148, 0x84be41de, 0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7,
    0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec, 0x14015c4f, 0x63066cd9,
    0xfa0f3d63, 0x8d080df5, 0x3b6e20c8, 0x4c69105e, 0xd56041e4, 0xa2677172,
    0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b, 0x35b5a8fa, 0x42b2986c,
    0xdbbbc9d6, 0xacbcf940, 0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59,
    0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116, 0x21b4f4b5, 0x56b3c423,
    0xcfba9599, 0xb8bda50f, 0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924,
    0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d, 0x76dc4190, 0x01db7106,
    0x98d220bc, 0xefd5102a, 0x71b18589, 0x06b6b51f, 0x9fbfe4a5, 0xe8b8d433,
    0x7807c9a2, 0x0f00f934, 0x9609a88e, 0xe10e9818, 0x7f6a0dbb, 0x086d3d2d,
    0x91646c97, 0xe6635c01, 0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e,
    0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457, 0x65b0d9c6, 0x12b7e950,
    0x8bbeb8ea, 0xfcb9887c, 0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xfbd44c65,
    0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2, 0x4adfa541, 0x3dd895d7,
    0xa4d1c46d, 0xd3d6f4fb, 0x4369e96a, 0x346ed9fc, 0xad678846, 0xda60b8d0,
    0x44042d73, 0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9, 0x5005713c, 0x270241aa,
    0xbe0b1010, 0xc90c2086, 0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f,
    0x5edef90e, 0x29d9c998, 0xb0d09822, 0xc7d7a8b4, 0x59b33d17, 0x2eb40d81,
    0xb7bd5c3b, 0xc0ba6cad, 0xedb88320, 0x9abfb3b6, 0x03b6e20c, 0x74b1d29a,
    0xead54739, 0x9dd277af, 0x04db2615, 0x73dc1683, 0xe3630b12, 0x94643b84,
    0x0d6d6a3e, 0x7a6a5aa8, 0xe40ecf0b, 0x9309ff9d, 0x0a00ae27, 0x7d079eb1,
    0xf00f9344, 0x8708a3d2, 0x1e01f268, 0x6906c2fe, 0xf762575d, 0x806567cb,
    0x196c3671, 0x6e6b06e7, 0xfed41b76, 0x89d32be0, 0x10da7a5a, 0x67dd4acc,
    0xf9b9df6f, 0x8ebeeff9, 0x17b7be43, 0x60b08ed5, 0xd6d6a3e8, 0xa1d1937e,
    0x38d8c2c4, 0x4fdff252, 0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b,
    0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60, 0xdf60efc3, 0xa867df55,
    0x316e8eef, 0x4669be79, 0xcb61b38c, 0xbc66831a, 0x256fd2a0, 0x5268e236,
    0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f, 0xc5ba3bbe, 0xb2bd0b28,
    0x2bb45a92, 0x5cb36a04, 0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d,
    0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x026d930a, 0x9c0906a9, 0xeb0e363f,
    0x72076785, 0x05005713, 0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0x0cb61b38,
    0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0x0bdbdf21, 0x86d3d2d4, 0xf1d4e242,
    0x68ddb3f8, 0x1fda836e, 0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777,
    0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c, 0x8f659eff, 0xf862ae69,
    0x616bffd3, 0x166ccf45, 0xa00ae278, 0xd70dd2ee, 0x4e048354, 0x3903b3c2,
    0xa7672661, 0xd06016f7, 0x4969474d, 0x3e6e77db, 0xaed16a4a, 0xd9d65adc,
    0x40df0b66, 0x37d83bf0, 0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 0x30b5ffe9,
    0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6, 0xbad03605, 0xcdd70693,
    0x54de5729, 0x23d967bf, 0xb3667a2e, 0xc4614ab8, 0x5d681b02, 0x2a6f2b94,
    0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2d02ef8d,
]


def calculate_crc32(data):
    """Calculate CRC32 for the given data."""
    crc = 0xffffffff
    for byte in data:
        index = (crc & 0xff) ^ byte
        crc = (crc >> 8) ^ CRC32_TABLE[index]
    return crc ^ 0xffffffff


class LynxDecoder:
    """Decoder for Leaperkim Lynx protocol."""

    def __init__(self):
        """Initialize the decoder."""
        self.frame = bytearray()
        self.state = "unknown"
        self.len = 0
        self.old1 = 0
        self.old2 = 0
        # SmartBMS data storage
        self.bms1_cells = [0.0] * 42  # Support up to 42 cells
        self.bms2_cells = [0.0] * 42
        self.bms1_temps = [0.0] * 6
        self.bms2_temps = [0.0] * 6
        self.bms1_current = 0.0
        self.bms2_current = 0.0
        self.last_data = None

    def process_data(self, data):
        """Process incoming BLE data."""
        for byte in data:
            self.check_char(byte)

    def check_char(self, c):
        """Process a single byte."""
        if self.state == "collecting":
            self.frame.append(c)
            size = len(self.frame)

            if size == self.len + 4:
                self.state = "done"
                # Process frame
                if self.len > 38:
                    # Check CRC
                    payload = self.frame[:-4]  # Exclude CRC
                    provided_crc = struct.unpack(">I", self.frame[-4:])[0]
                    calc_crc = calculate_crc32(payload)

                    if calc_crc == provided_crc:
                        self.decode_frame(self.frame)
                    else:
                        _LOGGER.debug(
                            "CRC Mismatch: Calc %08x vs Prov %08x", calc_crc, provided_crc
                        )

                self.reset()

        elif self.state == "lensearch":
            self.frame.append(c)
            self.len = c & 0xff
            self.state = "collecting"
            self.old2 = self.old1
            self.old1 = c

        else:  # unknown
            # Header sequence: 220, 90, 92 (0xDC, 0x5A, 0x5C)
            if c == 92 and self.old1 == 90 and self.old2 == 220:
                self.frame = bytearray([220, 90, 92])
                self.state = "lensearch"
            elif c == 90 and self.old1 == 220:
                self.old2 = self.old1
            else:
                self.old2 = 0
            self.old1 = c

    def reset(self):
        """Reset decoder state."""
        self.old1 = 0
        self.old2 = 0
        self.state = "unknown"
        self.frame = bytearray()

    def decode_frame(self, data):
        """Decode a complete frame and update last_data."""
        result = {}

        # Voltage: offset 4, int16 big endian, / 100.0
        result["voltage"] = struct.unpack(">h", data[4:6])[0] / 100.0

        # Speed: offset 6, int16 big endian, abs(), / 10.0
        result["speed"] = abs(struct.unpack(">h", data[6:8])[0]) / 10.0

        # Trip Distance: offset 8, 4 bytes mixed endian
        trip_dist_raw = (data[10] << 24) | (data[11] << 16) | (data[8] << 8) | (data[9])
        result["trip_distance"] = trip_dist_raw / 1000.0

        # Total Distance: offset 12, same weird format
        total_dist_raw = (data[14] << 24) | (data[15] << 16) | (data[12] << 8) | (data[13])
        result["total_distance"] = total_dist_raw / 1000.0

        # Current: offset 16, int16 big endian, / 10.0
        result["current"] = struct.unpack(">h", data[16:18])[0] / 10.0

        # Temperature: offset 18, 2 bytes
        result["temperature"] = ((data[18] << 8) | data[19]) / 100.0

        # Auto Off (Sleep Timer): offset 20, int16 big endian
        result["auto_off"] = struct.unpack(">h", data[20:22])[0]

        # Charge Mode: offset 22, int16 big endian
        result["charge_mode"] = struct.unpack(">h", data[22:24])[0]

        # Speed Alert: offset 24, int16 big endian
        result["speed_alert"] = struct.unpack(">h", data[24:26])[0]

        # Speed Tiltback: offset 26, int16 big endian
        result["speed_tiltback"] = struct.unpack(">h", data[26:28])[0]

        # Version: offset 28, int16 big endian, / 1000.0
        ver_raw = 0
        if len(data) >= 30:
            ver_raw = struct.unpack(">h", data[28:30])[0]
            result["version"] = ver_raw / 1000.0

        # Determine mVer for BMS logic
        mVer = ver_raw // 1000 if ver_raw > 0 else 0

        # Ride Mode (Pedals Mode): offset 30, int16 big endian
        if len(data) >= 32:
            result["ride_mode"] = struct.unpack(">h", data[30:32])[0]

        # Pitch Angle: offset 32, int16 big endian (signed), / 100.0
        if len(data) >= 34:
            result["pitch_angle"] = struct.unpack(">h", data[32:34])[0] / 100.0

        # HPWM: offset 34, int16 big endian, / 100.0
        if len(data) >= 36:
            result["hpwm"] = struct.unpack(">h", data[34:36])[0] / 100.0

        # SmartBMS parsing (for Lynx mVer >= 5)
        if mVer >= 5 and len(data) > 46:
            pnum = data[46]
            bmsnum = 1 if pnum < 4 else 2
            cells = self.bms1_cells if bmsnum == 1 else self.bms2_cells
            temps = self.bms1_temps if bmsnum == 1 else self.bms2_temps

            if pnum == 0 or pnum == 4:
                # BMS current data
                if len(data) > 72:
                    self.bms1_current = struct.unpack(">h", data[69:71])[0] / 100.0
                    self.bms2_current = struct.unpack(">h", data[71:73])[0] / 100.0
            elif pnum == 1 or pnum == 5:
                # Cells 0-14
                for i in range(15):
                    if 53 + i * 2 + 1 < len(data):
                        cell = struct.unpack(">h", data[53 + i * 2:55 + i * 2])[0]
                        cells[i] = cell / 1000.0
            elif pnum == 2 or pnum == 6:
                # Cells 15-29
                for i in range(15):
                    if 53 + i * 2 + 1 < len(data):
                        cell = struct.unpack(">H", data[53 + i * 2:55 + i * 2])[0]
                        cells[i + 15] = cell / 1000.0
            elif pnum == 3 or pnum == 7:
                # Cells 30-41 and temperatures
                for i in range(12):
                    offset = 59 + i * 2
                    if offset + 1 < len(data):
                        cell = struct.unpack(">H", data[offset:offset + 2])[0]
                        cells[i + 30] = cell / 1000.0

                if len(data) > 57:
                    temps[0] = struct.unpack(">h", data[47:49])[0] / 100.0
                    temps[1] = struct.unpack(">h", data[49:51])[0] / 100.0
                    temps[2] = struct.unpack(">h", data[51:53])[0] / 100.0
                    temps[3] = struct.unpack(">h", data[53:55])[0] / 100.0
                    temps[4] = struct.unpack(">h", data[55:57])[0] / 100.0
                    temps[5] = struct.unpack(">h", data[57:59])[0] / 100.0

        # Calculate BMS aggregated values
        if mVer >= 5:
            num_cells = 36  # Lynx has 36 cells per BMS

            # BMS 1
            valid_cells_1 = [c for c in self.bms1_cells[:num_cells] if c > 0.0]
            if valid_cells_1:
                result["bms1_voltage"] = sum(valid_cells_1)
                result["bms1_min_cell"] = min(valid_cells_1)
                result["bms1_max_cell"] = max(valid_cells_1)
                result["bms1_avg_cell"] = sum(valid_cells_1) / len(valid_cells_1)
                result["bms1_delta"] = result["bms1_max_cell"] - result["bms1_min_cell"]

            # BMS 2
            valid_cells_2 = [c for c in self.bms2_cells[:num_cells] if c > 0.0]
            if valid_cells_2:
                result["bms2_voltage"] = sum(valid_cells_2)
                result["bms2_min_cell"] = min(valid_cells_2)
                result["bms2_max_cell"] = max(valid_cells_2)
                result["bms2_avg_cell"] = sum(valid_cells_2) / len(valid_cells_2)
                result["bms2_delta"] = result["bms2_max_cell"] - result["bms2_min_cell"]

            # BMS currents
            result["bms1_current"] = self.bms1_current
            result["bms2_current"] = self.bms2_current

            # BMS temperatures
            for i in range(6):
                result[f"bms1_temp{i}"] = self.bms1_temps[i]
                result[f"bms2_temp{i}"] = self.bms2_temps[i]

            # Individual cells
            for i in range(num_cells):
                result[f"bms1_cell{i}"] = self.bms1_cells[i]
                result[f"bms2_cell{i}"] = self.bms2_cells[i]

        self.last_data = result

    def get_data(self):
        """Get the last decoded data."""
        return self.last_data

    def clear_data(self):
        """Clear the last data."""
        self.last_data = None
