import signal
import sys
import time
from datetime import datetime

import customtkinter as ctk
import keyboard
from obswebsocket import obsws, requests

# Initialize OBS WebSocket client (will be updated with user input)
client = None
status_label = None
current_keybind = 'ctrl+`'


def connect_client(host, port, password):
    global client
    client = obsws(host, port, password)
    try:
        client.connect()
        version = client.call(requests.GetVersion())
        log_message(
            f"Connected to OBS WebSocket.\nOBS Version: {version.getobsVersion()}\n"
            f"Running on {version.getplatformDescription()}")
        # enable_replay_buffer()  #enable replay on connect
        update_toggle_button()
        update_toggle_record()
    except Exception as e:
        log_message(f"Connection error: {e}")


def enable_replay_buffer():
    try:
        client.call(requests.StartReplayBuffer())
        log_message("Replay Buffer started automatically.")
        update_replay_buffer_status()
    except Exception as e:
        log_message(f"Error enabling replay buffer: {e}")


def stop_replay_buffer():
    client.call(requests.StopReplayBuffer())


def save_replay_buffer():
    try:
        client.call(requests.SaveReplayBuffer())
        time.sleep(2.5)
        last_replay = client.call(requests.GetLastReplayBufferReplay()).getsavedReplayPath()
        log_message(f"Replay saved: '{last_replay}'")
    except Exception as e:
        log_message(f"Error saving replay buffer: {e}")


def update_replay_buffer_status():
    try:
        response = client.call(requests.GetReplayBufferStatus()).getoutputActive()
        if response:
            status_color = "#77DD76"
            status_message = "Replay Buffer is ACTIVE"
        else:
            status_color = "#FF6962"
            status_message = "Replay Buffer is INACTIVE"

        status_label.configure(text=status_message, text_color=status_color)
        root.after(1500, update_replay_buffer_status)
    except Exception as e:
        log_message(f"Error getting replay buffer status: {e}")


def on_save_press():
    save_replay_buffer()


def update_toggle_button():
    global toggle_button
    try:
        response = client.call(requests.GetReplayBufferStatus()).getoutputActive()
        # Change text and color based on replay buffer status
        if response:
            toggle_button.configure(text="Stop Replay Buffer", fg_color="#9B4747", corner_radius=16,
                                    hover_color="#BF5757")  # Active (red color)
        else:
            toggle_button.configure(text="Start Replay Buffer", fg_color="#49A051", corner_radius=16,
                                    hover_color="#59BF60")  # Inactive (green color)

        root.after(1500, update_toggle_button)
    except Exception as e:
        log_message(f"Error updating toggle button: {e}")


def update_toggle_record():
    global record_button
    try:
        response = client.call(requests.GetRecordStatus()).getoutputActive()
        # Change text and color based on replay buffer status
        if response:
            record_button.configure(text="Stop Recording", fg_color="#9B4747", corner_radius=16,
                                    hover_color="#BF5757")  # Active (red color)
        else:
            record_button.configure(text="Start Recording", fg_color="#49A051", corner_radius=16,
                                    hover_color="#59BF60")  # Inactive (green color)

        root.after(1500, update_toggle_record)
    except Exception as e:
        log_message(f"Error updating toggle button: {e}")


def toggle_replay_buffer():
    global toggle_button
    try:
        response = client.call(requests.ToggleReplayBuffer()).getoutputActive()

        # Log message based on the status
        log_message("Replay Buffer started." if response else "Replay Buffer stopped.")

        # Start the thread to update the status
        update_replay_buffer_status()
    except Exception as e:
        log_message(f"Error toggling replay buffer: {e}")


def toggle_record():
    global record_button
    try:
        response = client.call(requests.ToggleRecord()).getoutputActive()

        log_message("Recording Started." if response else "Recording stopped.")

        update_toggle_record()

    except Exception as e:
        log_message(f"Error Toggling Recording: {e}")


def listen_for_keystrokes():
    keyboard.add_hotkey(current_keybind, on_save_press)


def handle_interrupt():
    stop_replay_buffer()
    if client:
        client.disconnect()
    sys.exit(0)


def log_message(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text.insert(ctk.END, f"[{current_time}] {message}\n")
    log_text.see(ctk.END)


def update_keybind():
    global current_keybind
    new_keybind = keybind_entry.get()
    if new_keybind != current_keybind:
        keyboard.remove_hotkey(current_keybind)
        keyboard.add_hotkey(new_keybind, on_save_press)
        log_message(f"Keybind updated from '{current_keybind}' to: '{new_keybind}'")
        current_keybind = new_keybind


def on_close():
    root.destroy()
    stop_replay_buffer()
    if client:
        client.disconnect()
    sys.exit(0)


def create_gui():
    """Creates the main GUI window."""
    global root, log_text, status_label, keybind_entry, toggle_button, record_button
    root = ctk.CTk()
    ctk.set_appearance_mode("dark")
    # root.geometry("600x560") ### The gui is not responsive at all, like literally
    root.title("OBS Replay Buffer Control")
    root.protocol("WM_DELETE_WINDOW", on_close)
    light_fg = "#FFFFFF"

    # Create frames for layout
    top_frame = ctk.CTkFrame(root, fg_color="transparent")
    top_frame.pack(padx=15, pady=15, fill="x")

    # Connection Info Frame (Top Left)
    connection_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
    connection_frame.pack(side=ctk.LEFT, padx=(0, 20), fill="y")  # Padding on right side

    ctk.CTkLabel(connection_frame, text="Host:", text_color=light_fg).grid(row=0, column=0, padx=(0, 10))
    host_entry = ctk.CTkEntry(connection_frame)
    host_entry.grid(row=0, column=1, padx=(5, 10), pady=5, sticky="ew")

    ctk.CTkLabel(connection_frame, text="Port:", text_color=light_fg).grid(row=1, column=0, padx=(0, 10))
    port_entry = ctk.CTkEntry(connection_frame, placeholder_text="4455")
    port_entry.insert(0, "4455")
    port_entry.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="ew")

    ctk.CTkLabel(connection_frame, text="Password:", text_color=light_fg).grid(row=2, column=0, padx=(0, 10))
    password_entry = ctk.CTkEntry(connection_frame, show='*')
    password_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="ew")

    connect_button = ctk.CTkButton(connection_frame, fg_color="#488D9E", hover_color="#57ACBF", corner_radius=16,
                                   text="Connect", command=lambda: connect_client(
            host_entry.get(), int(port_entry.get()), password_entry.get()))
    connect_button.grid(row=3, columnspan=2, pady=10)

    # Keybind Frame (Top Right)
    keybind_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
    keybind_frame.pack(side=ctk.RIGHT, fill="y")  # Stick to the right side

    ctk.CTkLabel(keybind_frame, text="Save Replay Keybind", text_color=light_fg).pack(pady=(8, 0))

    keybind_entry = ctk.CTkEntry(keybind_frame, fg_color="transparent")
    keybind_entry.insert(0, current_keybind)  # Set default value
    keybind_entry.pack(pady=8)

    update_keybind_button = ctk.CTkButton(keybind_frame, fg_color="#488D9E", hover_color="#57ACBF", corner_radius=16,
                                          text="Update Keybind", command=update_keybind)
    update_keybind_button.pack(pady=12)

    # Replay Buffer Control Frame
    control_frame = ctk.CTkFrame(root, fg_color="transparent")
    control_frame.pack(pady=10, fill="x")  # Fill horizontally for dynamic expansion

    record_button = ctk.CTkButton(
        control_frame,
        fg_color="#49A051",
        hover_color="#59BF60",
        corner_radius=16,
        text="Start Recording",
        command=toggle_record
    )
    record_button.grid(row=0, column=0, padx=15, pady=10, sticky="ew")  # Sticky 'ew' for horizontal expansion

    # Create buttons using grid
    toggle_button = ctk.CTkButton(
        control_frame,
        fg_color="#49A051",
        hover_color="#59BF60",
        corner_radius=16,
        text="Start Replay Buffer",
        command=toggle_replay_buffer
    )
    toggle_button.grid(row=0, column=1, padx=15, pady=10, sticky="ew")  # Sticky 'ew' for horizontal expansion

    save_button = ctk.CTkButton(
        control_frame,
        fg_color="#999246",
        hover_color="#BFB457",
        corner_radius=16,
        text="Save Replay Buffer",
        command=save_replay_buffer
    )
    save_button.grid(row=0, column=2, padx=15, pady=10, sticky="ew")  # Sticky 'ew' for horizontal expansion

    # Log Text Area
    log_text = ctk.CTkTextbox(root, height=200, width=300, state="normal", font=("Source Code Pro", 16))
    log_text.pack(padx=8, pady=10, fill="both", expand=True)  # Dynamically sized

    # Status Label
    status_label = ctk.CTkLabel(root, text="Replay Buffer Status: N/A", text_color=light_fg)
    status_label.pack(pady=10)

    # Start listening for keyboard shortcuts
    listen_for_keystrokes()

    # Run the GUI loop
    root.mainloop()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_interrupt)
    try:
        create_gui()
    except KeyboardInterrupt:
        pass
    finally:
        if client:
            client.disconnect()
