#!/usr/bin/env python3

import sys
import smbus

I2C_BUS = 1
I2C_ADDRESS = 0x20

IODIR_REGISTER = 0x00
GPIO_REGISTER = 0x09

POWER_PINS = {
    "dc1": 6,
    "dc2": 5,
    "dc3": 4,
    "dc4": 3,
}


def usage():
    print("""
Usage:
  smpro_power.py dc1 on
  smpro_power.py dc1 off
  smpro_power.py dc2 on
  smpro_power.py dc2 off
  smpro_power.py dc3 on
  smpro_power.py dc3 off
  smpro_power.py dc4 on
  smpro_power.py dc4 off

  smpro_power.py all on
  smpro_power.py all off

  smpro_power.py status
""")
    sys.exit(1)


def init_gpio(bus):
    # Configure MCP23008 GPIO pins as outputs.
    bus.write_byte_data(
        I2C_ADDRESS,
        IODIR_REGISTER,
        0x00
    )


def read_gpio(bus):
    return bus.read_byte_data(
        I2C_ADDRESS,
        GPIO_REGISTER
    )


def write_gpio(bus, value):
    bus.write_byte_data(
        I2C_ADDRESS,
        GPIO_REGISTER,
        value & 0xFF
    )


def set_port(bus, port, state):
    pin = POWER_PINS[port]

    value = read_gpio(bus)

    if state == "on":
        value |= (1 << pin)
    else:
        value &= ~(1 << pin)

    write_gpio(bus, value)

    print(f"{port}: {state.upper()}")


def set_all(bus, state):
    value = read_gpio(bus)

    mask = (
        (1 << POWER_PINS["dc1"]) |
        (1 << POWER_PINS["dc2"]) |
        (1 << POWER_PINS["dc3"]) |
        (1 << POWER_PINS["dc4"])
    )

    if state == "on":
        value |= mask
    else:
        value &= ~mask

    write_gpio(bus, value)

    print(f"All DC ports: {state.upper()}")


def status(bus):
    value = read_gpio(bus)

    print(f"GPIO register: 0x{value:02X}")

    for port, pin in POWER_PINS.items():
        if value & (1 << pin):
            print(f"{port.upper()}: ON")
        else:
            print(f"{port.upper()}: OFF")


def main():
    if len(sys.argv) < 2:
        usage()

    bus = smbus.SMBus(I2C_BUS)

    try:
        init_gpio(bus)

        if sys.argv[1] == "status":
            status(bus)
            return

        if sys.argv[1] == "all":
            if len(sys.argv) != 3:
                usage()

            state = sys.argv[2].lower()

            if state not in ("on", "off"):
                usage()

            set_all(bus, state)
            
            status(bus)
            return

        port = sys.argv[1].lower()

        if port not in POWER_PINS:
            usage()

        if len(sys.argv) != 3:
            usage()

        state = sys.argv[2].lower()

        if state not in ("on", "off"):
            usage()

        set_port(bus, port, state)
        
        status(bus)

    finally:
        bus.close()


if __name__ == "__main__":
    main()
    