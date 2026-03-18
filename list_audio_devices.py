import sounddevice as sd

print("\n--- Available Audio Input Devices ---")
devices = sd.query_devices()
for i, d in enumerate(devices):
    if d['max_input_channels'] > 0:
        print(f"ID: {i}, Name: {d['name']}, Sample Rate: {d['default_samplerate']}")
print("\nDefault Input Device:", sd.default.device[0])
