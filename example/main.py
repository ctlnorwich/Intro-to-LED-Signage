"""Introduction to LED Signage - main example.

A looping GIF background with pink scrolling text over the top, for the
Pimoroni Interstate 75 W (RP2350) and a HUB75 LED matrix panel.

"""

# ---------------------------------------------------------------------------
# LIBRARIES - code other people have written that we borrow
# ---------------------------------------------------------------------------

# "os" lets us look inside folders on the board, to find our GIF frames.
import os

# "time" lets us pause between frames so the animation plays at a steady speed.
import time

# "pngdec" opens PNG image files and draws them onto the display.
import pngdec

# The Interstate 75 driver, plus the names of the panel sizes we might use.
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X64, DISPLAY_INTERSTATE75_128X64

# PicoVector draws smooth text using our Alright Font (.af) file.
from picovector import PicoVector, Transform, ANTIALIAS_NONE, ANTIALIAS_FAST, ANTIALIAS_BEST


# ---------------------------------------------------------------------------
# SETTINGS - these are the lines you will change during the workshop!
# ---------------------------------------------------------------------------

# The size of the LED panel. For a 128x64 panel use DISPLAY_INTERSTATE75_128X64.
PANEL = DISPLAY_INTERSTATE75_64X64

# The folder on the board holding the background animation frames (PNG files).
GIF_FOLDER = "gif"

# Seconds to wait between frames. Smaller = faster animation AND faster text.
FRAME_DELAY = 0.05

# Background brightness, from 0 (off) to 1 (full). 0.5 = half, so the text stands out.
BACKGROUND_BRIGHTNESS = 0.5

# The Alright Font (.af) file on the board used to draw the text.
FONT_FILE = "fonts/cherry-hq.af"

# The words that scroll across the sign. Keep them inside the quote marks!
MESSAGE = "I must not fear. Fear is the mind-killer. Fear is the little-death that brings total obliteration."

# The height of the text in pixels. Remember, the panel is only 64 pixels tall!
TEXT_SIZE = 24

# How far down from the top of the screen the text sits, in pixels (0 = top).
TEXT_Y = 20

# The text colour as (red, green, blue). Each goes from 0 (off) to 255 (full).
TEXT_COLOUR = (255, 20, 147)

# Text brightness (both lines), from 0 (off) to 1 (full).
TEXT_BRIGHTNESS = 1

# Pixels the text moves left each frame. Try 2 for faster, or 0.5 for slower.
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
# FUNCTIONS - named chunks of code we can run whenever we like
# ---------------------------------------------------------------------------

# Define a function that makes a pen from a colour, dimmed by a brightness.
def dimmed_pen(colour, brightness):
    """Return a pen for a (red, green, blue) colour scaled by brightness (0 to 1)."""

    # Multiply red, green and blue by the brightness, and make a pen from them.
    return display.create_pen(int(colour[0] * brightness), int(colour[1] * brightness), int(colour[2] * brightness))


# Ask MicroPython to turn this function into super-fast "viper" machine code.
@micropython.viper  # noqa: F821
# Define a function that dims every pixel on the canvas. level 256 = unchanged.
def dim_canvas(canvas: ptr32, pixel_count: int, level: int):  # noqa: F821
    # Do this for every pixel on the canvas.
    for i in range(pixel_count):

        # Each pixel is stored as one number holding red, green and blue.
        colour = canvas[i]

        # Pull out the red part of the pixel and scale it by level / 256.
        red = ((colour >> 16) & 0xFF) * level >> 8

        # Pull out the green part and scale it.
        green = ((colour >> 8) & 0xFF) * level >> 8

        # Pull out the blue part and scale it.
        blue = (colour & 0xFF) * level >> 8

        # Put the three parts back together and store the dimmed pixel.
        canvas[i] = (red << 16) | (green << 8) | blue


# ---------------------------------------------------------------------------
# SETUP - this part runs once, when the board starts
# ---------------------------------------------------------------------------

# Start up the Interstate 75 and tell it what size panel is plugged in.
i75 = Interstate75(display=PANEL)

# "display" is our canvas. We draw here first, then send it to the LEDs.
display = i75.display

# Remember the panel width in pixels, so we know where the right edge is.
WIDTH = i75.width

# Count the pixels on the panel (width x height).
PIXEL_COUNT = WIDTH * i75.height

# Get direct access to the canvas's memory, so dim_canvas can change it fast.
canvas = memoryview(display)

# Turn BACKGROUND_BRIGHTNESS (0 to 1) into the whole number (0 to 256) dim_canvas needs.
BACKGROUND_LEVEL = int(BACKGROUND_BRIGHTNESS * 256)

# Create a black pen, used to wipe the screen clean before each frame.
BLACK = display.create_pen(0, 0, 0)

# Turn our text colour and brightness into a "pen" to draw with.
TEXT_PEN = dimmed_pen(TEXT_COLOUR, TEXT_BRIGHTNESS)

# Create a PNG decoder that draws images straight onto our canvas.
png = pngdec.PNG(display)

# Create a PicoVector renderer that also draws onto our canvas.
vector = PicoVector(display)

# Tell PicoVector how smooth to make the edges of the letters.
vector.set_antialiasing(ANTIALIASING)

# Make a blank "transform" (no rotating or stretching) for PicoVector to use.
# It MUST be kept in a variable, or the board's memory clean-up deletes it
# and the text disappears after a few seconds!
transform = Transform()

# Tell PicoVector to use our transform.
vector.set_transform(transform)

# Load our font file from the board, at the size of our main message.
vector.set_font(FONT_FILE, TEXT_SIZE)

# List every file in the GIF folder, sorted into order (frame_000, frame_001...).
frame_names = sorted(os.listdir(GIF_FOLDER))

# Keep only PNG files, adding the folder name to each, e.g. "gif/frame_000.png".
frames = [GIF_FOLDER + "/" + name for name in frame_names if name.lower().endswith(".png")]

# Measure the message: its width, and where its top edge is.
_, text_top, text_width, _ = vector.measure_text(MESSAGE)

# Start the message just off the right-hand edge, so it scrolls in.
text_x = WIDTH

# Only do this setup if the second line is switched on.
if SHOW_SECOND_LINE:

    # Turn the second line's colour and the text brightness into a pen.
    SECOND_PEN = dimmed_pen(SECOND_TEXT_COLOUR, TEXT_BRIGHTNESS)

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

# Start the animation on the first frame. Computers count from 0!
frame_number = 0

# Remember when we started counting frames, in milliseconds.
fps_start = time.ticks_ms()

# Count how many frames we've drawn since then.
fps_frames = 0


# ---------------------------------------------------------------------------
# MAIN LOOP - this part repeats forever, once per frame
# ---------------------------------------------------------------------------

# "while True" means loop forever. A sign never stops!
while True:

    # Pick up the black pen.
    display.set_pen(BLACK)

    # Wipe the whole canvas black, so nothing from the last frame is left.
    display.clear()

    # Open the PNG file for the current frame of the animation.
    png.open_file(frames[frame_number])

    # Draw the frame with its top-left corner at the top-left of the screen.
    png.decode(0, 0)

    # Dim the background, before any text is drawn on top of it.
    dim_canvas(canvas, PIXEL_COUNT, BACKGROUND_LEVEL)

    # Move to the next frame. The % wraps back to 0 after the last one.
    frame_number = (frame_number + 1) % len(frames)

    # Pick up the pink pen.
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
