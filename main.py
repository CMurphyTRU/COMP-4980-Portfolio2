
from PIL import Image
from fractal import mandelbrot, julia
from colors import get_color
from randomizer import randomize_settings

import os
import random


# Image dimensions.
WIDTH = 800
HEIGHT = 600

# Maximum iterations per pixel.
MAX_ITERATIONS = 500

# Default generation settings.
FRACTAL_TYPE = "julia"
PALETTE = "rainbow"
ZOOM = 1.0
CENTER_X = 0.0
CENTER_Y = 0.0

# Fixed Julia constant used when randomization is disabled.
JULIA_C = complex(-0.7, 0.27015)

# Random generation settings.
RANDOMIZE = True
SEED = None
NUMBER_OF_IMAGES = 3


# Generates a fractal image using the provided settings.
#
# Parameters:
# fractal_type: "mandelbrot" or "julia".
# center_x: Horizontal center on the complex plane.
# center_y: Vertical center on the complex plane.
# zoom: Magnification level.
# palette: Selected color palette.
# julia_c: Fixed complex constant for Julia generation.
# filename: Output image path.
def generate_fractal(
    fractal_type,
    center_x,
    center_y,
    zoom,
    palette,
    julia_c,
    filename=None,
    width=WIDTH,
    height=HEIGHT,
    max_iterations=MAX_ITERATIONS
):

    # Create a new RGB image.
    image = Image.new("RGB", (WIDTH, HEIGHT))

    # Access individual pixels.
    pixels = image.load()

    # Calculate the visible region.
    view_width = 3.5 / zoom
    view_height = view_width * HEIGHT / WIDTH

    # Iterate through every pixel.
    for x in range(WIDTH):
        for y in range(HEIGHT):

            # Convert pixel coordinates to complex coordinates.
            real = center_x + (x / WIDTH - 0.5) * view_width
            imaginary = center_y + (y / HEIGHT - 0.5) * view_height

            # Create the complex number for this pixel.
            point = complex(real, imaginary)

            # Select the appropriate fractal algorithm.
            if fractal_type == "mandelbrot":

                # Each pixel represents a different value of c.
                iterations = mandelbrot(
                    point,
                    MAX_ITERATIONS
                )

            elif fractal_type == "julia":

                # Each pixel represents the starting value of z.
                # The Julia constant remains fixed.
                iterations = julia(
                    point,
                    julia_c,
                    MAX_ITERATIONS
                )

            else:
                raise ValueError(
                    f"Unknown fractal type: {fractal_type}"
                )

            # Convert the iteration count into an RGB color.
            color = get_color(
                iterations,
                MAX_ITERATIONS,
                palette
            )

            # Assign the color to the pixel.
            pixels[x, y] = color

    # Save the generated image.
    # Save only when a filename is provided.
    if filename is not None:
        image.save(filename)

    # Return the image for use in the GUI.
    return image


# Controls the generation of multiple fractal images.
def main():

    # Create the output directory if necessary.
    os.makedirs("outputs", exist_ok=True)

    # Initialize the random number generator.
    rng = random.Random(SEED)

    # Generate the requested number of images.
    for i in range(NUMBER_OF_IMAGES):

        if RANDOMIZE:

            # Create an individual seed for this image.
            image_seed = rng.randrange(0, 2**32)

            # Generate random fractal settings.
            settings = randomize_settings(image_seed)

            fractal_type = settings["fractal_type"]
            center_x = settings["center_x"]
            center_y = settings["center_y"]
            zoom = settings["zoom"]
            palette = settings["palette"]
            julia_c = settings["julia_c"]

        else:

            # Use the manually configured settings.
            image_seed = None
            fractal_type = FRACTAL_TYPE
            center_x = CENTER_X
            center_y = CENTER_Y
            zoom = ZOOM
            palette = PALETTE
            julia_c = JULIA_C

        # Create a filename identifying the fractal type.
        filename = (
            f"outputs/{fractal_type}_{i + 1}.png"
        )

        # Generate the fractal image.
        generate_fractal(
            fractal_type,
            center_x,
            center_y,
            zoom,
            palette,
            julia_c,
            filename
        )

        # Display generation information.
        print(f"Generated: {filename}")
        print(f"Seed: {image_seed}")
        print(f"Type: {fractal_type}")
        print(f"Center: ({center_x}, {center_y})")
        print(f"Zoom: {zoom:.2f}")
        print(f"Palette: {palette}")

        # Display the Julia constant when applicable.
        if fractal_type == "julia":
            print(f"Julia constant: {julia_c}")

        print("-----------------------------")


# Run the generator when executed directly.
if __name__ == "__main__":
    main()
