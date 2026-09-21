import tkinter as tk
import pyvisa

# GPIB address, Interface number
adr = "13"
interface = "GPIB0"

# Open VISA
rm = pyvisa.ResourceManager()
dmm = rm.open_resource(f"{interface}::{adr}::INSTR")
dmm.timeout = 5000

# Read instrument ID
idn = dmm.query("*IDN?").strip()
# Set to Configure DC-V measurement mode
dmm.write("CONF:VOLT:DC")

# GUI
root = tk.Tk()
root.title("HP 34401A DC Voltage Monitor")
root.geometry("500x250")

running = False

voltage_text = tk.StringVar(value="-------- V")
status_text = tk.StringVar(value="STOPPED")


def measure():
    if not running:
        return

    try:
        voltage = float(dmm.query("READ?"))
        voltage_text.set(f"{voltage:.8f} V")
        status_text.set("RUNNING")
    except Exception as e:
        status_text.set("ERROR: " + str(e))

    if running:
        root.after(500, measure)


def start():
    global running

    if not running:
        running = True
        measure()


def stop():
    global running

    running = False
    status_text.set("STOPPED")


def close():
    dmm.close()
    rm.close()
    root.destroy()


tk.Label(
    root,
    text=idn,
    font=("Arial", 11)
).pack(pady=15)

tk.Label(
    root,
    text=f"Interface:{interface}   GPIB Address:{adr}",
    font=("Arial", 12)
).pack()

tk.Label(
    root,
    textvariable=voltage_text,
    font=("Courier", 28, "bold")
).pack(pady=15)

tk.Label(
    root,
    textvariable=status_text
).pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=15)

tk.Button(
    button_frame,
    text="START",
    command=start,
    width=10
).pack(side="left", padx=5)

tk.Button(
    button_frame,
    text="STOP",
    command=stop,
    width=10
).pack(side="left", padx=5)

tk.Button(
    button_frame,
    text="EXIT",
    command=close,
    width=10
).pack(side="left", padx=5)

root.protocol("WM_DELETE_WINDOW", close)

root.mainloop()
