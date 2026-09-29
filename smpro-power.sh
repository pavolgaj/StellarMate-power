#!/bin/bash

# NOT combine with INDI!!!

I2C_BUS=1
I2C_ADDR=0x20
GPIO_REG=0x09

usage() {
    echo "Usage:"
    echo "  $0 dc1 on|off"
    echo "  $0 dc2 on|off"
    echo "  $0 dc3 on|off"
    echo "  $0 dc4 on|off"
    echo "  $0 status"
    echo "  $0 all on|off"
    exit 1
}

# Handle status
if [[ "$1" == "status" ]]; then
    VALUE=$(i2cget -y "$I2C_BUS" "$I2C_ADDR" "$GPIO_REG")
    printf "GPIO register: %s\n" "$VALUE"

    for item in "DC1:6" "DC2:5" "DC3:4" "DC4:3"; do
        NAME="${item%%:*}"
        B="${item##*:}"

        if (( (VALUE & (1 << B)) != 0 )); then
            echo "$NAME: ON"
        else
            echo "$NAME: OFF"
        fi
    done

    exit 0
fi

# Handle all on/off
if [[ "$1" == "all" ]]; then
    if [[ "$2" != "on" && "$2" != "off" ]]; then
        usage
    fi

    VALUE=$(i2cget -y "$I2C_BUS" "$I2C_ADDR" "$GPIO_REG")

    if [[ "$2" == "on" ]]; then
        VALUE=$((VALUE | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 6)))
    else
        VALUE=$((VALUE & ~(1 << 3) & ~(1 << 4) & ~(1 << 5) & ~(1 << 6)))
    fi

    printf -v HEX '0x%02X' "$VALUE"

    echo "Setting all $2 (GPIO register = $HEX)"

    i2cset -y "$I2C_BUS" "$I2C_ADDR" "$GPIO_REG" "$HEX"
    
    # write status
    VALUE=$(i2cget -y "$I2C_BUS" "$I2C_ADDR" "$GPIO_REG")

    for item in "DC1:6" "DC2:5" "DC3:4" "DC4:3"; do
        NAME="${item%%:*}"
        B="${item##*:}"

        if (( (VALUE & (1 << B)) != 0 )); then
            echo "$NAME: ON"
        else
            echo "$NAME: OFF"
        fi
    done
    
    exit $?
fi

# GPIO mapping from SM Pro hardware_interface.cpp
case "$1" in
    dc1) BIT=6 ;;
    dc2) BIT=5 ;;
    dc3) BIT=4 ;;
    dc4) BIT=3 ;;
    *)
        usage
        ;;
esac

ACTION="$2"

if [[ "$ACTION" != "on" && "$ACTION" != "off" ]]; then
    usage
fi

VALUE=$(i2cget -y "$I2C_BUS" "$I2C_ADDR" "$GPIO_REG")

if [[ "$ACTION" == "on" ]]; then
    VALUE=$((VALUE | (1 << BIT)))
else
    VALUE=$((VALUE & ~(1 << BIT)))
fi

printf -v HEX '0x%02X' "$VALUE"

echo "Setting $1 $ACTION (GPIO register = $HEX)"

i2cset -y "$I2C_BUS" "$I2C_ADDR" "$GPIO_REG" "$HEX"

# write status
VALUE=$(i2cget -y "$I2C_BUS" "$I2C_ADDR" "$GPIO_REG")

for item in "DC1:6" "DC2:5" "DC3:4" "DC4:3"; do
    NAME="${item%%:*}"
    B="${item##*:}"

    if (( (VALUE & (1 << B)) != 0 )); then
        echo "$NAME: ON"
    else
        echo "$NAME: OFF"
    fi
done
    