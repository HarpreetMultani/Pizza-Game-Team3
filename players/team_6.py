# Standard Library Imports
import random  # For generating random numbers and choices

# Mathematical and Geometric Calculations
import math  # For mathematical operations like trigonometric functions
import numpy as np  # For numerical operations, array manipulations

# Statistical Analysis
from scipy import stats  # For statistical analysis and pattern recognition

# Optimization Algorithms
from scipy.optimize import minimize  # For optimizing pizza selection and cutting

# Additional Utilities
from collections import defaultdict  # For easier handling of data structures
from typing import List, Tuple, Dict  # For type annotations
from tokenize import String
import constants
from utils import pizza_calculations
from shapely.geometry import LineString, Point
import copy


class Player:
    def __init__(self, num_toppings, rng):
        self.num_toppings = num_toppings
        self.rng = rng
        self.pizza_radius = 6
        self.topping_radius = 0.375
        self.pizza_center = [0, 0]
        self.sequence = 0

    def customer_gen(self, num_cust, rng=None):
        def create_inst():
            # Generate preferences using the beta distribution
            alpha, beta = 2, 2  # You can adjust these parameters as needed
            p = np.random.beta(alpha, beta, self.num_toppings)

            # Scale and normalize preferences to sum to 12, and clamp between 0.1 and 11.9
            p = 11.8 * p / np.sum(p) + 0.1
            return p

        preferences_total = []
        rng = rng if rng is not None else self.rng

        for i in range(num_cust):
            preferences_1 = create_inst()
            preferences_2 = create_inst()

            preferences = [preferences_1, preferences_2]
            equal_prob = rng.random()
            if equal_prob <= 0.0:  # Change this if you want toppings to show up
                preferences = (np.ones((2, self.num_toppings)) * 12 / self.num_toppings).tolist()

            preferences_total.append(preferences)

        return preferences_total

    def choose_toppings(self, preferences):
        pizzas = np.zeros((10, 24, 3))  # 10 pizzas, 24 toppings each, 3 values per topping (x, y, type)

        pizza_radius = 3
        for j in range(constants.number_of_initial_pizzas):  # Iterate over each pizza
            pizza_indiv = np.zeros((24, 3))

            for i in range(24):  # Place 24 toppings on each pizza
                angle_increment = 2 * np.pi / 24
                angle = i * angle_increment

                # Calculate x, y coordinates
                x = pizza_radius * np.cos(angle)
                y = pizza_radius * np.sin(angle)

                # Assign topping type based on the number of toppings
                if self.num_toppings == 2:
                    topping_type = 1 if i < 12 else 2
                elif self.num_toppings == 3:
                    if i < 8:
                        topping_type = 1
                    elif i < 16:
                        topping_type = 2
                    else:
                        topping_type = 3
                else:  # self.num_toppings == 4
                    if i < 6:
                        topping_type = 1
                    elif i < 12:
                        topping_type = 2
                    elif i < 18:
                        topping_type = 3
                    else:
                        topping_type = 4

                pizza_indiv[i] = [x, y, topping_type]

            pizzas[j] = pizza_indiv

        return list(pizzas)

    def choose_and_cut(self, pizzas, remaining_pizza_ids, customer_amounts):
        best_score = -float('inf')
        best_pizza = None
        best_cut = None
        best_angle = None
        pizza_id = remaining_pizza_ids[0]
        current_pizza = pizzas[pizza_id]
        # Start with center and quadrants
        cut_points = [self.pizza_center] + self.get_quadrant_centers()
        self.sequence = 0

        while self.sequence < 6:
            print("Sequence: " + str(self.sequence))
            new_cut_points = []
            for point in cut_points:
                print(point)
                angle, score = self.find_optimal_cut_angle(current_pizza, point[0], point[1], customer_amounts)
                print(str(angle))
                if score > best_score:
                    best_score = score
                    best_cut = point
                    best_angle = angle
            # Generate new points around the current point for next sequence
            new_cut_points += self.generate_new_points_around(best_cut)
            cut_points = new_cut_points
            self.sequence += 1
            print("Best Cut: " + str(best_cut) + " Best Angle: " + str(best_angle))
        return pizza_id, best_cut, best_angle

    def get_quadrant_centers(self):
        radius = self.pizza_radius / 2  # Half the pizza radius to get quadrant centers
        return [
            [radius, radius],  # Top right quadrant
            [-radius, radius],  # Top left quadrant
            [-radius, -radius],  # Bottom left quadrant
            [radius, -radius]  # Bottom right quadrant
        ]

    def ratio_calculator(self, pizza, cut_1, num_toppings, multiplier, x, y):
        cut = copy.deepcopy(cut_1)
        result = np.zeros((2, num_toppings))
        cut[0] = (cut[0] - x) / multiplier
        cut[1] = -(cut[1] - y) / multiplier  # Because y axis is inverted in tkinter window
        center = [cut[0], cut[1]]
        theta = cut[2]

        topping_amts = [[0 for x in range(num_toppings)] for y in range(8)]
        for topping_i in pizza:
            top_abs_x = topping_i[0]
            top_abs_y = topping_i[1]
            distance_to_top = np.sqrt((top_abs_x - center[0]) ** 2 + (top_abs_y - center[1]) ** 2)
            theta_edge = np.arctan(0.375 / distance_to_top)

            if top_abs_x == center[0]:
                theta_top = 0
            else:
                theta_top = np.arctan((top_abs_y - center[1]) / (top_abs_x - center[0]))
            # print(theta, theta_edge, theta_distance, theta_top)
            if (top_abs_x - center[0]) <= 0 and (top_abs_y - center[1]) >= 0:
                theta_top = theta_top + np.pi
            if (top_abs_x - center[0]) <= 0 and (top_abs_y - center[1]) <= 0:
                theta_top = theta_top + np.pi
            topping_i[2] = int(topping_i[2])

            theta_distance = (theta_top - theta + (np.pi * 10)) % (2 * np.pi)

            if distance_to_top <= 0.375:  # Chosen center is withing pizza topping. Then by pizza theorem, 2 equal sized topping pieces
                result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + (np.pi * 0.375 * 0.375 / 2)
                result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + (np.pi * 0.375 * 0.375 / 2)

            elif (theta_edge + theta_distance) * 4 // np.pi == (-theta_edge + theta_distance) * 4 // np.pi:
                if (theta_distance * 4 // np.pi) % 2 == 0:
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + (np.pi * 0.375 * 0.375)
                else:
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + (np.pi * 0.375 * 0.375)
                topping_amts[int(theta_distance * 4 // np.pi)][int(topping_i[2]) - 1] = \
                topping_amts[int(theta_distance * 4 // np.pi)][int(topping_i[2]) - 1] + (np.pi * 0.375 * 0.375)

            elif (theta_edge + theta_distance) * 4 // np.pi == (
                    -theta_edge + theta_distance) * 4 // np.pi + 1:  # Topping falls in 2 slices
                if (theta_distance * 4 // np.pi) % 2 == 0:
                    small_angle_theta = min(theta_distance % (np.pi / 4), (np.pi / 4 - (theta_distance % (np.pi / 4))))
                    phi = np.arcsin(distance_to_top * np.sin(small_angle_theta) / 0.375)
                    area_smaller = (np.pi / 2 - phi - (np.cos(phi) * np.sin(phi))) * 0.375 * 0.375
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + (
                                np.pi * 0.375 * 0.375) - area_smaller
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + area_smaller
                else:
                    small_angle_theta = min(theta_distance % (np.pi / 4), (np.pi / 4 - (theta_distance % (np.pi / 4))))
                    phi = np.arcsin(distance_to_top * np.sin(small_angle_theta) / 0.375)
                    area_smaller = (np.pi / 2 - phi - (np.cos(phi) * np.sin(phi))) * 0.375 * 0.375
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + area_smaller
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + (
                                np.pi * 0.375 * 0.375) - area_smaller
                if small_angle_theta == theta_distance % (np.pi / 4):
                    topping_amts[int(theta_distance * 4 // np.pi)][int(topping_i[2]) - 1] = \
                    topping_amts[int(theta_distance * 4 // np.pi)][int(topping_i[2]) - 1] + (
                                np.pi * 0.375 * 0.375) - area_smaller
                    topping_amts[int(((theta_distance * 4 // np.pi) - 1) % 8)][int(topping_i[2]) - 1] = \
                    topping_amts[int(((theta_distance * 4 // np.pi) - 1) % 8)][int(topping_i[2]) - 1] + area_smaller
                else:
                    topping_amts[int(theta_distance * 4 // np.pi)][int(topping_i[2]) - 1] = \
                    topping_amts[int(theta_distance * 4 // np.pi)][int(topping_i[2]) - 1] + (
                                np.pi * 0.375 * 0.375) - area_smaller
                    topping_amts[int(((theta_distance * 4 // np.pi) + 1) % 8)][int(topping_i[2]) - 1] = \
                    topping_amts[int(((theta_distance * 4 // np.pi) + 1) % 8)][int(topping_i[2]) - 1] + area_smaller



            elif (theta_edge + theta_distance) * 4 // np.pi == (
                    -theta_edge + theta_distance) * 4 // np.pi + 2:  # Topping falls in 3 slices
                small_angle_theta_1 = theta_distance % (np.pi / 4)
                small_angle_theta_2 = (np.pi / 4) - small_angle_theta_1
                phi_1 = np.arcsin(distance_to_top * np.sin(small_angle_theta_1) / 0.375)
                phi_2 = np.arcsin(distance_to_top * np.sin(small_angle_theta_2) / 0.375)
                area_smaller_1 = (np.pi / 2 - phi_1 - (np.cos(phi_1) * np.sin(phi_1))) * 0.375 * 0.375
                area_smaller_2 = (np.pi / 2 - phi_2 - (np.cos(phi_2) * np.sin(phi_2))) * 0.375 * 0.375
                if (theta_distance * 4 // np.pi) % 2 == 0:
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + (
                                np.pi * 0.375 * 0.375) - area_smaller_1 - area_smaller_2
                    result[0][int(topping_i[2]) - 1] = result[0][
                                                           int(topping_i[2]) - 1] + area_smaller_1 + area_smaller_2
                else:
                    result[1][int(topping_i[2]) - 1] = result[1][
                                                           int(topping_i[2]) - 1] + area_smaller_1 + area_smaller_2
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + (
                                np.pi * 0.375 * 0.375) - area_smaller_1 - area_smaller_2
                topping_amts[int(theta_distance * 4 // np.pi)][int(topping_i[2]) - 1] = \
                topping_amts[int(theta_distance * 4 // np.pi)][int(topping_i[2]) - 1] + (
                            np.pi * 0.375 * 0.375) - area_smaller_1 - area_smaller_2
                topping_amts[int(((theta_distance * 4 // np.pi) + 1) % 8)][int(topping_i[2]) - 1] = \
                topping_amts[int(((theta_distance * 4 // np.pi) + 1) % 8)][int(topping_i[2]) - 1] + area_smaller_2
                topping_amts[int(((theta_distance * 4 // np.pi) - 1) % 8)][int(topping_i[2]) - 1] = \
                topping_amts[int(((theta_distance * 4 // np.pi) - 1) % 8)][int(topping_i[2]) - 1] + area_smaller_1


            else:  # just see the pattern from the above 2, draw some diagrams and you'll see how this came. Find areas of all small sectors, then minus accordingly later. This also takes care of the
                # above conditions. It's a general case, but let's have everything here because why not
                small_angle_theta = theta_distance % (np.pi / 4)
                small_areas_1 = []
                small_areas_2 = []
                while small_angle_theta < theta_edge:
                    phi = np.arcsin(distance_to_top * np.sin(small_angle_theta) / 0.375)
                    area_smaller = (np.pi / 2 - phi - (np.cos(phi) * np.sin(phi))) * 0.375 * 0.375
                    small_areas_1.append(area_smaller)
                    small_angle_theta = small_angle_theta + (np.pi / 4)
                for i in range(len(small_areas_1) - 1):
                    small_areas_1[i] = small_areas_1[i] - small_areas_1[i + 1]

                small_angle_theta = np.pi / 4 - (theta_distance % (np.pi / 4))
                while small_angle_theta < theta_edge:
                    phi = np.arcsin(distance_to_top * np.sin(small_angle_theta) / 0.375)
                    area_smaller = (np.pi / 2 - phi - (np.cos(phi) * np.sin(phi))) * 0.375 * 0.375
                    small_areas_2.append(area_smaller)
                    small_angle_theta = small_angle_theta + (np.pi / 4)
                for i in range(len(small_areas_2) - 1):
                    small_areas_2[i] = small_areas_2[i] - small_areas_2[i + 1]

                area_center = (np.pi * 0.375 * 0.375) - np.sum(small_areas_1) - np.sum(
                    small_areas_2)  # area of topping in slice where it's center lies.

                # To calculate the metric for slice areas
                topping_amts[int(theta_distance * 4 // np.pi)][int(topping_i[2]) - 1] = \
                topping_amts[int(theta_distance * 4 // np.pi)][int(topping_i[2]) - 1] + area_center
                for i in range(len(small_areas_1)):
                    topping_amts[int(((theta_distance * 4 // np.pi) - (i + 1)) % 8)][int(topping_i[2]) - 1] = \
                    topping_amts[int(((theta_distance * 4 // np.pi) - (i + 1)) % 8)][int(topping_i[2]) - 1] + \
                    small_areas_1[i]
                for i in range(len(small_areas_2)):
                    topping_amts[int(((theta_distance * 4 // np.pi) + (i + 1)) % 8)][int(topping_i[2]) - 1] = \
                    topping_amts[int(((theta_distance * 4 // np.pi) + (i + 1)) % 8)][int(topping_i[2]) - 1] + \
                    small_areas_2[i]

                for i in range(len(small_areas_1)):
                    if i % 2 == 1:
                        area_center = area_center + small_areas_1[i]

                for i in range(len(small_areas_2)):
                    if i % 2 == 1:
                        area_center = area_center + small_areas_2[i]
                if (theta_distance * 4 // np.pi) % 2 == 0:
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + area_center
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + (
                                np.pi * 0.375 * 0.375) - area_center
                else:
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + (
                                np.pi * 0.375 * 0.375) - area_center
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + area_center

        for i in range(num_toppings):
            result[0][i] = result[0][i] / (np.pi * 0.375 * 0.375)
            result[1][i] = result[1][i] / (np.pi * 0.375 * 0.375)
        return result, topping_amts
    def triangle_area(self, a, b, c):
        x1 = a[0]
        y1 = a[1]
        x2 = b[0]
        y2 = b[1]
        x3 = c[0]
        y3 = c[1]
        return (0.5 * abs((x1 * (y2 - y3)) + (x2 * (y3 - y1)) + (x3 * (y1 - y2))))

    def slice_area_calculator(self, cut_1, multiplier, x, y):
        center_x = (copy.deepcopy(cut_1[0]) - x) / multiplier
        center_y = -(copy.deepcopy(cut_1[1]) - y) / multiplier
        center = [center_x, center_y]
        theta1 = copy.deepcopy(cut_1[-1])
        circ_pts = [0, 0, 0, 0, 0, 0, 0, 0]
        ints_pts = [0, 0, 0, 0, 0, 0, 0, 0]
        area_slice = [0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(4):
            theta = theta1 + i * np.pi / 4
            dist_centers = math.sqrt((center[0]) ** 2 + (center[1]) ** 2)
            if center[0] == 0:
                angle_centerline = 0
            else:
                angle_centerline = math.atan((center[1]) / (center[0]))
            theta_diag = angle_centerline - theta
            sinin_1 = math.asin(math.sin(theta_diag) * dist_centers / 6)
            phi_1 = theta_diag - sinin_1
            phi_2 = theta_diag - math.pi + sinin_1
            if math.sin(theta_diag) == 0:
                point_1 = [6 * math.cos(angle_centerline), 6 * math.sin(angle_centerline)]
                point_2 = [-6 * math.cos(angle_centerline), -6 * math.sin(angle_centerline)]
            else:
                y1 = 6 * math.sin(phi_1) / math.sin(theta_diag)
                y2 = 6 * math.sin(phi_2) / math.sin(theta_diag)
                # point_1 = [center[0] - y1*math.sin(theta + angle_centerline) , center[1] - y1*math.cos(theta + angle_centerline)]
                # point_2 = [center[0] - y2*math.sin(theta + angle_centerline) , center[1] - y2*math.cos(theta + angle_centerline)]
                if center[0] < 0:
                    point_1 = [center[0] - y1 * math.cos(angle_centerline - theta_diag),
                               center[1] - y1 * math.sin(angle_centerline - theta_diag)]
                    point_2 = [center[0] - y2 * math.cos(angle_centerline - theta_diag),
                               center[1] - y2 * math.sin(angle_centerline - theta_diag)]
                else:
                    point_1 = [center[0] + y1 * math.cos(angle_centerline - theta_diag),
                               center[1] + y1 * math.sin(angle_centerline - theta_diag)]
                    point_2 = [center[0] + y2 * math.cos(angle_centerline - theta_diag),
                               center[1] + y2 * math.sin(angle_centerline - theta_diag)]
            circ_pts[i] = point_1
            circ_pts[i + 4] = point_2

        for i in range(8):
            line1 = LineString(Point(circ_pts[i]).coords[:] + Point(center).coords[:])
            line2 = LineString(Point(circ_pts[(i + 1) % 8]).coords[:] + Point([0, 0]).coords[:])
            line3 = LineString(Point(circ_pts[i]).coords[:] + Point([0, 0]).coords[:])
            line4 = LineString(Point(circ_pts[(i + 1) % 8]).coords[:] + Point(center).coords[:])
            int_pt_1 = line1.intersection(line2)
            int_pt_2 = line3.intersection(line4)
            if hasattr(int_pt_1, "x"):
                int_pt = [int_pt_1.x, int_pt_1.y]
                origin = [0, 0]
                area_1 = self.triangle_area(origin, int_pt, circ_pts[i])
                area_2 = self.triangle_area(center, circ_pts[(i + 1) % 8], int_pt)
                product_magnitudes = np.sqrt(circ_pts[i][0] ** 2 + circ_pts[i][1] ** 2) * np.sqrt(
                    circ_pts[(i + 1) % 8][0] ** 2 + circ_pts[(i + 1) % 8][1] ** 2)
                theta_sector = math.acos(
                    np.round(np.dot(circ_pts[i], circ_pts[(i + 1) % 8]), 4) / np.round(product_magnitudes, 4))
                area_sector = theta_sector * 36 / 2
                area_slice[i] = area_sector + area_2 - area_1
            elif hasattr(int_pt_2, "x"):
                int_pt = [int_pt_2.x, int_pt_2.y]
                area_1 = self.triangle_area([0, 0], int_pt, circ_pts[(i + 1) % 8])
                area_2 = self.triangle_area(center, int_pt, circ_pts[i])
                product_magnitudes = np.sqrt(circ_pts[i][0] ** 2 + circ_pts[i][1] ** 2) * np.sqrt(
                    circ_pts[(i + 1) % 8][0] ** 2 + circ_pts[(i + 1) % 8][1] ** 2)
                theta_sector = math.acos(
                    np.round(np.dot(circ_pts[i], circ_pts[(i + 1) % 8]), 4) / np.round(product_magnitudes, 4))
                area_sector = theta_sector * 36 / 2
                area_slice[i] = area_sector + area_2 - area_1
            else:
                area_1 = self.triangle_area([0, 0], center, circ_pts[(i + 1) % 8])
                area_2 = self.triangle_area(center, [0, 0], circ_pts[i])
                product_magnitudes = np.sqrt(circ_pts[i][0] ** 2 + circ_pts[i][1] ** 2) * np.sqrt(
                    circ_pts[(i + 1) % 8][0] ** 2 + circ_pts[(i + 1) % 8][1] ** 2)
                theta_sector = math.acos(
                    np.round(np.dot(circ_pts[i], circ_pts[(i + 1) % 8]), 4) / np.round(product_magnitudes, 4))
                area_sector = theta_sector * 36 / 2
                if theta_sector >= np.pi / 4:
                    area_slice[i] = area_sector + area_2 + area_1
                else:
                    area_slice[i] = area_sector - area_2 - area_1
        return area_slice
    def find_optimal_cut_angle(self, pizza, x, y, customer_amounts):
        best_angle = None
        best_score = -float('inf')

        # Assuming multiplier is a constant defined elsewhere in your code
        multiplier = 40 # Your multiplier value

        for angle in [i * math.pi / 36 for i in range(36)]:
            cut = [x, y, angle]
            B, C, _, _, _, _ = self.calculate_pizza_score(pizza, cut, customer_amounts, self.num_toppings, multiplier,
                                                          x, y)
            score = np.sum(B) - np.sum(C)  # Assuming we want to maximize the total improvement

            if score > best_score:
                best_score = score
                best_angle = angle

        return best_angle, best_score

    def calculate_pizza_score(self, pizza, pizza_cut, preferences, num_toppings, multiplier, x, y):
        # Calculate score for one pizza
        B = []
        C = []
        U = []
        obtained_preferences = []
        center_offset = []
        slice_amount_metric = []

        # Calculate the ratios, areas, and preferences
        obtained_pref, slice_areas_toppings = self.ratio_calculator(
            pizza, pizza_cut, num_toppings, multiplier, x, y)
        obtained_pref = np.array(obtained_pref)
        slice_areas = self.slice_area_calculator(pizza_cut, multiplier, x, y)

        # Random preference for U calculation
        random_pref, _ = self.ratio_calculator(pizza, [x, y, self.rng.random() * 2 * np.pi], num_toppings, multiplier, x, y)
        random_pref = np.array(random_pref)
        required_pref = np.array(preferences)
        uniform_pref = np.ones((2, num_toppings)) * (12 / num_toppings)

        # Calculate B, C, and U
        b = np.round(np.absolute(required_pref - uniform_pref), 3)
        c = np.round(np.absolute(obtained_pref - required_pref), 3)
        u = np.round(np.absolute(random_pref - uniform_pref), 3)
        B.append(b)
        C.append(c)
        U.append(u)
        obtained_preferences.append(tuple(np.round(obtained_pref, 3)))

        # Extra metrics
        x_offset = (pizza_cut[0] - x) / multiplier
        y_offset = (pizza_cut[1] - y) / multiplier
        center_offset.append(np.sqrt(x_offset ** 2 + y_offset ** 2))
        sum_1, sum_2, sum_metric = 0, 0, 0
        for j, area in enumerate(slice_areas):
            if j % 2 == 0:
                sum_2 += area
            else:
                sum_1 += area

        for k in range(num_toppings):
            for l, area_topping in enumerate(slice_areas_toppings):
                if l % 2 == 0:
                    sum_metric += abs((preferences[1][k] * slice_areas[l] / sum_2) - area_topping[k])
                else:
                    sum_metric += abs((preferences[0][k] * slice_areas[l] / sum_1) - area_topping[k])
        slice_amount_metric.append(sum_metric)

        return B, C, U, obtained_preferences, center_offset, slice_amount_metric

    def determine_slice(self, topping, cut_point, cut_angle):
        # Convert topping position to polar coordinates relative to the cut point
        dx = topping[0] - cut_point[0]
        dy = topping[1] - cut_point[1]
        angle = math.atan2(dy, dx)

        # Normalize angle to be between 0 and 2*pi
        angle = angle if angle >= 0 else (2 * math.pi + angle)

        # Determine the starting angle of each slice
        slice_angles = [(cut_angle + i * math.pi / 4) % (2 * math.pi) for i in range(8)]

        # Sort the slice angles and find which range the topping's angle falls into
        slice_angles.sort()
        for i in range(8):
            start_angle = slice_angles[i]
            end_angle = slice_angles[(i + 1) % 8]
            if start_angle < end_angle:
                if start_angle <= angle < end_angle:
                    return i
            else:  # Case where the slice crosses the 0 angle
                if start_angle <= angle or angle < end_angle:
                    return i

        # If for some reason it doesn't fall into any slice, return an error value
        return -1

    def generate_new_points_around(self, point):
        new_points = []
        delta = self.pizza_radius / (2 * (self.sequence + 1))  # Adjust the distance from the original point

        for dx in [-delta, 0, delta]:
            for dy in [-delta, 0, delta]:
                if dx != 0 or dy != 0:  # Exclude the original point
                    new_points.append([point[0] + dx, point[1] + dy])

        return new_points
