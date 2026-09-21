# 34401A-1ch.py

import time
import pyvisa

rm = pyvisa.ResourceManager()
instrument_address = "GPIB0::13::INSTR"

try:
    with rm.open_resource(instrument_address) as dmm:
        # Display instrument identification
        print("Connected to:", dmm.query("*IDN?").strip())

        # Measure DC voltage five times
        for i in range(5):
            voltage = dmm.query("MEAS:VOLT:DC?")
            print(f"Measurement {i + 1}: {voltage.strip()} V")
            time.sleep(1)

except Exception as e:
    print(f"ERROR: {e}")

finally:
    rm.close()