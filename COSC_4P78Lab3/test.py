import serial
import tkinter as tk

#ssc32 = serial.Serial('/dev/ttyS0', 115200)
ssc32 = serial.Serial('COM4', 115200)
step_size=50
# grip
grip_out = 1000
grip_in = 1400
grip = grip_in

# Define row, col positions
r1c2 = {
    "base": 1500,
    "shoulder": 1700,
    "elbow": 1700,
    "wrist": 1300,
    "rotate": 1400,
    "grip": grip
}
r2c2 = {
    "base": 1500,
    "shoulder": 1450,
    "elbow": 1450,
    "wrist": 1300,
    "rotate": 1400,
    "grip": grip
}
r3c2 = {
    "base": 1500,
    "shoulder": 1200,
    "elbow": 1200,
    "wrist": 1300,
    "rotate": 1400,
    "grip": grip
}

# Define default values
defaults = {
    "base": 1500,
    "shoulder": 2150,
    "elbow": 2150,
    "wrist": 1300,
    "rotate": 1400,
    "grip": 1000
}
fields = {
    "base": "#0 P",
    "shoulder": "#1 P",
    "elbow": "#2 P",
    "wrist": "#3 P",
    "rotate": "#4 P",
    "grip": "#5 P"
}

def increment(entry):
    value = int(entry.get())
    entry.delete(0, tk.END)
    entry.insert(0, str(value + step_size))
    display()

def decrement(entry):
    value = int(entry.get())
    entry.delete(0, tk.END)
    entry.insert(0, str(value - step_size))
    display()

def display_output(output_field, text):
    output_field.delete(0, tk.END)
    output_field.insert(0, text)

def display():
    values = [f"{fields[label]}{entry.get()}" for label, entry in entries.items()]
    display_output(output_field, " ".join(values)+" T1000")

def send():
    ssc32.write( (output_field.get()+"\r").encode() )

def home():
    for label,entry in entries.items():
        entry.delete(0,tk.END)
        entry.insert(0,str(defaults[label]))
    display()
    send()

# Create the main window
root = tk.Tk()
root.title("Numeric Input GUI")

entries = {}

# Create the home button
home_button = tk.Button(root, text="Home", command=lambda: home())
home_button.pack(pady=5)

# Create the input fields with + and - buttons
for label, default_value in defaults.items():
    frame = tk.Frame(root)
    frame.pack(pady=2, anchor="w")

    label_widget = tk.Label(frame, text=label.capitalize() + ":", width=10, anchor="w")
    label_widget.pack(side=tk.LEFT, padx=5)

    minus_button = tk.Button(frame, text="-", width=3, command=lambda l=label: decrement(entries[l]))
    minus_button.pack(side=tk.LEFT)

    entry = tk.Entry(frame, width=5, justify=tk.CENTER)
    entry.insert(0, str(default_value))
    entry.pack(side=tk.LEFT, padx=5)
    entries[label] = entry

    plus_button = tk.Button(frame, text="+", width=3, command=lambda l=label: increment(entries[l]))
    plus_button.pack(side=tk.LEFT)

# Create the read button
read_button = tk.Button(root, text="Read", command=lambda: read())
read_button.pack(pady=5)

# Create the send button
send_button = tk.Button(root, text="Send to Arm", command=lambda: send())
send_button.pack(pady=10)

# Create the output field
output_field = tk.Entry(root, width=60, justify=tk.LEFT)
output_field.pack(pady=10)

display()

# Run the main loop
root.mainloop()