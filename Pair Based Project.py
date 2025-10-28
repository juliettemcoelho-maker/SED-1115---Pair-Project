from machine import Pin, PWM, UART
from time import sleep

# Set up PWM output 
pwm_pin = machine.Pin(16)
pwm = machine.PWM(pwm_pin)
pwm.freq(1000)  # Set PWM frequency to 1 kHz

uart = machine.UART(0, 115200, tx=machine.Pin(8), rx=machine.Pin(9))
uart.init(115200, bits=8, parity=None, stop=1)

# Converts duty cycle percentage to a 16-bit
def duty_percent_to_u16(pct):
    if pct < 0: 
        pct = 0
    if pct > 100: 
        pct = 100
    return int(pct * 65535 // 100)

# Sends a "SET" message with the chosen duty cycle to Pico B
def send_set(duty):
    msg = "SET:{}\n".format(int(duty))
    uart.write(msg)

# Waits to receive text from Pico B or times out
def recv_line(timeout_ms=500):
    start = time.ticks_ms()
    buf = b""
    while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
        if uart.any():
            b = uart.read(1)
            if not b:
                continue
            buf += b
            if b == b'\n':  # message ends when a newline is found
                return buf.decode().strip()
        time.sleep_ms(10)
    return None  # no message received in time

# Cycles through duty cycles and compares results
print("Starting PWM sender. Frequency 1000 Hz")

try:
    while True:
        # Test these PWM duty cycles
        for duty in [10, 25, 50, 75, 90]:
            pwm.duty_u16(duty_percent_to_u16(duty))
            print("Set duty:", duty, "%")

            # Send target duty cycle to Pico B
            send_set(duty)

            reply = None
            start_time = time.time()

            # Wait 3 seconds for a measurement reply
            while time.time() - start_time < 3:
                line = recv_line(timeout_ms=500)
                if line and line.startswith("MEAS:"):
                    reply = line
                    break
                time.sleep(0.05)

            # If reply was received -> show the results
            if reply:
                try:
                    parts = reply.split(',')
                    meas_part = parts[0].split(':')[1]
                    volt_part = parts[1].split(':')[1]
                    meas_pct = float(meas_part)
                    meas_v = float(volt_part)
                    diff = duty - meas_pct
                    print("Measured: {:.2f}% | {:.3f} V | Difference: {:+.2f}%".format(
                        meas_pct, meas_v, diff))
                except Exception as e:
                    print("Error reading reply:", reply, "Error:", e)
            else:
                print("No reply from Pico B for duty", duty, "%")

            time.sleep(0.5)  # short delay before next test
except KeyboardInterrupt:
    pwm.deinit()
    print("Program stopped.")

