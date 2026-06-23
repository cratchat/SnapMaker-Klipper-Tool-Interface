#!/usr/bin/env python3

import argparse
from gp8403 import GP8403, OUTPUT_RANGE_5V, OUTPUT_RANGE_10V, CHANNEL_0

def main():
    parser = argparse.ArgumentParser(description="Set GP8403 DAC output voltage")
    parser.add_argument("voltage", type=float, help="Output voltage in volts, e.g. 3.5")
    parser.add_argument("--range", choices=["5", "10"], default="5", help="DAC output range")
    parser.add_argument("--bus", type=int, default=1)
    parser.add_argument("--address", type=lambda x: int(x, 0), default=0x58)

    args = parser.parse_args()

    output_range = OUTPUT_RANGE_5V if args.range == "5" else OUTPUT_RANGE_10V
    max_voltage = 5.0 if args.range == "5" else 10.0

    if not 0 <= args.voltage <= max_voltage:
        raise ValueError(f"Voltage must be between 0 and {max_voltage} V")

    voltage_mv = int(round(args.voltage * 1000))

    dac = GP8403(bus=args.bus, address=args.address)
    dac.begin()
    dac.setDACOutRange(output_range)
    dac.setDACOutVoltage(voltage_mv, CHANNEL_0)

    print(f"Set GP8403 CH0 to {args.voltage:.3f} V")

if __name__ == "__main__":
    main()
