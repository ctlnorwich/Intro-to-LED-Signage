"""Introduction to LED Signage - alternative example.

Instead of playing GIF frames, this example *generates* its background
while it runs, using Voronoi noise: a handful of invisible points drift
around the screen, and every pixel is coloured by whichever point is closest.
The scrolling text (and optional second line) works exactly the same as in
the main example.

Every line has a comment (starting with #) explaining what it does.
"""

# ---------------------------------------------------------------------------
# LIBRARIES - code other people have written that we borrow
# ---------------------------------------------------------------------------

# "math" gives us square roots, which we need to measure distances.
import math

# "random" lets us pick random starting positions, speeds and colours.
import random

# "time" lets us pause between frames.
import time

# The Interstate 75 driver, plus the names of the panel sizes we might use.
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X64, DISPLAY_INTERSTATE75_128X64

# PicoVector draws smooth text using our Alright Font (.af) file.
from picovector import PicoVector, Transform, ANTIALIAS_NONE, ANTIALIAS_FAST, ANTIALIAS_BEST


# ---------------------------------------------------------------------------
# SETTINGS - background
# ---------------------------------------------------------------------------

# The size of the LED panel. For a 128x64 panel use DISPLAY_INTERSTATE75_128X64.
PANEL = DISPLAY_INTERSTATE75_64X64

# How many drifting points (and so how many cells) there are.
NUM_POINTS = 8

# Size of each chunky "block" in pixels. 1 = full detail but slow, 4 = fast.
BLOCK_SIZE = 2

# How many pixels the points can drift each frame.
POINT_SPEED = 0.5

# How far (in pixels) the light spreads out from each point before fading out.
GLOW = 24

# The range of colours used, as a position on the colour wheel from 0 to 1.
# 0 = red, 0.17 = yellow, 0.33 = green, 0.5 = cyan, 0.66 = blue, 0.83 = magenta.
HUE_MIN = 0.55

# The other end of the colour range (see above).
HUE_MAX = 0.8

# How quickly all the colours travel around the colour wheel. 0 = not at all.
COLOUR_DRIFT = 0.002

# Background brightness, from 0 (off) to 1 (full). 0.5 = half, so the text stands out.
BACKGROUND_BRIGHTNESS = 0.5

# Seconds to wait between frames. Drawing the noise already takes a while!
FRAME_DELAY = 0.01


# ---------------------------------------------------------------------------
# SETTINGS - text (the same as the main example)
# ---------------------------------------------------------------------------

# The Alright Font (.af) file on the board used to draw the text.
FONT_FILE = "fonts/cherry-hq.af"

# The words that scroll across the sign. Keep them inside the quote marks!
MESSAGE = "I must not fear. Fear is the mind-killer. Fear is the little-death that brings total obliteration."

# The height of the text in pixels.
TEXT_SIZE = 24

# How far down from the top of the screen the text sits, in pixels (0 = top).
TEXT_Y = 20

# The text colour as (red, green, blue). Each goes from 0 (off) to 255 (full). This is white.
TEXT_COLOUR = (255, 255, 255)

# Text brightness (both lines), from 0 (off) to 1 (full).
TEXT_BRIGHTNESS = 1

# Pixels the text moves left each frame.
SCROLL_SPEED = 1

# Change False to True to switch on a second line of text.
SHOW_SECOND_LINE = False

# The words for the second line. This line does not scroll, so keep it short!
SECOND_MESSAGE = "DUNE"

# The Alright Font (.af) file for the second line. A different font adds contrast!
SECOND_FONT_FILE = "fonts/silkscreen.af"

# The height of the second line of text in pixels.
SECOND_TEXT_SIZE = 12

# How far down from the top of the screen the second line sits, in pixels.
SECOND_TEXT_Y = 48

# The colour of the second line as (red, green, blue). This is white.
SECOND_TEXT_COLOUR = (255, 255, 255)

# Smoothness of letter edges: ANTIALIAS_NONE, ANTIALIAS_FAST or ANTIALIAS_BEST.
ANTIALIASING = ANTIALIAS_FAST


# ---------------------------------------------------------------------------
# SETUP - this part runs once, when the board starts
# ---------------------------------------------------------------------------

# Start up the Interstate 75 and tell it what size panel is plugged in.
i75 = Interstate75(display=PANEL)

# "display" is our canvas. We draw here first, then send it to the LEDs.
display = i75.display

# Remember the panel width in pixels.
WIDTH = i75.width

# Remember the panel height in pixels.
HEIGHT = i75.height

# Turn our text colour into a "pen", multiplying red, green and blue by the brightness.
TEXT_PEN = display.create_pen(int(TEXT_COLOUR[0] * TEXT_BRIGHTNESS), int(TEXT_COLOUR[1] * TEXT_BRIGHTNESS), int(TEXT_COLOUR[2] * TEXT_BRIGHTNESS))

# Create a PicoVector renderer that draws onto our canvas.
vector = PicoVector(display)

# Tell PicoVector how smooth to make the edges of the letters.
vector.set_antialiasing(ANTIALIASING)

# Make a blank "transform" (no rotating or stretching) for PicoVector to use.
# It MUST be kept in a variable, or the board's memory clean-up deletes it
# and the text disappears after a few seconds!
transform = Transform()

# Tell PicoVector to use our transform.
vector.set_transform(transform)

# Load our font file from the board, at the size of our message.
vector.set_font(FONT_FILE, TEXT_SIZE)

# Measure the message: its width, and where its top edge is.
_, text_top, text_width, _ = vector.measure_text(MESSAGE)

# Start the message just off the right-hand edge, so it scrolls in.
text_x = WIDTH

# Only do this setup if the second line is switched on.
if SHOW_SECOND_LINE:

    # Turn the second line's colour into a pen, multiplying by the text brightness.
    SECOND_PEN = display.create_pen(int(SECOND_TEXT_COLOUR[0] * TEXT_BRIGHTNESS), int(SECOND_TEXT_COLOUR[1] * TEXT_BRIGHTNESS), int(SECOND_TEXT_COLOUR[2] * TEXT_BRIGHTNESS))

    # Create a second PicoVector renderer. Each one holds its own font.
    second_vector = PicoVector(display)

    # Starting a new renderer resets the smoothness, so set it again.
    second_vector.set_antialiasing(ANTIALIASING)

    # Starting a new renderer also resets the transform, so set it again too.
    second_vector.set_transform(transform)

    # Load the second line's font file from the board, at the second line's size.
    second_vector.set_font(SECOND_FONT_FILE, SECOND_TEXT_SIZE)

    # Measure the second line: its width, and where its top edge is.
    _, second_top, second_width, _ = second_vector.measure_text(SECOND_MESSAGE)

    # Work out the x position that puts the second line in the middle.
    second_x = int((WIDTH - second_width) / 2)

# Empty lists to hold each point's x position, y position, speeds and colour.
point_x = []

# Each point's y position.
point_y = []

# Each point's speed left/right (negative = left).
point_dx = []

# Each point's speed up/down (negative = up).
point_dy = []

# Each point's colour, as a position on the colour wheel.
point_hue = []

# Repeat once for every point we want to create.
for _ in range(NUM_POINTS):

    # Give the point a random x position somewhere across the screen.
    point_x.append(random.uniform(0, WIDTH))

    # Give the point a random y position somewhere down the screen.
    point_y.append(random.uniform(0, HEIGHT))

    # Give the point a random left/right speed.
    point_dx.append(random.uniform(-POINT_SPEED, POINT_SPEED))

    # Give the point a random up/down speed.
    point_dy.append(random.uniform(-POINT_SPEED, POINT_SPEED))

    # Give the point a random colour from inside our colour range.
    point_hue.append(random.uniform(HUE_MIN, HUE_MAX))

# How far the colours have travelled around the colour wheel so far.
hue_shift = 0

# Remember when we started counting frames, in milliseconds.
fps_start = time.ticks_ms()

# Count how many frames we've drawn since then.
fps_frames = 0


# ---------------------------------------------------------------------------
# FUNCTIONS - named chunks of code we can run whenever we like
# ---------------------------------------------------------------------------

# Ask MicroPython to turn this function into faster machine code.
@micropython.native  # noqa: F821
# Define a function called draw_voronoi. It needs to know the current hue_shift.
def draw_voronoi(hue_shift):
    """Draw one frame of Voronoi noise across the whole screen."""

    # Step down the screen one block at a time...
    for y in range(0, HEIGHT, BLOCK_SIZE):

        # ...and across the screen one block at a time.
        for x in range(0, WIDTH, BLOCK_SIZE):

            # Start with a huge distance, so any real point will be closer.
            closest_distance = 1000000

            # Remember which point is closest. We start by guessing point 0.
            closest_point = 0

            # Check every point, one at a time.
            for i in range(NUM_POINTS):

                # How far across this block is from the point.
                dx = x - point_x[i]

                # How far down this block is from the point.
                dy = y - point_y[i]

                # Pythagoras! Distance squared (skipping the slow square root).
                distance = dx * dx + dy * dy

                # If this point is closer than any we've found so far...
                if distance < closest_distance:

                    # ...remember how close it is...
                    closest_distance = distance

                    # ...and which point it was.
                    closest_point = i

            # Brightness: 1 right on top of the point, fading to 0 at GLOW pixels away.
            brightness = 1 - math.sqrt(closest_distance) / GLOW

            # If we're further away than GLOW, brightness would go negative...
            if brightness < 0:

                # ...so keep it at 0 (off).
                brightness = 0

            # The colour of this block is the colour of its closest point, plus the drift.
            hue = (point_hue[closest_point] + hue_shift) % 1

            # Make a pen from the colour (hue), full saturation (1), and brightness.
            display.set_pen(display.create_pen_hsv(hue, 1, brightness * BACKGROUND_BRIGHTNESS))

            # Fill in this block with that pen.
            display.rectangle(x, y, BLOCK_SIZE, BLOCK_SIZE)


# Define a function called move_points, which drifts every point a little.
def move_points():
    """Move every point by its speed, bouncing off the edges of the screen."""

    # Do this for every point.
    for i in range(NUM_POINTS):

        # Move the point left/right by its speed.
        point_x[i] += point_dx[i]

        # Move the point up/down by its speed.
        point_y[i] += point_dy[i]

        # If the point has gone off the left or right edge...
        if point_x[i] < 0 or point_x[i] > WIDTH:

            # ...flip its left/right speed so it bounces back.
            point_dx[i] = -point_dx[i]

        # If the point has gone off the top or bottom edge...
        if point_y[i] < 0 or point_y[i] > HEIGHT:

            # ...flip its up/down speed so it bounces back.
            point_dy[i] = -point_dy[i]


# ---------------------------------------------------------------------------
# MAIN LOOP - this part repeats forever, once per frame
# ---------------------------------------------------------------------------

# "while True" means loop forever. A sign never stops!
while True:

    # Draw the background. It covers every pixel, so we don't need to clear first.
    draw_voronoi(hue_shift)

    # Drift the points ready for the next frame.
    move_points()

    # Nudge all the colours a little way around the colour wheel.
    hue_shift += COLOUR_DRIFT

    # Pick up the text pen.
    display.set_pen(TEXT_PEN)

    # Draw the message at its current position. int() rounds to whole pixels.
    vector.text(MESSAGE, int(text_x), int(TEXT_Y - text_top))

    # Nudge the message to the left, ready for the next frame.
    text_x -= SCROLL_SPEED

    # If the end of the message has completely left the screen on the left...
    if text_x < -text_width:

        # ...send it back to the right-hand edge to scroll in again.
        text_x = WIDTH

    # Only draw the second line if it is switched on.
    if SHOW_SECOND_LINE:

        # Pick up the second line's pen.
        display.set_pen(SECOND_PEN)

        # Draw the second line in its own font, centred, at its height on the screen.
        second_vector.text(SECOND_MESSAGE, second_x, int(SECOND_TEXT_Y - second_top))

    # Send the canvas to the LED panel. Nothing shows until we do this!
    i75.update()

    # Wait a moment before drawing the next frame.
    time.sleep(FRAME_DELAY)

    # Count this frame.
    fps_frames += 1

    # Work out how many milliseconds have passed since we started counting.
    fps_elapsed = time.ticks_diff(time.ticks_ms(), fps_start)

    # Once a whole second (1000 milliseconds) has passed...
    if fps_elapsed >= 1000:

        # ...print the frames per second to the Shell in Thonny.
        print("FPS:", round(fps_frames * 1000 / fps_elapsed, 1))

        # Start counting again from now.
        fps_start = time.ticks_ms()

        # Reset the frame count.
        fps_frames = 0
