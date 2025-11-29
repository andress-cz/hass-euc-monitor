import asyncio
import struct
import sys
# from bleak import BleakClient, BleakScanner # Moved to main

# Constants
EUC_SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
EUC_CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

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
    crc = 0xffffffff
    for byte in data:
        # Replicating the logic from VeteranDecoder.mc
        # var mask_8 = ~(-1 << 8) << (32 - 8);
        # var crc_shifted_8 = ~mask_8 & ((crc >> 8) | mask_8);
        # crc = crc_shifted_8 ^ crc32Table[(crc & 0xff) ^ rawData[i + offset]];
        
        # In Python:
        # The MonkeyC logical right shift (>>) behaves like Python's >> for positive numbers,
        # but we need to be careful with signed 32-bit integers if we were doing it exactly like MC.
        # However, Python handles arbitrarily large integers.
        # Let's implement standard CRC32 logic but check if it matches the table usage.
        
        # The MC code:
        # crc_shifted_8 = (crc >> 8) & 0x00FFFFFF  (effectively, since mask_8 is 0xFF000000 inverted? No wait)
        # ~(-1 << 8) is 0x000000FF. << 24 is 0xFF000000. ~ of that is 0x00FFFFFF.
        # So mask_8 is 0x00FFFFFF.
        # crc_shifted_8 = 0x00FFFFFF & ((crc >> 8) | 0xFF000000) ... wait, the MC code is weird.
        
        # Let's look at standard CRC32 implementation using a table.
        # Standard: crc = (crc >> 8) ^ table[(crc ^ byte) & 0xFF]
        # The MC code seems to be doing exactly that but with manual bit masking to simulate 32-bit unsigned behavior?
        
        # Let's try the standard approach first, it usually matches.
        
        index = (crc & 0xff) ^ byte
        crc = (crc >> 8) ^ CRC32_TABLE[index]
        
    return crc ^ 0xffffffff

class LynxDecoder:
    def __init__(self):
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
        self.last_packet_time = 0

    def process_data(self, data):
        for byte in data:
            self.check_char(byte)

    def check_char(self, c):
        if self.state == "collecting":
            self.frame.append(c)
            size = len(self.frame)
            
            # Validation checks from frameDecoder.mc were removed as they caused issues with Lynx data.

            if size == self.len + 4:
                self.state = "done"
                # Process frame
                if self.len > 38:
                    # Check CRC
                    payload = self.frame[:-4] # Exclude CRC
                    provided_crc = struct.unpack(">I", self.frame[-4:])[0]
                    calc_crc = calculate_crc32(payload)
                    
                    if calc_crc == provided_crc:
                        self.decode_frame(self.frame)
                    else:
                        print(f"CRC Mismatch: Calc {calc_crc:08x} vs Prov {provided_crc:08x}")
                
                self.reset()
                
        elif self.state == "lensearch":
            self.frame.append(c)
            self.len = c & 0xff
            self.state = "collecting"
            self.old2 = self.old1
            self.old1 = c
            
        else: # unknown
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
        self.old1 = 0
        self.old2 = 0
        self.state = "unknown"
        self.frame = bytearray()

    def decode_frame(self, data):
        # Based on processFrame in VeteranDecoder.mc
        # data includes header
        
        # Voltage: offset 4, int16 big endian, / 100.0
        voltage = struct.unpack(">h", data[4:6])[0] / 100.0
        
        # Speed: offset 6, int16 big endian, abs(), / 10.0
        speed = abs(struct.unpack(">h", data[6:8])[0]) / 10.0
        
        # Trip Distance: offset 8, 4 bytes mixed endian
        trip_dist_raw = (data[10] << 24) | (data[11] << 16) | (data[8] << 8) | (data[9])
        trip_dist = trip_dist_raw / 1000.0
        
        # Total Distance: offset 12, same weird format
        total_dist_raw = (data[14] << 24) | (data[15] << 16) | (data[12] << 8) | (data[13])
        total_dist = total_dist_raw / 1000.0
        
        # Current: offset 16, int16 big endian, / 10.0
        current = struct.unpack(">h", data[16:18])[0] / 10.0
        
        # Temperature: offset 18, 2 bytes
        temp = ((data[18] << 8) | data[19]) / 100.0

        # Auto Off (Sleep Timer): offset 20, int16 big endian
        auto_off = struct.unpack(">h", data[20:22])[0]

        # Charge Mode: offset 22, int16 big endian
        charge_mode = struct.unpack(">h", data[22:24])[0]

        # Speed Alert: offset 24, int16 big endian
        speed_alert = struct.unpack(">h", data[24:26])[0]

        # Speed Tiltback: offset 26, int16 big endian
        speed_tiltback = struct.unpack(">h", data[26:28])[0]
        
        # Version: offset 28, int16 big endian, / 1000.0
        version = 0
        ver_raw = 0
        if len(data) >= 30:
            ver_raw = struct.unpack(">h", data[28:30])[0]
            version = ver_raw / 1000.0
        
        # Determine mVer for BMS logic
        mVer = ver_raw // 1000 if ver_raw > 0 else 0

        # Ride Mode (Pedals Mode): offset 30, int16 big endian
        # The Android app sends 0/1/2 to SET mode but doesn't use the read value for display
        # Show the raw value from the wheel
        ride_mode_raw = 0
        if len(data) >= 32:
            ride_mode_raw = struct.unpack(">h", data[30:32])[0]

        # Pitch Angle: offset 32, int16 big endian (signed), / 100.0
        pitch_angle = 0.0
        if len(data) >= 34:
             pitch_angle = struct.unpack(">h", data[32:34])[0] / 100.0
            
        # HPWM: offset 34, int16 big endian, / 100.0
        hpwm = 0
        if len(data) >= 36:
             hpwm = struct.unpack(">h", data[34:36])[0] / 100.0

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
        
        # Generate BMS info for both BMS (display always, not just when packet 3/7 arrives)
        bms_info = ""
        if mVer >= 5:
            num_cells = 36  # Lynx has 36 cells
            
            # BMS 1
            valid_cells_1 = [c for c in self.bms1_cells[:num_cells] if c > 0.0]
            if valid_cells_1:
                min_cell_1 = min(valid_cells_1)
                max_cell_1 = max(valid_cells_1)
                avg_cell_1 = sum(valid_cells_1) / len(valid_cells_1)
                bms_voltage_1 = sum(valid_cells_1)
                bms_info += f"\n--- BMS 1 ---\n"
                bms_info += f"Voltage: {bms_voltage_1:.2f} V | "
                bms_info += f"Min: {min_cell_1:.3f} V | "
                bms_info += f"Max: {max_cell_1:.3f} V | "
                bms_info += f"Avg: {avg_cell_1:.3f} V | "
                bms_info += f"Delta: {(max_cell_1 - min_cell_1):.3f} V\n"
                bms_info += f"Current: {self.bms1_current:.2f} A | "
                bms_info += f"Temps: {self.bms1_temps[0]:.1f}/{self.bms1_temps[1]:.1f}/{self.bms1_temps[2]:.1f}/{self.bms1_temps[3]:.1f}/{self.bms1_temps[4]:.1f}/{self.bms1_temps[5]:.1f} C\n"
            
            # BMS 2
            valid_cells_2 = [c for c in self.bms2_cells[:num_cells] if c > 0.0]
            if valid_cells_2:
                min_cell_2 = min(valid_cells_2)
                max_cell_2 = max(valid_cells_2)
                avg_cell_2 = sum(valid_cells_2) / len(valid_cells_2)
                bms_voltage_2 = sum(valid_cells_2)
                bms_info += f"\n--- BMS 2 ---\n"
                bms_info += f"Voltage: {bms_voltage_2:.2f} V | "
                bms_info += f"Min: {min_cell_2:.3f} V | "
                bms_info += f"Max: {max_cell_2:.3f} V | "
                bms_info += f"Avg: {avg_cell_2:.3f} V | "
                bms_info += f"Delta: {(max_cell_2 - min_cell_2):.3f} V\n"
                bms_info += f"Current: {self.bms2_current:.2f} A | "
                bms_info += f"Temps: {self.bms2_temps[0]:.1f}/{self.bms2_temps[1]:.1f}/{self.bms2_temps[2]:.1f}/{self.bms2_temps[3]:.1f}/{self.bms2_temps[4]:.1f}/{self.bms2_temps[5]:.1f} C\n"

        print("\033[H\033[J") # Clear screen
        print(f"Voltage: {voltage:.2f} V")
        print(f"Speed: {speed:.1f} km/h")
        print(f"Trip Distance: {trip_dist:.3f} km")
        print(f"Total Distance: {total_dist:.2f} km")
        print(f"Current: {current:.1f} A")
        print(f"Temperature: {temp:.2f} C")
        print(f"HPWM: {hpwm:.2f} %")
        print(f"Version: {version:.3f}")
        print("-" * 40)
        print(f"Ride Mode: {ride_mode_raw}")
        print(f"Pitch Angle: {pitch_angle:.2f} deg")
        print(f"Speed Alert: {speed_alert} km/h")
        print(f"Tiltback Speed: {speed_tiltback} km/h")
        print(f"Auto Off: {auto_off} sec")
        print(f"Charge Mode: {charge_mode}")
        if bms_info:
            print(bms_info)



async def main():
    try:
        from bleak import BleakClient, BleakScanner
    except ImportError:
        print("Error: 'bleak' module not found. Please install it using 'pip install bleak'.")
        return

    print("Scanning for Leaperkim device...")
    device = None
    async with BleakScanner() as scanner:
        async for d, a in scanner.advertisement_data():
            if d.name and "Leaperkim" in d.name: # Adjust if name is different
                print(f"Found {d.name} ({d.address})")
                device = d
                break
            # Also check for service UUID if name is not reliable
            if EUC_SERVICE_UUID in a.service_uuids:
                 print(f"Found device with EUC Service ({d.address})")
                 device = d
                 break
    
    if not device:
        # Try to find by name prefix if exact match failed
        devices = await BleakScanner.discover()
        for d in devices:
             if d.name and d.name.startswith("LK"): # Leaperkim often starts with LK? Or just check known names
                 print(f"Found potential device {d.name} ({d.address})")
                 device = d
                 break
    
    if not device:
        print("No Leaperkim device found.")
        return

    print(f"Connecting to {device.name or device.address}...")
    
    decoder = LynxDecoder()

    def notification_handler(sender, data):
        decoder.process_data(data)

    async with BleakClient(device) as client:
        print("Connected!")
        await client.start_notify(EUC_CHARACTERISTIC_UUID, notification_handler)
        
        # Keep running
        while True:
            await asyncio.sleep(1)


def test_decoder():
    print("Running decoder test...")
    decoder = LynxDecoder()
    
    # Construct a mock frame
    # Header: 220, 90, 92 (DC 5A 5C)
    # Length byte: L (Total length of data including header and length byte)
    # Payload
    # CRC
    
    # Let's create a payload of 40 bytes.
    # Header (3) + Length (1) + Payload (40) = 44 bytes.
    # So Length byte should be 44.
    
    length_byte = 44
    frame_data = bytearray([220, 90, 92, length_byte])
    
    payload = bytearray([0] * 40)
    # Set some values
    # Voltage (offset 4 in frame_data? No, offset 4 in the WHOLE frame including header?)
    # In decode_frame(self, data):
    # voltage = struct.unpack(">h", data[4:6])[0] / 100.0
    # data[0] is 220.
    # So data[4] is the first byte of payload!
    # Yes.
    
    # Voltage: 100.2 V -> 10020 -> 0x2724
    struct.pack_into(">h", payload, 0, 10020) # Payload index 0 is frame index 4
    # Speed: 25.5 km/h -> 255 -> 0x00FF
    struct.pack_into(">h", payload, 2, 255)   # Payload index 2 is frame index 6
    
    # Trip Distance: 12.345 km -> 12345
    # Frame index 8, 9, 10, 11 -> Payload index 4, 5, 6, 7
    # Logic: (data[10] << 24) | (data[11] << 16) | (data[8] << 8) | (data[9])
    # We want this to equal 12345 (0x00003039)
    # So data[10]=00, data[11]=00, data[8]=30, data[9]=39
    # Payload index 6=00, 7=00, 4=30, 5=39
    payload[6] = 0x00
    payload[7] = 0x00
    payload[4] = 0x30
    payload[5] = 0x39
    
    # Version: offset 28. Let's set it to 4.005 (4005 -> 0x0FA5)
    # Payload index 28-4 = 24.
    struct.pack_into(">h", payload, 24, 4005)

    # Auto Off: offset 20 -> payload index 16. Set to 300.
    struct.pack_into(">h", payload, 16, 300)
    
    # Charge Mode: offset 22 -> payload index 18. Set to 1.
    struct.pack_into(">h", payload, 18, 1)
    
    # Speed Alert: offset 24 -> payload index 20. Set to 50.
    struct.pack_into(">h", payload, 20, 50)
    
    # Speed Tiltback: offset 26 -> payload index 22. Set to 60.
    struct.pack_into(">h", payload, 22, 60)
    
    # Ride Mode: offset 30 -> payload index 26. Set to 2 (Soft).
    struct.pack_into(">h", payload, 26, 2)
    
    # Pitch Angle: offset 32 -> payload index 28. Set to -500 (-5.00 deg).
    struct.pack_into(">h", payload, 28, -500)
    
    frame_data.extend(payload)
    
    # Calculate CRC on frame_data (0 to len-1)
    crc = calculate_crc32(frame_data)
    print(f"Calculated CRC: {crc:08x}")
    
    # Append CRC
    full_frame = frame_data + struct.pack(">I", crc)
    
    print(f"Feeding frame: {full_frame.hex()}")
    decoder.process_data(full_frame)
    print("Test complete.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run decoder test")
    args = parser.parse_args()

    if args.test:
        test_decoder()
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print(f"Error: {e}")
