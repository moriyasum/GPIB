import tkinter as tk
from tkinter import ttk

import pyvisa
# import subprocess # Commented out for Windows compatibility.
import csv
from datetime import datetime
from collections import deque

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# --------------------------------------------------
# GPIB addresses, Interface number
# --------------------------------------------------
adr1 = "11"
adr2 = "12"
adr3 = "13"
interface = "GPIB0"

# --------------------------------------------------
# Open VISA
# --------------------------------------------------
rm = pyvisa.ResourceManager()

dmm1 = rm.open_resource(
    f"{interface}::{adr1}::INSTR"
)

dmm2 = rm.open_resource(
    f"{interface}::{adr2}::INSTR"
)

dmm3 = rm.open_resource(
    f"{interface}::{adr3}::INSTR"
)

dmm1.timeout = 5000
dmm2.timeout = 5000
dmm3.timeout = 5000


# --------------------------------------------------
# Instrument identification
# --------------------------------------------------
id1 = dmm1.query("*IDN?").strip()
id2 = dmm2.query("*IDN?").strip()
id3 = dmm3.query("*IDN?").strip()


# --------------------------------------------------
# Configure DMMs
# --------------------------------------------------
dmm1.write("CONF:VOLT:DC")
dmm2.write("CONF:VOLT:DC")
dmm3.write("CONF:VOLT:DC")


# --------------------------------------------------
# GUI
# --------------------------------------------------
root = tk.Tk()

root.title(
    "HP 34401A - 3 Channel DMM"
)

root.geometry("900x820")


running = False
recording = False
sample_count = 0

csv_file = None
csv_writer = None


# --------------------------------------------------
# Data for graph
# --------------------------------------------------
MAX_POINTS = 100

sample_data = deque(maxlen=MAX_POINTS)

data1 = deque(maxlen=MAX_POINTS)
data2 = deque(maxlen=MAX_POINTS)
data3 = deque(maxlen=MAX_POINTS)


# --------------------------------------------------
# Tk variables
# --------------------------------------------------
adapter_text = tk.StringVar(
    value=f"Interface: {interface}"
)

value1_text = tk.StringVar(
    value="-------- V"
)

value2_text = tk.StringVar(
    value="-------- V"
)

value3_text = tk.StringVar(
    value="-------- V"
)

status_text = tk.StringVar(
    value="STOPPED"
)

count_text = tk.StringVar(
    value="Sample: 0"
)

record_text = tk.StringVar(
    value=""
)


# --------------------------------------------------
# Update graph
# --------------------------------------------------
def update_graph():

    line1.set_data(
        list(sample_data),
        list(data1)
    )

    line2.set_data(
        list(sample_data),
        list(data2)
    )

    line3.set_data(
        list(sample_data),
        list(data3)
    )

    ax.relim()
    ax.autoscale_view()

    canvas.draw_idle()


# --------------------------------------------------
# Measurement
# --------------------------------------------------
def measure():

    global sample_count

    if not running:
        return

    try:

        value1 = float(
            dmm1.query("READ?")
        )

        value2 = float(
            dmm2.query("READ?")
        )

        value3 = float(
            dmm3.query("READ?")
        )


        # ------------------------------
        # Numerical display
        # ------------------------------
        value1_text.set(
            f"{value1: .8f} V"
        )

        value2_text.set(
            f"{value2: .8f} V"
        )

        value3_text.set(
            f"{value3: .8f} V"
        )


        # ------------------------------
        # Sample number
        # ------------------------------
        sample_count += 1

        count_text.set(
            f"Sample: {sample_count}"
        )


        # ------------------------------
        # Store graph data
        # ------------------------------
        sample_data.append(sample_count)

        data1.append(value1)
        data2.append(value2)
        data3.append(value3)


        # ------------------------------
        # CSV recording
        # ------------------------------
        if recording:

            now = datetime.now()

            csv_writer.writerow([
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S.%f")[:-3],
                sample_count,
                value1,
                value2,
                value3
            ])

            csv_file.flush()


        # ------------------------------
        # Update graph
        # ------------------------------
        update_graph()

        status_text.set(
            "RUNNING"
        )


    except Exception as e:

        status_text.set(
            "ERROR: " + str(e)
        )


    if running:

        root.after(
            500,
            measure
        )


# --------------------------------------------------
# START
# --------------------------------------------------
def start_measurement():

    global running

    if not running:
        running = True
        status_text.set(
            "RUNNING"
        )

        measure()


# --------------------------------------------------
# STOP
# --------------------------------------------------
def stop_measurement():

    global running

    running = False

    status_text.set(
        "STOPPED"
    )


# --------------------------------------------------
# RECORD
# --------------------------------------------------
def toggle_recording():

    global recording
    global csv_file
    global csv_writer

    # ----------------------------------------------
    # Start recording
    # ----------------------------------------------
    if not recording:

        now = datetime.now()

        filename = now.strftime(
            "DMM_%Y%m%d_%H%M%S.csv"
        )

        csv_file = open(
            filename,
            "w",
            newline=""
        )

        csv_writer = csv.writer(
            csv_file
        )

        # CSV header
        csv_writer.writerow([
            "Date",
            "Time",
            "Sample",
            f"DMM{adr1} (V)",
            f"DMM{adr2} (V)",
            f"DMM{adr3} (V)"
        ])

        csv_file.flush()

        recording = True


        # RECORD button becomes red
        record_button.config(
            bg="red",
            fg="white",
            activebackground="red",
            activeforeground="white"
        )


        record_text.set(
            "Recording: " + filename
        )


    # ----------------------------------------------
    # Stop recording
    # ----------------------------------------------
    else:

        recording = False

        if csv_file is not None:

            csv_file.close()

            csv_file = None
            csv_writer = None


        # RECORD button returns to normal
        record_button.config(
            bg=default_button_bg,
            fg="black",
            activebackground=default_button_bg,
            activeforeground="black"
        )


        record_text.set(
            ""
        )


# --------------------------------------------------
# CLEAR
# --------------------------------------------------
def clear_graph():

    global sample_count

    sample_count = 0

    sample_data.clear()

    data1.clear()
    data2.clear()
    data3.clear()

    count_text.set(
        "Sample: 0"
    )

    update_graph()


# --------------------------------------------------
# Close
# --------------------------------------------------
def close_program():

    global running
    global recording
    global csv_file

    running = False


    # Close recording file if necessary
    if recording and csv_file is not None:

        csv_file.close()

        csv_file = None

        recording = False


    dmm1.close()
    dmm2.close()
    dmm3.close()

    rm.close()

    root.destroy()


# --------------------------------------------------
# Title
# --------------------------------------------------
ttk.Label(
    root,
    text="HP 34401A  DC Voltage Monitor",
    font=("Arial", 20, "bold")
).pack(pady=10)


# --------------------------------------------------
# Adapter
# --------------------------------------------------
ttk.Label(
    root,
    textvariable=adapter_text,
    font=("Arial", 12, "bold")
).pack()


# --------------------------------------------------
# DMM numerical display
# --------------------------------------------------
frame = ttk.Frame(root)

frame.pack(pady=10)


ttk.Label(
    frame,
    text=f"DMM 1   GPIB Address {adr1}",
    font=("Arial", 12, "bold")
).grid(
    row=0,
    column=0,
    padx=20
)

ttk.Label(
    frame,
    textvariable=value1_text,
    font=("Courier", 20, "bold")
).grid(
    row=1,
    column=0,
    padx=20,
    pady=5
)


ttk.Label(
    frame,
    text=f"DMM 2   GPIB Address {adr2}",
    font=("Arial", 12, "bold")
).grid(
    row=0,
    column=1,
    padx=20
)

ttk.Label(
    frame,
    textvariable=value2_text,
    font=("Courier", 20, "bold")
).grid(
    row=1,
    column=1,
    padx=20,
    pady=5
)


ttk.Label(
    frame,
    text=f"DMM 3   GPIB Address {adr3}",
    font=("Arial", 12, "bold")
).grid(
    row=0,
    column=2,
    padx=20
)

ttk.Label(
    frame,
    textvariable=value3_text,
    font=("Courier", 20, "bold")
).grid(
    row=1,
    column=2,
    padx=20,
    pady=5
)


# --------------------------------------------------
# Status
# --------------------------------------------------
status_frame = ttk.Frame(root)

status_frame.pack(pady=5)


ttk.Label(
    status_frame,
    textvariable=status_text,
    font=("Arial", 12, "bold")
).grid(
    row=0,
    column=0,
    padx=20
)


ttk.Label(
    status_frame,
    textvariable=count_text,
    font=("Arial", 12)
).grid(
    row=0,
    column=1,
    padx=20
)


# --------------------------------------------------
# Recording status
# --------------------------------------------------
tk.Label(
    root,
    textvariable=record_text,
    fg="red",
    font=("Arial", 11, "bold")
).pack(pady=2)


# --------------------------------------------------
# Matplotlib graph
# --------------------------------------------------
figure = Figure(
    figsize=(8, 4),
    dpi=100
)

ax = figure.add_subplot(111)

ax.set_title(
    "DC Voltage"
)

ax.set_xlabel(
    "Sample"
)

ax.set_ylabel(
    "Voltage (V)"
)

ax.grid(True)


line1, = ax.plot(
    [],
    [],
    label=f"GPIB {adr1}"
)

line2, = ax.plot(
    [],
    [],
    label=f"GPIB {adr2}"
)

line3, = ax.plot(
    [],
    [],
    label=f"GPIB {adr3}"
)

ax.legend()


canvas = FigureCanvasTkAgg(
    figure,
    master=root
)

canvas.draw()

canvas.get_tk_widget().pack(
    fill=tk.BOTH,
    expand=True,
    padx=20,
    pady=10
)


# --------------------------------------------------
# Buttons
# --------------------------------------------------
button_frame = ttk.Frame(root)

button_frame.pack(pady=10)


ttk.Button(
    button_frame,
    text="START",
    command=start_measurement,
    width=13
).grid(
    row=0,
    column=0,
    padx=5
)


ttk.Button(
    button_frame,
    text="STOP",
    command=stop_measurement,
    width=13
).grid(
    row=0,
    column=1,
    padx=5
)


# RECORD uses tk.Button because background color
# can be changed easily.
record_button = tk.Button(
    button_frame,
    text="RECORD",
    command=toggle_recording,
    width=12
)

record_button.grid(
    row=0,
    column=2,
    padx=5
)


# Save normal button background color
default_button_bg = record_button.cget(
    "background"
)


ttk.Button(
    button_frame,
    text="CLEAR",
    command=clear_graph,
    width=13
).grid(
    row=0,
    column=3,
    padx=5
)


ttk.Button(
    button_frame,
    text="EXIT",
    command=close_program,
    width=13
).grid(
    row=0,
    column=4,
    padx=5
)


root.protocol(
    "WM_DELETE_WINDOW",
    close_program
)

root.mainloop()
