import smbus2
import time

try:
    import RPi.GPIO as GPIO
    _GPIO_OK = True
except ImportError:
    _GPIO_OK = False

# Registers
_RANGE_REG  = 0x01
_DAC_REG    = 0x02

# Store-to-EEPROM timing constants (from DFRobot_GP8403.cpp)
_HEAD  = 0x02
_ADDR  = 0x10
_CMD1  = 0x03
_CMD2  = 0x00
_DELAY = 0.010      # 10 ms  (GP8302_STORE_TIMING_DELAY)
_TB    = 1e-6       # I2C_CYCLE_BEFORE
_TA    = 2e-6       # I2C_CYCLE_AFTER
_TT    = 5e-6       # I2C_CYCLE_TOTAL

# Public constants
OUTPUT_RANGE_5V  = 0x00
OUTPUT_RANGE_10V = 0x11
CHANNEL_0        = 0
CHANNEL_1        = 1
CHANNEL_BOTH     = 2


class GP8403:
    """
    2-channel 12-bit I2C DAC driver for GP8403.
    Default: bus=1, address=0x58, SDA=GPIO2, SCL=GPIO3 (BCM).
    """

    def __init__(self, bus=1, address=0x58, sda=2, scl=3):
        self._bus_id = bus
        self.address = address
        self._sda    = sda
        self._scl    = scl
        self._bus    = smbus2.SMBus(bus)
        self._max_mv = 5000

    # ------------------------------------------------------------------ public

    def begin(self):
        """Return True if the device ACKs on the bus."""
        try:
            self._bus.read_byte(self.address)
            return True
        except OSError:
            return False

    def setDACOutRange(self, output_range):
        """Set output range: OUTPUT_RANGE_5V or OUTPUT_RANGE_10V."""
        self._max_mv = 5000 if output_range == OUTPUT_RANGE_5V else 10000
        self._bus.write_byte_data(self.address, _RANGE_REG, output_range)

    def setDACOutVoltage(self, voltage_mv, channel):
        """
        Set output voltage in millivolts on the given channel (0, 1, or CHANNEL_BOTH).
        Input is in mV, clamped to [0, max_range].
        Usage: dac.setDACOutVoltage(voltage_in_uV / 1000, 0)
        """
        v   = max(0.0, min(float(voltage_mv), float(self._max_mv)))
        raw = int(v / self._max_mv * 4095) << 4    # 12-bit left-shifted 4
        lo  = raw & 0xFF
        hi  = (raw >> 8) & 0xFF

        if channel == CHANNEL_0:
            self._bus.write_i2c_block_data(self.address, _DAC_REG, [lo, hi])
        elif channel == CHANNEL_1:
            self._bus.write_i2c_block_data(self.address, _DAC_REG << 1, [lo, hi])
        elif channel == CHANNEL_BOTH:
            self._bus.write_i2c_block_data(self.address, _DAC_REG, [lo, hi, lo, hi])

    def store(self):
        """
        Save current DAC output values to on-chip EEPROM.
        Uses bit-banged I2C to satisfy the GP8403 unlock timing sequence
        (mirrors DFRobot_GP8403.cpp store()).
        Requires RPi.GPIO (provided by rpi-lgpio on Pi 4/5).
        """
        if not _GPIO_OK:
            raise RuntimeError("RPi.GPIO not available; cannot write to EEPROM")

        self._bus.close()

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self._scl, GPIO.OUT)
        GPIO.setup(self._sda, GPIO.OUT)
        GPIO.output(self._scl, GPIO.HIGH)
        GPIO.output(self._sda, GPIO.HIGH)

        # Unlock sequence — see DFRobot_GP8403.cpp store()
        self._start(); self._tx(_HEAD, bits=3, flag=False); self._stop()
        self._start(); self._tx(_ADDR); self._tx(_CMD1); self._stop()

        self._start()
        self._tx(self.address << 1, ack=1)
        for _ in range(8):
            self._tx(_CMD2, ack=1)
        self._stop()

        time.sleep(_DELAY)

        self._start(); self._tx(_HEAD, bits=3, flag=False); self._stop()
        self._start(); self._tx(_ADDR); self._tx(_CMD2); self._stop()

        GPIO.cleanup([self._sda, self._scl])
        self._bus = smbus2.SMBus(self._bus_id)

    def close(self):
        self._bus.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    # --------------------------------------------------------- bit-bang helpers

    def _start(self):
        GPIO.output(self._scl, GPIO.HIGH)
        GPIO.output(self._sda, GPIO.HIGH)
        time.sleep(_TB)
        GPIO.output(self._sda, GPIO.LOW)
        time.sleep(_TA)
        GPIO.output(self._scl, GPIO.LOW)
        time.sleep(_TT)

    def _stop(self):
        GPIO.output(self._sda, GPIO.LOW)
        time.sleep(_TB)
        GPIO.output(self._scl, GPIO.HIGH)
        time.sleep(_TT)
        GPIO.output(self._sda, GPIO.HIGH)
        time.sleep(_TT)

    def _tx(self, data, ack=1, bits=8, flag=True):
        """Send `bits` MSBs of `data`; optionally clock in ACK bit."""
        for i in range(bits - 1, -1, -1):
            GPIO.output(self._sda, GPIO.HIGH if (data & (1 << i)) else GPIO.LOW)
            time.sleep(_TB)
            GPIO.output(self._scl, GPIO.HIGH)
            time.sleep(_TT)
            GPIO.output(self._scl, GPIO.LOW)
            time.sleep(_TA)
        if flag:
            return self._rx_ack()
        else:
            GPIO.output(self._sda, GPIO.LOW)
            GPIO.output(self._scl, GPIO.HIGH)
            return 0

    def _rx_ack(self):
        GPIO.setup(self._sda, GPIO.IN)
        time.sleep(_TB)
        GPIO.output(self._scl, GPIO.HIGH)
        time.sleep(_TT)
        bit = GPIO.input(self._sda)
        GPIO.output(self._scl, GPIO.LOW)
        time.sleep(_TA)
        GPIO.setup(self._sda, GPIO.OUT)
        return bit


# ------------------------------------------------------------------ quick test
if __name__ == "__main__":
    dac = GP8403(bus=1, address=0x58)
    if not dac.begin():
        print("GP8403 not found on I2C bus 1 @ 0x58")
        raise SystemExit(1)

    dac.setDACOutRange(OUTPUT_RANGE_5V)
    print("Range  : 5 V")

    for mv in [0, 1000, 2500, 5000]:
        dac.setDACOutVoltage(mv, CHANNEL_0)
        print(f"CH0 -> {mv} mV")
        time.sleep(0.5)

    dac.store()
    print("Stored to EEPROM")
    dac.close()
