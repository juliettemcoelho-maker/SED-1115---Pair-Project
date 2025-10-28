from machine import Pin, PWM, ADC
import time

# Set up PWM on Pin 0 (adjust to your wiring)
pwm_pin = Pin(0)
pwm = PWM(pwm_pin)
pwm.freq(1000)              # Frequency: 1000 Hz – works well with RC filter

# Set duty cycle (e.g., 50% duty is 32768 out of 65535)
duty = 32768
pwm.duty_u16(duty)          # Change this value to set the intensity (try 10000, 40000, etc.)

# Let the RC filter output stabilize
time.sleep(0.1)

# Set up ADC on Pin 26 (ADC0 on Pico)
adc = ADC(Pin(26))          # Make sure your RC filter output is wired here

while True:
    raw = adc.read_u16()                   # Reads value from 0 to 65535 (16-bit)
    voltage = (raw / 65535) * 3.3          # Converts to voltage (3.3V Pico max)
    print('PWM Duty:', duty, 'ADC Value:', raw, 'Voltage:', round(voltage, 2), 'V')
    time.sleep(0.5)
