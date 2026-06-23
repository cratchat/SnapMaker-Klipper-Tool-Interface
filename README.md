# SnapMaker-Klipper-Tool-Interface

# Snapmaker Klipper

# Overview

# Configuration file (.cfg)
This section provides the Klipper configuration file for the modified Snapmaker platform. The configuration defines the essential machine parameters required to operate the system with Klipper, including MCU communication, Cartesian motion settings, stepper motor pin assignments, endstop inputs, auxiliary output pins, temperature sensing, bed mesh settings, input shaping, firmware retraction, the homing sequence, and custom G-code macros.

The configuration is designed for the original Snapmaker machine running Klipper through a USB serial connection. The MCU communicates at a baud rate of 115200, and the virtual SD card path is configured for use with Mainsail. The configuration has been tuned for the existing modified hardware setup.

This configuration also demonstrates how the Snapmaker tool connector can be used to control a stepper motor, a load output, and temperature sensing. In addition, it includes an example of using a Python interface from Klipper to control external hardware, such as a DAC-based pressure-control system.

# CAD model
The tool design is provided as a Fusion 360 CAD model in .f3d format, allowing users to inspect, modify, and adapt the mechanical design for their own Snapmaker Klipper modification setup.

# Wiring and Connector
This section provides the wiring diagram and connector information for the Snapmaker Klipper modification. The wiring diagram shows how the Klipper firmware interacts with the input and output pins of the controller board, including stepper motor signals, endstop inputs, temperature sensor inputs, auxiliary outputs, and power-control signals.

The tool connector information is provided to support custom tool development. It allows users to interface their own tool designs with the Snapmaker hardware by identifying the available electrical connections, signal pins, power lines, and sensor inputs. This section is intended to help users understand the relationship between the Klipper configuration file, the physical wiring, and the actual hardware behavior.

The wiring and connector documentation should be used together with the .cfg file to verify pin assignments before powering or operating the machine.

# References
a. Snapmaker Klipper by Ninth2234 : https://github.com/Ninth2234/snapmaker_klipper
b. open-interface-pressure-controller by schaiwuth : https://github.com/schaiwuth/open-interface-pressure-controller
c. Pico-Pneumatic-Valve by Ninth2234 : https://github.com/Ninth2234/Pico-Pneumatic-Valve
