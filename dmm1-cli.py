import pyvisa
import time

# GPIB address, Interface number
adr = "13"
interface = "GPIB0"

# Open VISA
rm = pyvisa.ResourceManager()
dmm = rm.open_resource(f"{interface}::{adr}::INSTR")
dmm.timeout = 5000

# Read instrument ID
print("Interface: ", interface, ", GPIB address: ", adr)
print("Instrument ID: ", dmm.query("*IDN?").strip())

for i in range(5):   # set number of loop
    # Configure the DMM for DC voltage measurement
    dmm.write("CONF:VOLT:DC")

    # Take a measurement
    value = dmm.query("READ?")
    print(i, "DC Voltage =", value.strip(), "V")

    time.sleep(2)

# Close the instrument
dmm.close()
rm.close()
