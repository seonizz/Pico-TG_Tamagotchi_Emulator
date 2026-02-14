# Pico-TG-Tamagotchi-Emulator

## Hardware
- Raspberry Pi Pico
- SSD1306 OLED (I2C)
- 3 Push Buttons
- Battery via VSYS

## Features
- FOOD / WASH system
- Status decay
- Jump mini-game
- Battery standalone boot (main.py auto run)

## Pin Mapping
red/VSYS
black/GND

[OLED/Pico]
GND/GND
VCC/3V3(OUT)
SCL/GP21
SDA/GP20

[button/Pico] 
1/GP16 
2/GP17 
3/GP18 
u/GND

## How to Run
Save files to Pico as main.py and power via VSYS.
