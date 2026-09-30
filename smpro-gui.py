#! /usr/bin/env python3

import sys, os
import tkinter as tk
import tkinter.ttk as ttk
import smbus
import time

I2C_BUS = 1
I2C_ADDRESS = 0x20

IODIR_REGISTER = 0x00
GPIO_REGISTER = 0x09

POWER_PINS = {
    0: 6,   #dc1
    1: 5,   #dc2
    2: 4,   #dc3
    3: 3,   #dc4
}

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

    #print(f"{port}: {state.upper()}")

class Toplevel1:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''

        top.geometry("500x220")
        top.minsize(1, 1)
        top.resizable(0, 0)
        top.title("StellarMate Power Control")

        self.top = top

        # DC 12V frame
        self.Labelframe1 = ttk.LabelFrame(self.top, text="DC 12V")
        self.Labelframe1.place(x=10, y=10, width=490, height=170)

        # Frame holding channels
        dc_frame = ttk.Frame(self.Labelframe1)
        dc_frame.grid(row=0, column=0, padx=1, pady=0)

        # Master ON/OFF buttons
        master_frame = ttk.Frame(self.Labelframe1)
        master_frame.grid(row=0, column=1, padx=(5, 5), pady=10, sticky="ns")

        self.Button4 = ttk.Button(master_frame, text="ON", width=8,command=self.dc_on)
        self.Button4.grid(row=0, column=0, pady=(20, 10))

        self.Button4_2 = ttk.Button(master_frame, text="OFF", width=8,command=self.dc_off)
        self.Button4_2.grid(row=1, column=0, pady=10)


        # Create DC1 ... DC5
        self.dc_frames = []
        self.dc_on_buttons = []
        self.dc_off_buttons = []
        self.dc_labels = []
        self.dc = []

        for i in range(4):
                frame = ttk.LabelFrame(dc_frame, text=f"DC {i+1}")
                frame.grid(row=0, column=i, padx=1, pady=0, sticky="n")

                btn_on = ttk.Button(frame, text="ON", width=8, command=lambda ch=i: self.dc1_on(ch))
                btn_on.grid(row=0, column=0, padx=5, pady=(8,4))

                btn_off = ttk.Button(frame, text="OFF", width=8, command=lambda ch=i: self.dc1_off(ch))
                btn_off.grid(row=1, column=0, padx=5, pady=4)

                self.dc.append(tk.StringVar(value='OFF'))
                lbl = ttk.Label(frame, anchor="center", textvariable=self.dc[i])
                lbl.grid(row=2, column=0, pady=(8,8))

                self.dc_frames.append(frame)
                self.dc_on_buttons.append(btn_on)
                self.dc_off_buttons.append(btn_off)
                self.dc_labels.append(lbl)

        # Refresh button
        self.Button5 = ttk.Button(self.top,text="Refresh",width=10,command=self.refresh)
        self.Button5.place(x=205, y=185)
        
        
        self.bus = smbus.SMBus(I2C_BUS)
        init_gpio(self.bus)
        
        time.sleep(0.1)
        self.refresh()

    def dc1_on(self,number):
        pin = POWER_PINS[number]

        value = read_gpio(self.bus)
        time.sleep(0.1)
        
        value |= (1 << pin)
        
        write_gpio(self.bus, value)
        
        time.sleep(0.1)
        
        self.refresh()

    def dc1_off(self,number):
        pin = POWER_PINS[number]

        value = read_gpio(self.bus)
        time.sleep(0.1)
        
        value &= ~(1 << pin)
        
        write_gpio(self.bus, value)
        
        time.sleep(0.1)
        
        self.refresh()

    def dc_on(self):
        value = read_gpio(self.bus)
        time.sleep(0.1)
        
        mask = (
            (1 << POWER_PINS[0]) |
            (1 << POWER_PINS[1]) |
            (1 << POWER_PINS[2]) |
            (1 << POWER_PINS[3])
        )
        
        value |= mask
        
        write_gpio(self.bus, value)
        
        time.sleep(0.1)
        
        self.refresh()

    def dc_off(self):
        value = read_gpio(self.bus)
        time.sleep(0.1)
        
        mask = (
            (1 << POWER_PINS[0]) |
            (1 << POWER_PINS[1]) |
            (1 << POWER_PINS[2]) |
            (1 << POWER_PINS[3])
        )
        
        value &= ~mask
        
        write_gpio(self.bus, value)
        
        time.sleep(0.1)
        
        self.refresh()


    def refresh(self):
        value = read_gpio(self.bus)
        #print(f"GPIO register: 0x{value:02X}")

        for port, pin in POWER_PINS.items():
            if value & (1 << pin):
                self.dc[port].set('ON')
            else:
                self.dc[port].set('OFF')    


if __name__ == '__main__':
    '''Main entry point for the application.'''
    global root
    root = tk.Tk()
    #root.protocol( 'WM_DELETE_WINDOW' , root.destroy)
    # Creates a toplevel widget.
    global _top1, _w1
    _top1 = root
    _w1 = Toplevel1(_top1)
    root.mainloop()




