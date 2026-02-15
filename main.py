import machine
import ssd1306
import time
import framebuf
import sprites

i2c = machine.I2C(0, scl=machine.Pin(21), sda=machine.Pin(20))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

btn_a = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
btn_left = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)
btn_right = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)

def make_fb(data, w, h):
    size = (w * h) // 8
    buf = bytearray(size)
    for i in range(min(len(data), size)):
        buf[i] = data[i]
    return framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HLSB)

heart_fb = make_fb(sprites.icon_heart, 8, 8)
chicken_fb = make_fb(sprites.icon_chicken, 8, 8)
event_food_fb = make_fb(sprites.event_food, 16, 16)
event_wash_fb = make_fb(sprites.event_wash, 16, 16)
char_fbs = [make_fb(f, 32, 32) for f in sprites.char_frames]

obstacle_data = bytearray([
    0x03,0x80,
    0x07,0xC0,
    0x07,0xC0,
    0x03,0x80,
    0x03,0x80,
    0x03,0x80,
    0x07,0xC0,
    0x00,0x00
])
obstacle_fb = make_fb(obstacle_data, 16, 8)

MODE_MAIN = 0
MODE_GAME = 1
mode = MODE_MAIN

heart_val = 3
food_val = 3
menu_index = 0
frame_idx = 0
last_decay_time = time.ticks_ms()

event_icon = None
event_start = 0
EVENT_DURATION = 3000

GROUND_Y = 36
player_y = GROUND_Y
velocity = 0
gravity = 1
jump_power = -16
obstacle_x = 128
score = 0

sleep_mode = False

while True:
    now = time.ticks_ms()

    if not btn_left.value() and not btn_right.value():
        oled.fill(0)
        oled.show()
        sleep_mode = True
        time.sleep(0.3)

    if sleep_mode:
        oled.fill(0)
        oled.show()
        if not btn_a.value():
            sleep_mode = False
            time.sleep(0.3)
        time.sleep(0.1)
        continue

    if mode == MODE_MAIN:
        if not btn_left.value():
            menu_index = (menu_index - 1) % 3
            time.sleep(0.2)

        if not btn_right.value():
            menu_index = (menu_index + 1) % 3
            time.sleep(0.2)

        if not btn_a.value():
            if menu_index == 0:
                food_val = min(3, food_val + 1)
                event_icon = event_food_fb
                event_start = now
            elif menu_index == 1:
                heart_val = min(3, heart_val + 1)
                event_icon = event_wash_fb
                event_start = now
            elif menu_index == 2:
                mode = MODE_GAME
                obstacle_x = 128
                player_y = GROUND_Y
                velocity = 0
                score = 0
            time.sleep(0.2)

        if event_icon and time.ticks_diff(now, event_start) > EVENT_DURATION:
            event_icon = None

        oled.fill(0)

        for i in range(heart_val):
            oled.blit(heart_fb, i * 10 + 2, 2)

        for i in range(food_val):
            oled.blit(chicken_fb, 128 - (i + 1) * 10, 2)

        oled.blit(char_fbs[(frame_idx // 5) % len(char_fbs)], 48, 20)

        if event_icon:
            oled.blit(event_icon, 88, 20)

        oled.hline(0, 52, 128, 1)
        menus = ["FOOD", "WASH", "PLAY"]

        for i, m in enumerate(menus):
            x = i * 42 + 5
            if i == menu_index:
                oled.fill_rect(i * 42, 54, 42, 10, 1)
                oled.text(m, x, 56, 0)
            else:
                oled.text(m, x, 56, 1)

        if time.ticks_diff(now, last_decay_time) > 20000:
            food_val = max(1, food_val - 1)
            heart_val = max(1, heart_val - 1)
            last_decay_time = now

    else:
        if not btn_a.value() and player_y == GROUND_Y:
            velocity = jump_power

        velocity += gravity
        player_y += velocity

        if player_y > GROUND_Y:
            player_y = GROUND_Y
            velocity = 0

        obstacle_x -= 4
        if obstacle_x < -16:
            obstacle_x = 128
            score += 1

        if obstacle_x < 64 and obstacle_x > 40:
            if player_y > GROUND_Y - 24:
                mode = MODE_MAIN
                time.sleep(0.5)

        oled.fill(0)
        oled.hline(0, GROUND_Y + 16, 128, 1)
        oled.blit(char_fbs[0], 48, int(player_y))
        oled.blit(obstacle_fb, obstacle_x, GROUND_Y + 8)
        oled.text("Score:" + str(score), 0, 0)

    oled.show()
    frame_idx += 1
    time.sleep(0.05)
