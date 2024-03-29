#!/usr/bin/env python3
"""
Exercise 3
"""
from decimal import Decimal
from copy import deepcopy as dc
import sys
from time import perf_counter
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as si
from scipy.stats import qmc
import scipy.signal as ss

#################################
#  OPTION INITIATION FUNCTIONS  #
#################################

def run_option_a(global_vars: dict):
    """Execute part a

    :param global_vars: global variables

    """
    print(
        "-> Creating diffraction pattern for the following parameters:",
        f"\n\t-> Wavelength: {global_vars['wavelength']} m",
        f"\n\t-> Aperture width: {global_vars['aperture_width']} m",
        f"\n\t-> Screen distance: {global_vars['screen_distance']} m",
        f"\n\t-> Screen coordinates: {global_vars['screen_coords']} m",
        f"\n\t-> Points for Simpson's method: {global_vars['points_simpson']}",
    )
    input("* Press anything to continue...")
    x_vals = get_x_vals(
        global_vars["screen_coords"],
        global_vars["points_screen"],
    )
    intensity_simpson, intensity_quadrature, t_s_diff, t_q_diff = get_intensity(
        global_vars,
        x_vals,
        get_x_prime_vals(
            global_vars["aperture_width"],
            global_vars["points_simpson"],
        ),
        True,
        True,
    )
    plot_1d_diffraction_1(intensity_simpson, intensity_quadrature, x_vals)
    print(f"-> Time taken for Simpson's method: {t_s_diff} s.")
    print(f"-> Time taken for Quadrature's method: {t_q_diff} s.")
    input("* Press anything to return to menu...")


def run_option_b(global_vars: dict):
    """Execute part b

    :param global_vars: global variables

    """
    print(
        "-> Changing aperture width & calculating effects",
        "on maximum intensity & width of central maximum",
    )
    ap_widths, max_intensity, central_width = vary_aperture(global_vars)
    plot_far_field_effects(ap_widths, max_intensity, central_width, "aperture width")

    print(
        "-> Changing screen distance & calculating effects",
        "on maximum intensity & width of central maximum",
    )
    screen_distances, max_intensity, central_width = vary_screen_distance(global_vars)
    plot_far_field_effects(
        screen_distances, max_intensity, central_width, "screen distance"
    )

    global_vars["screen_coords"] = (-20e-3, 20e-3)
    global_vars["aperture_width"] = 2e-3
    global_vars["screen_distance"] = 3e-3
    global_vars["points_simpson"] = 401
    print(
        "-> Showing near-field effects",
        f"\n\t-> Screen size: {global_vars['screen_coords']} m",
        f"\n\t-> Aperture width: {global_vars['aperture_width']} m",
        f"\n\t-> Screen distance: {global_vars['screen_distance']} m",
        f"\n\t-> Sample size for Simpson's integration: {global_vars['points_simpson']}",
    )
    input("* Press anything to continue...")
    x_vals = get_x_vals(
        global_vars["screen_coords"],
        global_vars["points_screen"],
    )
    intensity_nf, _, _, _ = get_intensity(
        global_vars,
        x_vals,
        get_x_prime_vals(
            global_vars["aperture_width"],
            global_vars["points_simpson"],
        ),
        True,
        False,
    )
    plot_1d_diffraction_2(x_vals, intensity_nf)

    global_vars["screen_coords"] = (-30e-3, 30e-3)
    global_vars["aperture_width"] = 2e-5
    global_vars["screen_distance"] = 2e-2
    print(
        "-> Examine the effect of varying number of points for Simpson's method",
        "for far-field diffraction",
        f"\n\t-> Screen size: {global_vars['screen_coords']} m",
        f"\n\t-> Aperture width: {global_vars['aperture_width']} m",
        f"\n\t-> Screen distance: {global_vars['screen_distance']} m",
    )
    input("* Press anything to continue...")
    vary_plot_points(global_vars)

    global_vars["screen_coords"] = (-20e-3, 20e-3)
    global_vars["aperture_width"] = 2e-3
    global_vars["screen_distance"] = 3e-3
    print(
        "-> Examine the effect of varying number of points for Simpson's method",
        "for near-field diffraction",
        f"\n\t-> Screen size: {global_vars['screen_coords']} m",
        f"\n\t-> Aperture width: {global_vars['aperture_width']} m",
        f"\n\t-> Screen distance: {global_vars['screen_distance']} m",
    )
    input("* Press anything to continue...")
    vary_plot_points(global_vars)
    input("* Press anything to return to menu...")


def run_option_c(global_vars: dict):
    """Execute part c

    :param global_vars: global variables

    """
    print("-> Creating 2D diffraction patterns with a square/rectangular aperture")
    points = int(take_input_int("number of points (default: 50)") or "50")
    global_vars["points_screen"] = points
    global_vars["screen_coords"] = (-5e-5, 5e-5)
    global_vars["aperture_width"] = 2e-5
    distances = np.array([2.5, 5, 7.5, 10, 15, 20, 25, 30]) * 1e-5
    x_vals = get_x_vals(
        global_vars["screen_coords"],
        global_vars["points_screen"],
    )
    y_scale = float(
        take_input_general(
            "aperture y dimension relative to x dimension (default: 1 for square aperture)"
        )
        or "1"
    )
    y_vals = get_x_vals(
        (
            global_vars["screen_coords"][0] * y_scale,
            global_vars["screen_coords"][1] * y_scale,
        ),
        global_vars["points_screen"],
    )
    for val in distances:
        print(
            f"-> Generating plot for screen distance {round_with_decimal(6, val)} m..."
        )
        global_vars["screen_distance"] = val
        intensity = get_intensity_2d(
            global_vars,
            x_vals,
            y_vals,
            lambda y: -global_vars["aperture_width"] / 2,
            lambda y: global_vars["aperture_width"] / 2,
        )
        plot_2d_diffraction(global_vars, intensity)
    input("* Press anything to return to menu...")


def run_option_d(global_vars: dict):
    """Execute option d

    :param global_vars: global variables

    """
    print("-> Creating 2D diffraction patterns with a circular aperture")
    points = int(take_input_int("number of points (default: 50)") or "50")
    global_vars["points_screen"] = points
    global_vars["screen_coords"] = (-5e-5, 5e-5)
    global_vars["aperture_width"] = 2e-5
    distances = np.array([2.5, 5, 7.5, 10, 15, 20, 25, 30]) * 1e-5
    x_vals = get_x_vals(
        global_vars["screen_coords"],
        global_vars["points_screen"],
    )
    y_vals = get_x_vals(
        global_vars["screen_coords"],
        global_vars["points_screen"],
    )
    for val in distances:
        print(
            f"-> Generating plot for screen distance {round_with_decimal(6, val)} m..."
        )
        global_vars["screen_distance"] = val
        intensity = get_intensity_2d(
            global_vars,
            x_vals,
            y_vals,
            lambda y: -np.sqrt((global_vars["aperture_width"] / 2) ** 2 - y**2),
            lambda y: np.sqrt((global_vars["aperture_width"] / 2) ** 2 - y**2),
        )
        plot_2d_diffraction(global_vars, intensity)
    input("* Press anything to return to menu...")


def run_option_e(global_vars: dict):
    """Execute option e

    :param global_vars: global variables

    """
    print("-> Evaluating the area of a circle using the Monte Carlo method.")
    radius = float(take_input_general("circle radius (default: 1)") or "1")
    sample_size = int(take_input_int("sample size (default: 500000)") or "500000")
    global_vars["mc_sample_size"] = sample_size
    min_size = [-radius, -radius]
    max_size = [radius, radius]
    sample = np.random.uniform(
        low=min_size, high=max_size, size=(global_vars["mc_sample_size"], 2)
    )
    input("* Press anything to continue...")
    result, error = evaluate_monte(sample, radius, dimension=2)
    print(
        f"-> For N={global_vars['mc_sample_size']}, the area is:",
        result,
        "with error:",
        error,
    )
    input("* Press anything to return to menu...")


def run_option_f(global_vars: dict):
    """Execute option f

    :param global_vars: global variables

    """
    print(
        "-> Investigating the effect of the number of samples on the area",
        "of a unit circle using the Monte Carlo method.",
    )
    sample_size = int(take_input_int("max sample size (default: 100000)") or "100000")
    global_vars["mc_sample_size"] = sample_size
    step = int(take_input_int("step (default: 100)") or "100")
    radius = 1
    min_size, max_size = -radius, radius
    sample_sizes = np.arange(50, global_vars["mc_sample_size"], step)
    errors, results = np.zeros_like(sample_sizes, dtype=np.float_), np.zeros_like(
        sample_sizes, dtype=np.float_
    )
    input("* Press anything to continue...")
    for idx, sample_size_var in enumerate(sample_sizes):
        sample = np.random.uniform(
            low=min_size, high=max_size, size=(sample_size_var, 2)
        )
        results[idx], errors[idx] = evaluate_monte(sample, radius, dimension=2)
    plot_monte_carlo(errors, results, sample_sizes, np.pi, dimension=2)
    input("* Press anything to return to menu...")


def run_option_g(global_vars: dict):
    """Execute option g

    :param global_vars: global variables

    """

    def evaluate_volumes(
        prev_prev_volume: float, radius: float, dimension: int
    ) -> float:
        return 2 * np.pi * radius**2 / dimension * prev_prev_volume

    radius = 1
    min_size, max_size = -radius, radius
    sample_size = int(take_input_int("max sample size (default: 100000)") or "100000")
    global_vars["mc_sample_size"] = sample_size
    step = int(take_input_int("step (default: 100)") or "100")
    sample_sizes = np.arange(50, global_vars["mc_sample_size"], step)
    dimensions = np.arange(2, 50, 1, dtype=np.int_)
    volumes = np.zeros_like(dimensions, dtype=np.float_)
    volumes[0] = np.pi * radius**2
    volumes[1] = 4 * np.pi * radius**3 / 3
    for idx, dimension_val in enumerate(dimensions):
        errors, results = np.zeros_like(sample_sizes, dtype=np.float_), np.zeros_like(
            sample_sizes, dtype=np.float_
        )
        volumes[idx] = volumes[idx] * (dimension_val in [2, 3]) + evaluate_volumes(
            volumes[idx - 2], radius, dimension_val
        ) * (dimension_val not in [2, 3])
        if dimension_val <= 10:
            print(f"-> Generating plot for hypersphere dimension {dimension_val}...")
            for idx2, sample_size_var in enumerate(sample_sizes):
                sample = np.random.uniform(
                    low=min_size, high=max_size, size=(sample_size_var, dimension_val)
                )
                results[idx2], errors[idx2] = evaluate_monte(
                    sample, radius, dimension_val
                )
            plot_monte_carlo(errors, results, sample_sizes, volumes[idx], dimension_val)
    print("-> Showing volume of hypersphere as a function of number of dimension")
    input("* Press anything to continue...")
    plt.scatter(dimensions, volumes, c="k", marker="x")
    plt.xlabel("Number of dimensions")
    plt.ylabel("Volume of hypersphere (arbitrary)")
    plt.show()
    input("* Press anything to return to menu...")


def run_option_h():
    """Execute option h: an extra part
    Compare pseudorandom MC with quasirandom MC using low-discrepancy Sobol sequence
    as the sampler for random numbers.
    """
    print(
        "-> Testing the convergence of Numpy pseudorandom sequence RNG versus Scipy Sobol low-discrepancy sequence RNG"
    )
    sample_size_pseudo = np.repeat(
        np.array([2**n for n in range(5, 12)], dtype=np.int_), 5000
    )
    sample_size_quasi = np.repeat(np.arange(4, 11, 1, dtype=np.int_), 5000)
    radius = 1
    min_size, max_size = -radius, radius
    results_quasi, results_pseudo = np.zeros_like(
        sample_size_pseudo, dtype=np.float_
    ), np.zeros_like(sample_size_pseudo, dtype=np.float_)
    input("* Press anything to continue...")
    for idx, sample_size_var in enumerate(sample_size_pseudo):
        sample = np.random.uniform(
            low=min_size, high=max_size, size=(sample_size_var, 2)
        )
        results_pseudo[idx], _ = evaluate_monte(sample, radius, dimension=2)
    for idx, sample_size_var in enumerate(sample_size_quasi):
        sampler = qmc.Sobol(d=2, scramble=True)
        sample = sampler.random_base2(m=sample_size_var)
        qmc.scale(sample, -1, 1)
        results_quasi[idx], _ = evaluate_monte(sample, radius, dimension=2)
    plot_compare_pseudo_quasi(results_pseudo, results_quasi, sample_size_pseudo, np.pi)
    input("* Press anything to return to menu...")


##############################
#  PROBLEM 1 MAIN FUNCTIONS  #
##############################


def vary_plot_points(global_vars: dict):
    """Vary points for Simpson's method & observe effects with plots

    :param global_vars: global variables

    """
    points = [3, 7, 11, 31, 51, 101, 201, 301, 401]
    x_vals = get_x_vals(
        global_vars["screen_coords"],
        global_vars["points_screen"],
    )
    for point in points:
        x_prime_vals = get_x_prime_vals(
            global_vars["aperture_width"],
            point,
        )
        intensity_simpson, _, _, _ = get_intensity(
            global_vars,
            x_vals,
            x_prime_vals,
            True,
            False,
        )
        plt.scatter(x_vals, intensity_simpson, s=1, label=point)
    plt.legend(
        markerscale=4.0,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.05),
        ncol=6,
        fancybox=True,
    )
    plt.xlabel("Screen coordinate (m)")
    plt.ylabel("Intensity (arbitrary)")
    plt.show()
    plt.clf()
    plt.cla()
    plt.close()


def vary_aperture(global_vars: dict) -> tuple:
    """Vary aperture width & investigate effects

    :param global_vars: global variables

    """
    points = int(take_input_int("number of points (default: 50)") or "50")
    input("* Press anything to continue...")
    ap_widths = np.linspace(1e-5, 4e-5, points)
    x_vals = get_x_vals(
        global_vars["screen_coords"],
        global_vars["points_screen"],
    )
    max_intensity, central_width = np.zeros_like(ap_widths), np.zeros_like(ap_widths)
    for idx, ap_val in enumerate(ap_widths):
        intensity_simpson, _, _, _ = get_intensity(
            global_vars,
            x_vals,
            get_x_prime_vals(
                ap_val,
                global_vars["points_simpson"],
            ),
            True,
            False,
        )
        max_intensity[idx] = np.max(intensity_simpson)
        central_width[idx] = (
            2
            * x_vals[
                global_vars["points_screen"] // 2
                - 1
                + ss.argrelextrema(
                    intensity_simpson[global_vars["points_screen"] // 2 :], np.less
                )[0][0]
            ]
        )
    return ap_widths, max_intensity, central_width


def vary_screen_distance(global_vars: dict) -> tuple:
    """Vary screen distance & observe effects

    :global_vars: global variables

    """
    points = int(take_input_int("number of points (default: 50)") or "50")
    input("* Press anything to continue...")
    screen_distances = np.linspace(5e-3, 9e-2, points)
    x_vals = get_x_vals(
        global_vars["screen_coords"],
        global_vars["points_screen"],
    )
    x_prime_vals = get_x_prime_vals(
        global_vars["aperture_width"],
        global_vars["points_simpson"],
    )
    max_intensity, central_width = np.zeros_like(screen_distances), np.zeros_like(
        screen_distances
    )
    for idx, dist_val in enumerate(screen_distances):
        global_vars["screen_distance"] = dist_val
        intensity_simpson, _, _, _ = get_intensity(
            global_vars,
            x_vals,
            x_prime_vals,
            True,
            False,
        )
        max_intensity[idx] = np.max(intensity_simpson)
        central_width[idx] = (
            2
            * x_vals[
                global_vars["points_screen"] // 2
                - 1
                + ss.argrelextrema(
                    intensity_simpson[global_vars["points_screen"] // 2 :], np.less
                )[0][0]
            ]
        )
    return screen_distances, max_intensity, central_width


def get_intensity(
    global_vars: dict,
    x_vals: np.ndarray,
    x_prime_vals: np.ndarray,
    is_simp: bool,
    is_quad: bool,
) -> tuple:
    """Get the intensity for 1d aperture using either method

    :param global_vars: global variables
    :param x_vals: screen coordinates
    :param x_prime_vals: aperture coordinates
    :param is_simp: boolean to execute Simpsons' method
    :param is_quad: boolean to execute Quad method
    :returns: tuple of two ndarray (simp,quad)

    """
    e_field_vals_simpson, e_field_vals_quadrature = np.zeros_like(
        x_vals, dtype=np.complex_
    ), np.zeros_like(x_vals, dtype=np.complex_)
    intensity_simpson, intensity_quadrature = np.zeros_like(x_vals), np.zeros_like(
        x_vals
    )
    t_s_diff, t_q_diff = 0, 0
    if is_simp:
        t_s_i = perf_counter()
        for idx, x_val in enumerate(x_vals):
            e_field_vals_simpson[idx] = integrate_diffraction_simpson(
                global_vars, x_val, x_prime_vals
            )
        t_s_f = perf_counter()
        t_s_diff = t_s_f - t_s_i
        intensity_simpson = calculate_intensity(global_vars, e_field_vals_simpson)
    if is_quad:
        t_q_i = perf_counter()
        for idx, x_val in enumerate(x_vals):
            e_field_vals_quadrature[idx] = integrate_diffraction_quadrature(
                global_vars,
                x_val,
                -global_vars["aperture_width"] / 2,
                global_vars["aperture_width"] / 2,
            )
        t_q_f = perf_counter()
        t_q_diff = t_q_f - t_q_i
        intensity_quadrature = calculate_intensity(global_vars, e_field_vals_quadrature)
    return intensity_simpson, intensity_quadrature, t_s_diff, t_q_diff


def get_intensity_2d(
    global_vars: dict,
    x_vals: np.ndarray,
    y_vals: np.ndarray,
    x_lower_bound,
    x_upper_bound,
) -> np.ndarray:
    """Get intensity for 2 dimensional aperture using dblquad

    :param global_vars: global variables
    :param x_vals: screen coordinates in x
    :param y_vals: screen coordinates in y
    :param x_lower_bound: lower bound in x
    :param x_upper_bound: upper bound in x
    :returns: 2d intensity array

    """
    e_field_vals_quadrature_2d = np.zeros(
        (np.size(x_vals), np.size(y_vals)), dtype=np.complex_
    )
    for idx, x_val in enumerate(x_vals):
        for idx2, y_val in enumerate(y_vals):
            e_field_vals_quadrature_2d[idx, idx2] = integrate_diffraction_dblquad(
                global_vars,
                x_val,
                y_val,
                x_lower_bound,
                x_upper_bound,
                (-global_vars["aperture_width"] / 2, global_vars["aperture_width"] / 2),
            )
    return calculate_intensity(global_vars, e_field_vals_quadrature_2d)


def get_x_vals(screen_coordinates: tuple, points: int) -> np.ndarray:
    """Get screen coordinates

    :param screen_coordinates: location on screen
    :param points: number of points for screen coordinate
    :returns: array of screen coordinates

    """
    return np.linspace(screen_coordinates[0], screen_coordinates[1], points)


def get_x_prime_vals(aperture_width: float, points: int) -> np.ndarray:
    """Get aperture coordinates

    :param aperture_width: width of aperture
    :param points: number of simpson points
    :returns: an array for aperture coordinates

    """
    return np.linspace(-aperture_width / 2, aperture_width / 2, points)


def integrate_diffraction_simpson(
    global_vars: dict, x_val: float, x_prime_vals: np.ndarray
) -> np.complex128:
    """
    Use Simpson's method to find the electric field at a given x coordinate
    on the screen. Takes two model arrays and gives the area.

    :param global_vars: global variables
    :param x_val: current x coordinate
    :param x_prime_vals: aperture coordinates
    :returns: a complex value of electric field at x

    """
    integrand = np.exp(
        1j
        * np.pi
        * (x_val - x_prime_vals) ** 2
        / (global_vars["wavelength"] * global_vars["screen_distance"])
    )
    return (global_vars["E0"] * si.simpson(integrand, x_prime_vals)) / (
        global_vars["wavelength"] * global_vars["screen_distance"]
    )


def integrate_diffraction_quadrature(
    global_vars: dict, x_val: float, lower_bound: float, upper_bound: float
) -> np.complex128:
    """Use the quadrature method to integrate for the electric field at x

    :param global_vars: global variables
    :param x_val: coordinate on screen
    :param lower_bound: one end of the aperture
    :param upper_bound: the other end of the aperture
    :returns: the electric field value at x

    """

    def real_integrand(x):
        return np.cos(
            np.pi
            * (x_val - x) ** 2
            / (global_vars["wavelength"] * global_vars["screen_distance"])
        )

    def imaginary_integrand(x):
        return np.sin(
            np.pi
            * (x_val - x) ** 2
            / (global_vars["wavelength"] * global_vars["screen_distance"])
        )

    real_integral, _ = si.quad(real_integrand, lower_bound, upper_bound)
    imaginary_integral, _ = si.quad(imaginary_integrand, lower_bound, upper_bound)
    return (
        global_vars["E0"] / (global_vars["wavelength"] * global_vars["screen_distance"])
    ) * (real_integral + 1j * imaginary_integral)


def integrate_diffraction_dblquad(
    global_vars: dict,
    x_val: float,
    y_val: float,
    x_bound_lower,
    x_bound_upper,
    y_bound: tuple,
) -> np.complex128:
    """Perform double integration using dblquad

    :param global_vars: global variables
    :param x_val: screen coordinates in x
    :param y_val: screen coordinates in y
    :param x_bound_lower: lower x bound (function or float)
    :param x_bound_upper: upper x bound (function or float)
    :param y_bound: y bounds as a tuple
    :returns: the electric field value at (x_val,y_val)

    """

    def real_integrand(x, y):
        return np.cos(
            np.pi
            * ((x_val - x) ** 2 + (y_val - y) ** 2)
            / (global_vars["wavelength"] * global_vars["screen_distance"])
        )

    def imaginary_integrand(x, y):
        return np.sin(
            np.pi
            * ((x_val - x) ** 2 + (y_val - y) ** 2)
            / (global_vars["wavelength"] * global_vars["screen_distance"])
        )

    real_integral = si.dblquad(
        real_integrand,
        y_bound[0],
        y_bound[1],
        x_bound_lower,
        x_bound_upper,
        epsrel=1e-12,
        epsabs=1e-12,
    )
    imaginary_integral = si.dblquad(
        imaginary_integrand, y_bound[0], y_bound[1], x_bound_lower, x_bound_upper
    )
    return (
        global_vars["E0"] / (global_vars["wavelength"] * global_vars["screen_distance"])
    ) * (real_integral[0] + 1j * imaginary_integral[0])


def calculate_intensity(global_vars: dict, e_field_vals: np.ndarray) -> np.ndarray:
    """Return the intensity given the electric field value

    :param global_vars: global variables
    :param e_field_val: complex electric field value
    :returns: intensity as a real float

    """
    return np.real(
        (
            global_vars["c"]
            * global_vars["epsilon_0"]
            * e_field_vals
            * np.conjugate(e_field_vals)
        )
    )


##############################
#  PROBLEM 2 MAIN FUNCTIONS  #
##############################


def evaluate_monte(sample: np.ndarray, radius: float, dimension: int) -> tuple:
    """Evaluate multidimensional equations using the Monte Carlo method

    :param sample: the sample array (random numbers)
    :param radius: radius of hypersphere
    :param dimension: dimension of hypersphere

    :returns: a tuple of result and error

    """

    def pythag_function(sample, radius):
        return np.sum(sample**2, axis=1) <= radius

    func = pythag_function(sample, radius).astype(int)
    integral = ((2 * radius) ** dimension) * np.mean(func)
    error = ((2 * radius) ** dimension) * np.std(func) / np.sqrt(np.size(sample))
    return integral, error


######################
#  HELPER FUNCTIONS  #
######################


def take_input_int(var_name: str) -> int | str:
    """Take in a value as an input with error catching. These should be integers
    Except in the case where the input is empty, then use default value implemented in the mother
    function

    :param var_name: a string name for variable

    :returns: a positive integer

    """
    input_var = input(f"+ Enter a value for {var_name}: ")
    while True:
        if input_var == "":
            return input_var
        try:
            var = int(input_var)
            # assert var > 0
            break
        except Exception:
            input_var = input(f"! Please enter a valid value for {var_name}: ")
    return var


def take_input_complex(var_name: str) -> complex | str:
    """Take in a value as an input with error catching These should be complex
    Except in the case where the input is empty, then use default value implemented in the mother
    function

    :param var_name: a string name for variable
    :returns: the inputted variable

    """
    input_var = input(f"+ Enter a value for {var_name}: ")
    while True:
        if input_var == "":
            return input_var
        try:
            var = complex(input_var)
            break
        except ValueError:
            input_var = input(f"! Please enter a valid value for {var_name}: ")
    return var


def take_input_general(var_name: str) -> float | str:
    """Take in a value as an input with error catching These should be floating point numbers
    Except in the case where the input is empty, then use default value implemented in the mother
    function

    :param var_name: a string name for variable
    :returns: the inputted variable

    """
    input_var = input(f"+ Enter a value for {var_name}: ")
    while True:
        if input_var == "":
            return input_var
        try:
            var = float(input_var)
            break
        except ValueError:
            input_var = input(f"! Please enter a valid value for {var_name}: ")
    return var


def round_with_decimal(decimal_places: int, value: float) -> float:
    """Round a float to the nearest dp provided without precision error
    using quantize() from Decimal class

    :param dp: number of decimal places
    :param value: the float to round
    :returns: the answer as a float

    """
    reference = "1." + "0" * decimal_places
    return float(Decimal(str(value)).quantize(Decimal(reference)))


def map_float_to_index(value: float, step: float, start: float) -> int:
    """Given the value convert it to an index

    :param value: the original value
    :param step: the stepsize
    :returns: the index

    """
    return int(round_with_decimal(0, (value - start) / step))


########################
#  PLOTTING FUNCTIONS  #
########################


def plot_1d_diffraction_1(
    intensity_simpson: np.ndarray, intensity_quadrature: np.ndarray, x_vals: np.ndarray
):
    """Plot intensity vs screen coordinate for 2 methods

    :param intensity_simpson: intensity array from simpsons method
    :param intensity_quadrature: intensity array from quadrature method
    :param x_vals: screen coordinate array

    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("1D Fresnel diffraction")
    ax1.set(
        xlabel="Screen coordinate (m)",
        ylabel="Intensity (arbitrary)",
        title="Simpson's method",
    )
    ax2.set(
        xlabel="Screen coordinate (m)",
        ylabel="Intensity (arbitrary)",
        title="Quadrature method",
    )
    ax1.scatter(x_vals, intensity_simpson, s=2, c="k")
    ax2.scatter(x_vals, intensity_quadrature, s=2, c="k")
    plt.show()
    plt.clf()
    plt.cla()
    plt.close()


def plot_1d_diffraction_2(x_vals: np.ndarray, intensity: np.ndarray):
    """Plot intensity vs screen coordinate for 1 methods

    :param x_vals: x screen coordinates
    :param intensity: intensity array

    """
    plt.xlabel("Screen coordinate (m)")
    plt.ylabel("Intensity (arbitrary)")
    plt.scatter(x_vals, intensity, s=2, c="k")
    plt.show()
    plt.clf()
    plt.cla()
    plt.close()


def plot_far_field_effects(
    variable: np.ndarray,
    max_intensity: np.ndarray,
    central_width: np.ndarray,
    variable_name: str,
):
    """Plot variable vs maximum intensity and central width

    :param variable: the variable to plot on x-axis
    :param max_intensity: maximum intensity array
    :param central_width: centra width array
    :param variable_name: string of variable name

    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle(f"Effects of changing {variable_name}")
    log_var = np.log(variable)
    log_i = np.log(max_intensity)
    log_w = np.log(central_width)
    i_slope, _ = np.polyfit(log_var, log_i, 1)
    w_slope, _ = np.polyfit(log_var, log_w, 1)
    ax1.scatter(np.log(variable), np.log(max_intensity), s=2, c="r")
    ax1.set(
        xlabel=f"log({variable_name.capitalize()})",
        ylabel="log(Intensity (arbitrary))",
        title=f"Peak intensity of central maxima, slope {i_slope}",
    )
    ax2.scatter(np.log(variable), np.log(central_width), s=2, c="b")
    ax2.set(
        xlabel=f"log({variable_name.capitalize()})",
        ylabel="log(Central peak width)",
        title=f"Width of central maxima, slope {w_slope}",
    )
    plt.show()
    plt.clf()
    plt.cla()
    plt.close()


def plot_2d_diffraction(global_vars: dict, intensity: np.ndarray):
    """Plot 2d diffraction patterns in x,y

    :param global_vars: global variables
    :param intensity: intensity array

    """
    plt.imshow(intensity)
    plt.ylabel("Relative screen coordinate (vertical)")
    plt.xlabel("Relative screen coordinate (horizontal)")
    plt.title(
        f"Screen distance = {round_with_decimal(6,float(global_vars['screen_distance']))} m; Aperture width = {global_vars['aperture_width']} m"
    )
    plt.show()
    plt.clf()
    plt.cla()
    plt.close()


def plot_monte_carlo(
    errors: np.ndarray,
    results: np.ndarray,
    sample_sizes: np.ndarray,
    real_value: float,
    dimension: int,
):
    """Plot errors & results vs number of samples. For error plotting,
    the log is taken for both axes, but due to some values being 0,
    those are taken out.

    :param errors: errors array
    :param results: results array
    :param sample_sizes: sample array
    :param real_value: expected volume of hypersphere
    :param dimension: hypersphere dimension

    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle(
        f"The effect of the number of samples on results of the Monte Carlo method ({dimension}D)."
    )
    ax1.set(
        xlabel="Number of samples",
        ylabel="Volume of hypersphere (arbitrary)",
        title="Convergence of results",
    )
    ax1.scatter(sample_sizes, results, s=2, c="r")
    ax1.plot(
        sample_sizes,
        np.full_like(sample_sizes, real_value, dtype=np.float_),
        c="k",
        alpha=0.5,
    )
    sample_sizes = np.where(errors <= sys.float_info.epsilon, 0, sample_sizes)
    sample_sizes = np.where(sample_sizes <= sys.float_info.epsilon, 0, sample_sizes)
    errors = np.where(sample_sizes <= sys.float_info.epsilon, 0, errors)
    errors = np.where(errors <= sys.float_info.epsilon, 0, errors)
    log_sample, log_errors = np.log(sample_sizes[sample_sizes != 0]), np.log(
        errors[errors != 0]
    )
    slope, _ = np.polyfit(log_sample, log_errors, 1)
    ax2.set(
        xlabel="log(Number of samples)",
        ylabel="log(Error) (arbitrary)",
        title=f"Improvement of errors, slope {slope}",
    )
    ax2.scatter(log_sample, log_errors, s=2, c="b")
    plt.show()
    plt.clf()
    plt.cla()
    plt.close()


def plot_compare_pseudo_quasi(
    results_pseudo: np.ndarray,
    results_quasi: np.ndarray,
    sample_sizes: np.ndarray,
    real_value: float,
):
    """Plot errors & results vs number of samples. For error plotting,
    the log is taken for both axes, but due to some values being 0,
    those are taken out.

    :param errors: errors array
    :param results: results array
    :param sample_sizes: sample array
    :param real_value: expected volume of hypersphere
    :param dimension: hypersphere dimension

    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle(
        f"Comparison between convergence Pseudo-Monte Carlo and Quasi-Monte Carlo."
    )
    ax1.set(
        xlabel="Number of samples",
        ylabel="Area of circle (arbitrary)",
        title="Convergence of results for Pseudo method",
    )
    ax1.scatter(sample_sizes, results_pseudo, s=2, c="r")
    ax1.plot(
        sample_sizes,
        np.full_like(sample_sizes, real_value, dtype=np.float_),
        c="k",
        alpha=0.5,
    )
    ax2.set(
        xlabel="Number of samples",
        ylabel="Area of circle (arbitrary)",
        title="Convergence of results for Quasi method",
    )
    ax2.scatter(sample_sizes, results_quasi, s=2, c="r")
    ax2.plot(
        sample_sizes,
        np.full_like(sample_sizes, real_value, dtype=np.float_),
        c="k",
        alpha=0.5,
    )
    plt.show()
    plt.clf()
    plt.cla()
    plt.close()


def main():
    """Driver code"""
    user_input = "0"
    global_vars = {
        "wavelength": 1e-6,
        "aperture_width": 2e-5,
        "screen_distance": 2e-2,
        "screen_coords": (-5e-3, 5e-3),
        "points_simpson": 101,
        "points_screen": 5000,
        "E0": 1,
        "c": 3e8,
        "epsilon_0": 8.85e-12,
        "mc_sample_size": 500000,
    }
    # plt.rcParams.update({"font.size": 20})  # Uncomment for bigger plot fonts (for report only)
    while user_input != "q":
        print(
            "---------------------------------------------------------"
            "\n(a) 1D diffraction: compare Simpsons & quadrature",
            "\n(b) 1D diffraction: explore parameters & near-field",
            "\n(c) 2D diffraction: square/rectangular aperture",
            "\n(d) 2D diffraction: circular aperture",
            "\n(e) Monte Carlo: estimate pi & error",
            "\n(f) Monte Carlo: results & errors vs N (2D)",
            "\n(g) Monte Carlo results & errors vs N (2D-10D)",
            "\n(h) Pseudorandom vs quasirandom Monte Carlo (extension)",
            "\n---------------------------------------------------------",
        )
        user_input = input(
            '+ Enter a choice, "a", "b", "c", "d", "e", "f", "g", "h", or "q" to quit: '
        )
        print("-> You entered the choice:", user_input)
        if user_input == "a":
            run_option_a(dc(global_vars))
        elif user_input == "b":
            run_option_b(dc(global_vars))
        elif user_input == "c":
            run_option_c(dc(global_vars))
        elif user_input == "d":
            run_option_d(dc(global_vars))
        elif user_input == "e":
            run_option_e(dc(global_vars))
        elif user_input == "f":
            run_option_f(dc(global_vars))
        elif user_input == "g":
            run_option_g(dc(global_vars))
        elif user_input == "h":
            run_option_h()
        elif user_input != "q":
            print("! This is not a valid choice.")
    print("-> You have chosen to finish - goodbye.")

if __name__ == "__main__":
    main()
