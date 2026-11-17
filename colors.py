import math

def get_color(iterations, max_iterations, palette):
    if iterations == max_iterations:
        return (0, 0, 0)

    t = iterations / max_iterations

    if palette == "rainbow":

        red = int(127.5 * (1 + math.sin(6 * math.pi * t)))
        green = int(127.5 * (1 + math.sin(6 * math.pi * t + 2)))
        blue = int(127.5 * (1 + math.sin(6 * math.pi * t + 4)))

    elif palette == "fire":

        red = min(255, int(255 * t * 3))
        green = min(255, int(255 * t * t * 3))
        blue = min(255, int(100 * t * t * t))

    elif palette == "ocean":

        red = int(30 * t)
        green = min(255, int(200 * t))
        blue = min(255, int(100 + 155 * t))

    elif palette == "grayscale":

        value = int(255 * t)

        red = value
        green = value
        blue = value

    else:
        return get_color(iterations, max_iterations, "rainbow")

    return (red, green, blue)