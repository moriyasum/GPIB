import pyvisa
import time

# GPIB addresses, Interface number
adr1 = "11"
adr2 = "12"
adr3 = "13"
interface = "GPIB0"

# Open VISA
rm = pyvisa.ResourceManager()
dmm1 = rm.open_resource(f"{interface}::{adr1}::INSTR")
dmm1.timeout = 5000
dmm2 = rm.open_resource(f"{interface}::{adr2}::INSTR")
dmm2.timeout = 5000
dmm3 = rm.open_resource(f"{interface}::{adr3}::INSTR")
dmm3.timeout = 5000

print(f"Interface:{interface}")
# Read instrument ID
print(f"Instrument 1: Addr={adr1} ", dmm1.query("*IDN?").strip())
print(f"Instrument 2: Addr={adr2} ", dmm2.query("*IDN?").strip())
print(f"Instrument 3: Addr={adr3} ", dmm3.query("*IDN?").strip())

# Set to Configure DC-V measurement mode
dmm1.write("CONF:VOLT:DC")
dmm2.write("CONF:VOLT:DC")
dmm3.write("CONF:VOLT:DC")
    
for i in range(10):   # Set how many sampling times
    # Send READ command and print out the value
    value = dmm1.query("READ?")
    print(i, "DC Volt:", adr1+ "=", value.strip(), "V, ", end="")

    value = dmm2.query("READ?")
    print(adr2+ "=", value.strip(), "V, ", end="")

    value = dmm3.query("READ?")
    print(adr3+ "=", value.strip(), "V")
    
    time.sleep(0.5)

# Close the instrument
dmm1.close()
dmm2.close()
dmm3.close()
rm.close()
