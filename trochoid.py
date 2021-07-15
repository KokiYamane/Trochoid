from solid import *
from solid.utils import *
from euclid3 import Point2
from solid.splines import catmull_rom_points
import numpy as np
import matplotlib.pyplot as plt


def epicycloid(theta, r_c, r_m, r_d=None):
    if r_d is None:
        r_d = r_m
    x = (r_c + r_m) * np.cos(theta) - r_d * np.cos((r_c + r_m) / r_m * theta)
    y = (r_c + r_m) * np.sin(theta) - r_d * np.sin((r_c + r_m) / r_m * theta)
    return x, y


def hypercycloid(theta, r_c, r_m, r_d=None):
    if r_d is None:
        r_d = r_m
    x = (r_c - r_m) * np.cos(theta) + r_d * np.cos(-(r_c - r_m) / r_m * theta)
    y = (r_c - r_m) * np.sin(theta) + r_d * np.sin(-(r_c - r_m) / r_m * theta)
    return x, y


def trochoid(theta, r, teeth):
    r_m = r / teeth / 2
    if theta % ((2 * np.pi) / teeth) < np.pi / teeth:
        return epicycloid(theta, r, r_m, r_m)
    else:
        return hypercycloid(theta, r, r_m, r_m)


def make_trochoid_gear(r, teeth):
    thetas = np.arange(0, 2 * np.pi, 2 * np.pi / 200)
    x_list, y_list = np.array([trochoid(theta, r, teeth)
                               for theta in thetas]).transpose()
    points = [Point2(x, y) for x, y in zip(x_list, y_list)]
    curve_points_closed = catmull_rom_points(points, close_loop=True)
    return linear_extrude(10)(polygon(curve_points_closed))


def make_trochoid_outer(r, teeth):
    thetas = np.arange(0, 2 * np.pi, 2 * np.pi / 200)
    x_list, y_list = np.array([trochoid(theta, r, teeth)
                               for theta in thetas]).transpose()
    points = [Point2(x, y) for x, y in zip(x_list, y_list)]
    curve_points_closed = catmull_rom_points(points, close_loop=True)
    outer = cylinder(r=r+10, h=10, segments=200)
    inner = translate([0, 0, -1])(
        linear_extrude(12)(
            polygon(curve_points_closed)
        ))
    return outer - hole()(inner)


def plot(outer_r, out_teeth):
    tooth_h = outer_r / (out_teeth * 2)
    inner_r = outer_r - (tooth_h * 2)

    thetas = np.arange(0, 2 * np.pi + 1, 2 * np.pi / 200)
    outer_x, outer_y = np.array([trochoid(theta, outer_r, out_teeth)
                                 for theta in thetas]).transpose()
    inner_x, inner_y = np.array([trochoid(theta, inner_r, out_teeth - 1)
                                 for theta in thetas]).transpose()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(outer_x, outer_y)
    plt.plot(inner_x + 2 * tooth_h, inner_y)
    ax.set_aspect('equal')
    plt.savefig('trochoid.png')


def make_model():
    outer_r = 20
    out_teeth = 7
    plot(outer_r, out_teeth)
    tooth_h = outer_r / (out_teeth * 2)
    inner_r = outer_r - (tooth_h * 2)

    inner = make_trochoid_gear(inner_r, out_teeth - 1)
    outer = make_trochoid_outer(outer_r, out_teeth)

    return translate([2*outer_r+20, 0, 0])(inner) + outer


if __name__ == '__main__':
    scad_render_to_file(
        make_model(),
        'output/output.scad',
        include_orig_code=False)
