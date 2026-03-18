import sounddevice as sd
import sys

def list_devices():
    print(f"Python Version: {sys.version}")
    print("\n--- Available Audio Input Devices ---")
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            print(f"ID: {i}, Name: {d['name']}, Default Sample Rate: {d['default_samplerate']}")
            
    print("\nDefault State:")
    print(f"Input Device ID: {sd.default.device[0]}")
    print(f"Output Device ID: {sd.default.device[1]}")

if __name__ == "__main__":
    list_devices()
