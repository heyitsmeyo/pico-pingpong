import board
import busio
import digitalio
import displayio
import os
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306
from adafruit_display_shapes.rect import Rect
import time

#displayio.release_displays()

board_type = os.uname().machine

if 'Pico' in board_type:
    sda, sck = board.GP0, board.GP1

i2c = busio.I2C(sck, sda)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

splash = displayio.Group()
display.show(splash)

paddle_width = 5
paddle_height = 20
ball_radius = 3

def show_menu():
    def play_start_tone():
        # Play the start tone on the buzzer
        buzzer.value = True
        time.sleep(0.1)  # Adjust the duration and frequency as needed
        buzzer.value = False

    menu_group = displayio.Group()
    menu_label = label.Label(terminalio.FONT, text="Press start")
    menu_label.x = (display.width - menu_label.bounding_box[2]) // 2
    menu_label.y = (display.height - menu_label.bounding_box[3]) // 2
    menu_group.append(menu_label)
    display.show(menu_group)

    button_start = digitalio.DigitalInOut(board.GP7)
    button_start.switch_to_input(pull=digitalio.Pull.UP)
    play_start_tone()

    while True:
        if not button_start.value:
            menu_group.remove(menu_label)  # Remove the menu label from the menu group
            display.refresh()
            break

    display.show(splash)  # Show the game display after the start button is pressed

paddle_x = 0
paddle1_y = (display.height - paddle_height) // 2
paddle2_y = (display.height - paddle_height) // 2

ball_x = display.width // 2
ball_y = display.height // 2
ball_dx = 2
ball_dy = 2

score1 = 0
score2 = 0

paddle1 = Rect(0, 0, paddle_width, paddle_height, fill=0xFFFFFF)
paddle1.x = paddle_x
paddle1.y = paddle1_y

paddle2 = Rect(0, 0, paddle_width, paddle_height, fill=0xFFFFFF)
paddle2.x = display.width - paddle_width
paddle2.y = paddle2_y

ball = Rect(0, 0, ball_radius * 2, ball_radius * 2, fill=0xFFFFFF)
ball.x = ball_x - ball_radius
ball.y = ball_y - ball_radius

splash.append(paddle1)
splash.append(paddle2)
splash.append(ball)

score_label = label.Label(terminalio.FONT, text="0 - 0" , size=2)
score_label.x = (display.width - score_label.bounding_box[2]) // 2
score_label.y = 3

line = Rect(0, 0, 1, display.height, fill=0xFFFFFF)
line.x = display.width // 2
line.y = 0

splash.append(line)

splash.append(score_label)

# Configure buttons for Player 1
button_up1 = digitalio.DigitalInOut(board.GP2)
button_up1.switch_to_input(pull=digitalio.Pull.UP)
button_down1 = digitalio.DigitalInOut(board.GP3)
button_down1.switch_to_input(pull=digitalio.Pull.UP)

# Configure buttons for Player 2
button_up2 = digitalio.DigitalInOut(board.GP4)
button_up2.switch_to_input(pull=digitalio.Pull.UP)
button_down2 = digitalio.DigitalInOut(board.GP5)
button_down2.switch_to_input(pull=digitalio.Pull.UP)

buzzer_pin = board.GP6
buzzer = digitalio.DigitalInOut(buzzer_pin)
buzzer.direction = digitalio.Direction.OUTPUT

def play_edge_hit_sound():
    # Play the edge hit sound
    buzzer.value = True
    time.sleep(0.1)  # Adjust the duration as needed
    buzzer.value = False

def play_buzzer(duration):
    buzzer.value = True
    time.sleep(duration)
    buzzer.value = False

def game_over(winning_player):
    global score1, score2
    
    # Reset the score to 0
    score1 = 0
    score2 = 0

    # Display the winning player
    winning_label = label.Label(terminalio.FONT, text="Player {} wins!".format(winning_player))
    winning_label.x = (display.width - winning_label.bounding_box[2]) // 2
    winning_label.y = (display.height - winning_label.bounding_box[3]) // 2
    splash.append(winning_label)
    display.refresh()
    time.sleep(2)  # Delay for 2 seconds

    # Reset the game state
    winning_player = 0
    splash.remove(winning_label)
    score_label.text = "{} - {}".format(score1, score2)
    ball_x = display.width // 2
    ball_y = display.height // 2

show_menu()

while True:
    # Move Player 1 paddle up if the up button is pressed
    if not button_up1.value:
        paddle1_y -= 1
    # Move Player 1 paddle down if the down button is pressed
    if not button_down1.value:
        paddle1_y += 1

    # Move Player 2 paddle up if the up button is pressed
    if not button_up2.value:
        paddle2_y -= 1
    # Move Player 2 paddle down if the down button is pressed
    if not button_down2.value:
        paddle2_y += 1

    if paddle1_y < 0:
        paddle1_y = 0
    elif paddle1_y > display.height - paddle_height:
        paddle1_y = display.height - paddle_height

    if paddle2_y < 0:
        paddle2_y = 0
    elif paddle2_y > display.height - paddle_height:
        paddle2_y = display.height - paddle_height

    # Update paddle positions
    paddle1.y = paddle1_y
    paddle2.y = paddle2_y

    # Move the ball
    ball_x += ball_dx
    ball_y += ball_dy

    # Bounce the ball if it hits the display edges
    if ball_x <= 0 or ball_x >= display.width - ball_radius * 2:
        ball_dx = -ball_dx
        play_edge_hit_sound()

        # Check which player scored
        if ball_x <= 0:
            score2 += 1
        else:
            score1 += 1

        # Update the score label
        score_label.text = "{} - {}".format(score1, score2)

        # Check if any player has reached the winning score
        if score1 == 3:
            game_over(1)
        elif score2 == 3:
            game_over(2)
        else:
            # Reset the ball position to the center
            ball_x = display.width // 2
            ball_y = display.height // 2

    if ball_y <= 0 or ball_y >= display.height - ball_radius * 2:
        ball_dy = -ball_dy
        play_edge_hit_sound()

    # Update the ball position
    ball.x = ball_x - ball_radius
    ball.y = ball_y - ball_radius

    # Check if the ball hits Player 1 paddle
    if (
        ball_x <= paddle1.x + paddle_width
        and paddle1.y <= ball_y + ball_radius
        and ball_y <= paddle1.y + paddle_height
    ):
        ball_dx = -ball_dx
        play_buzzer(0.1)  # Play buzzer sound for Player 1

    # Check if the ball hits Player 2 paddle
    if (
        ball_x >= paddle2.x - ball_radius * 2
        and paddle2.y <= ball_y + ball_radius
        and ball_y <= paddle2.y + paddle_height
    ):
        ball_dx = -ball_dx
        play_buzzer(0.1)  # Play buzzer sound for Player 2

    display.refresh()
    time.sleep(0.01)  # Delay between game loop iterations

