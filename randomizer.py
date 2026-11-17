import random
import math


# Interesting regions of the Mandelbrot set.
# Each tuple contains:
# (center_x, center_y, minimum_zoom, maximum_zoom)
# Known locations near interesting Mandelbrot boundaries.
# (center_x, center_y, min_zoom, max_zoom)
MANDELBROT_REGIONS = [
    (-0.7435, 0.1314, 100.0, 500.0),
    (-0.75, 0.1, 20.0, 100.0),
    (-1.25, 0.0, 10.0, 50.0),
    (-0.1, 0.9, 10.0, 50.0),
    (0.25, 0.0, 10.0, 50.0)
]


# Available color palettes.
PALETTES = [
    "rainbow",
    "fire",
    "ocean",
    "grayscale"
]


# Julia set constants known to produce interesting patterns.
JULIA_CONSTANTS = [
    complex(-0.7, 0.27015),
    complex(-0.8, 0.156),
    complex(0.285, 0.01),
    complex(-0.4, 0.6),
    complex(-0.70176, -0.3842)
]


# Generates randomized settings for either fractal type.
#
# Parameters:
# seed: Optional integer used for reproducible randomization.
#
# Returns:
# Dictionary containing the fractal type, position,
# zoom level, palette, and Julia constant.
def randomize_settings(seed=None):

    # Initialize a random number generator.
    rng = random.Random(seed)

    # Randomly choose between Mandelbrot and Julia generation.
    fractal_type = rng.choice(["mandelbrot", "julia"])

    # Select a random color palette.
    palette = rng.choice(PALETTES)

    if fractal_type == "mandelbrot":

        # Select a known interesting region.
        region = rng.choice(MANDELBROT_REGIONS)

        center_x, center_y, min_zoom, max_zoom = region

        # Randomly select the zoom level.
        zoom = math.exp(
            rng.uniform(math.log(min_zoom), math.log(max_zoom))
        )

        # Calculate the visible width and height.
        view_width = 3.5 / zoom
        view_height = view_width * 600 / 800

        # Apply small random offsets relative to the visible area.
        center_x += rng.uniform(
            -view_width * 0.1,
            view_width * 0.1
        )

        center_y += rng.uniform(
            -view_height * 0.1,
            view_height * 0.1
        )

        julia_c = None
    
    else:

        # Julia sets are initially displayed near the origin.
        center_x = 0.0
        center_y = 0.0

        # Randomly select a moderate zoom level.
        zoom = rng.uniform(1.0, 3.0)

        # Select a Julia constant controlling the shape.
        julia_c = rng.choice(JULIA_CONSTANTS)

    # Return all generated parameters.
    return {
        "fractal_type": fractal_type,
        "center_x": center_x,
        "center_y": center_y,
        "zoom": zoom,
        "palette": palette,
        "julia_c": julia_c
    }
