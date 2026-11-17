

# calculate the escape iteration count for a complex number
# this is done using the mandelbrot equation: z(n+1) = z(n)^2 + c
# 'c' is the complex number representing a point on the complex plane
# 'max_iterations' is the max number of iterations to perform
# the function returns the iteration at which the point escapes or max_iterations if it does not escape
def mandelbrot(c, max_iterations):
    z = 0

    # repeatedly apply the mandelbrot equation
    for i in range(max_iterations):
        z = z * z + c

        if abs(z) > 2:
            return i

    return max_iterations


def julia(z, c, max_iterations):

    for i in range(max_iterations):

        z = z * z + c

        if abs(z) > 2:
            return i

    return max_iterations