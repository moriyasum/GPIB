import pyvisa
import time

# Open the VISA Resource Manager
rm = pyvisa.ResourceManager()

# Open the HP 34401A
dmm = rm.open_resource("GPIB0::13::INSTR")
dmm.timeout = 5000

# Read instrument identification
print("Instrument:")
print(dmm.query("*IDN?").strip())

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
