import constants
from tokenize import String
from typing import Tuple, List
from utils import pizza_calculations

import numpy as np
from itertools import permutations
from math import pi, sin, cos, tan, sqrt
from scipy.optimize import shgo, direct, dual_annealing, differential_evolution, brute


class Player:
    def __init__(self, num_toppings, rng: np.random.Generator) -> None:
        """Initialise the player"""
        self.rng = rng
        self.num_toppings = num_toppings
        self.BUFFER = 0.001
        self.N4_RADIUS_BUFFER = 0.4  # TODO: Make min radius calculation more sophisticated so this isn't needed
        self.NUM_BRUTE_SAMPLES = 100

        # TODO: Access these values from GUI (may need TA)
        self.x = 480
        self.y = 400
        self.multiplier = 40

    def customer_gen(self, num_cust, rng = None):
        
        """Function in which we create a distribution of customer preferences

        Args:
            num_cust(int) : the total number of customer preferences you need to create
            rng(int) : A random seed that you can use to generate your customers. You can choose to not pass this, in that case the seed taken will be self.rng

        Returns:
            preferences_total(list) : List of size [num_cust, 2, num_toppings], having all generated customer preferences
        """
        rng_today = rng if rng else self.rng
        
        def get_person_preferences():
            prefs = list()
            remains = 12.0
            for i in range(self.num_toppings-1):
                p = rng_today.random()
                prefs.append(remains*p)
                remains *= (1-p)
            prefs.append(remains)
            prefs = np.array(prefs)
            rng_today.shuffle(prefs)
            return prefs

        return [[get_person_preferences() for i in range(2)] for j in range(num_cust)]

    def _get_topping_default(self, preferences):
        x_coords = [np.sin(pi/2)]
        pizzas = np.zeros((10, 24, 3))
        for j in range(constants.number_of_initial_pizzas):
            pizza_indiv = np.zeros((24,3))
            i = 0
            while i<24:
                angle = self.rng.random()*2*pi
                dist = self.rng.random()*6
                x = dist*np.cos(angle)
                y = dist*np.sin(angle)
                clash_exists = pizza_calculations.clash_exists(x, y, pizza_indiv, i)
                if not clash_exists:
                    pizza_indiv[i] = [x, y, i%self.num_toppings + 1]
                    i = i+1
            pizza_indiv = np.array(pizza_indiv)
            pizzas[j] = pizza_indiv
        print(pizzas)
        return list(pizzas)

    def _draw_topping(self, angle_start, angle_end, amount, category, r = None):
        theta = (angle_end-angle_start)/(2*amount)
        radius = self.BUFFER + 0.375/sin(theta)
        if r is not None:
            radius = max(radius, r)
        return [[radius*cos(angle_start+(2*i+1)*theta), radius*sin(angle_start+(2*i+1)*theta), category] for i in range(amount)]

    def _get_topping_2(self, preferences):
        inner = self._draw_topping(0, pi, 4, 1) +\
                self._draw_topping(pi, 2*pi, 4, 2)
        outer = self._draw_topping(0, pi, 8, 1) +\
                self._draw_topping(pi, 2*pi, 8, 2)
        pizza = inner + outer
        return [pizza] * 10

    def _get_topping_3(self, preferences):
        def helper(categories):
            inner = self._draw_topping(0, pi, 2, categories[0]) +\
                    self._draw_topping(pi, 2*pi, 2, categories[1])
            outer = self._draw_topping(0, pi, 6, categories[0]) +\
                    self._draw_topping(pi, 2*pi, 6, categories[1])
            arc = self._draw_topping(0.25*pi, 0.75*pi, 8, categories[2])
            return inner + outer + arc
        perms = list(permutations([1,2,3]))*2
        return [helper(perm) for perm in perms[0:10]]

    def _get_topping_4(self, preferences):
        def helper(categories):
            inner = self._draw_topping(0, pi, 2, categories[0]) +\
                    self._draw_topping(pi, 2*pi, 2, categories[1])
            outer = self._draw_topping(0, pi, 4, categories[0], 1.22) +\
                    self._draw_topping(pi, 2*pi, 4, categories[1], 1.22)
            # 1.22 drived as below:
            # https://www.symbolab.com/solver?or=gms&query=%28x*cos%28pi%2F8%29-0.375%29%5E2+%2B+%28x*sin%28pi%2F8%29-0.375%29%5E2+%3D+0.75%5E2
            arc = self._draw_topping(0, 0.5*pi, 6, categories[2], 4) +\
                self._draw_topping(0.5*pi, pi, 6, categories[3], 4)
            # used 4 to move the arc outer. may wanna change this.
            return inner + outer + arc
        perms = list(permutations([1,2,3,4]))
        # return [helper(perm) for perm in perms[0:10]]
        return [helper([1,2,3,4]) for perm in range(10)]  # TODO: Use permuted pizzas

    def choose_toppings(self, preferences):
        """Function in which we choose position of toppings

        Args:
            num_toppings(int) : the total number of different topics chosen among 2, 3 and 4
            preferences(list) : List of size 100*2*num_toppings for 100 generated preference pairs(actual amounts) of customers.

        Returns:
            pizzas(list) : List of size [10,24,3], where 10 is the pizza id, 24 is the topping id, innermost list of size 3 is [x coordinate of topping center, y coordinate of topping center, topping number of topping(1/2/3/4) (Note that it starts from 1, not 0)]
        """
        if self.num_toppings == 2:
            return self._get_topping_2(preferences)
        elif self.num_toppings == 3:
            return self._get_topping_3(preferences)
        elif self.num_toppings == 4:
            return self._get_topping_4(preferences)
        else:
            return self._get_topping_default(preferences)

    def _get_interpoint(self, angle, radius):
        '''Returns the cut intersection point coordinates from an angle and radius in a [x, y] list'''
        return [radius*cos(pi+angle), radius*sin(pi+angle)]

    def _get_topping_counts(self, pizza, angle, radius):
        '''Returns the actual topping counts of a pizza with given cut angle/radius in a 2xn ndarray.'''
        interpoint = self._get_interpoint(angle, radius)
        cut = [
            self.x + interpoint[0] * self.multiplier,
            self.y - interpoint[1] * self.multiplier,
            angle
        ]
        topping_counts, _ = pizza_calculations().ratio_calculator(pizza, cut, self.num_toppings, self.multiplier, self.x, self.y)
        return topping_counts
    
    def _get_error(self, pizza, angle, radius, relevant_topping_ids, customer_amounts):
        '''
        Returns the error for the given pizza/angle/radius/toppings.
        Only the error for the relevant toppings are included in the error sum.
        Angle and radius are numbers.
        '''
        topping_counts = self._get_topping_counts(pizza, angle, radius)
        return np.sum(np.abs((customer_amounts - topping_counts)[:,relevant_topping_ids]))

    def _minimize_error(self, pizza, angle, radius, relevant_topping_ids, customer_amounts):
        '''
        Returns the angle/radius which minimizes the error on the given toppings, and that error.
        Only the error for the relevant toppings are included in the error sum.
        One of angle/radius is a (start, end) tuple, the other is a number.
        '''
        h = lambda x: np.squeeze(np.array(x))[()]  # convert 1.5 or array([1.5]) to 1.5
        if isinstance(angle, tuple):
            bounds = angle
            f = lambda x: self._get_error(pizza, h(x), radius, relevant_topping_ids, customer_amounts)
        else:
            bounds = radius
            f = lambda x: self._get_error(pizza, angle, h(x), relevant_topping_ids, customer_amounts)
        minimizer, minimum, _, _ = brute(f, [bounds], Ns=self.NUM_BRUTE_SAMPLES, full_output=True)
        return minimizer, minimum

    def _get_min_cut_radius(self, outer_ring_count):
        '''Return the cut radius such that it would be tangent to the outer ring of toppings'''
        return sqrt(2)*(self.BUFFER + 0.375 + 0.375 / sin(pi / outer_ring_count))

    def _get_cut_default(self, pizzas, remaining_pizza_ids, customer_amounts):
        return remaining_pizza_ids[0], [0,0], np.random.random()*pi
    
    def _get_cut_2(self, pizzas, remaining_pizza_ids, customer_amounts):
        # not considering non-integer cuts
        angle = customer_amounts[0][0]/12 * pi
        radius = self._get_min_cut_radius(16)
        return remaining_pizza_ids[0], self._get_interpoint(angle, radius), angle

    def _get_cut_3(self, pizzas, remaining_pizza_ids, customer_amounts):
        return self._get_cut_default(pizzas, remaining_pizza_ids, customer_amounts)

    def _get_cut_4(self, pizzas, remaining_pizza_ids, customer_amounts):
        pizza_id = remaining_pizza_ids[0]
        pizza = pizzas[pizza_id]
        angle, _ = self._minimize_error(pizza, (pi, 2 * pi), 5, [0, 1], customer_amounts)
        radius_range = (self._get_min_cut_radius(8) + self.N4_RADIUS_BUFFER, 6 - self.N4_RADIUS_BUFFER)  # TODO: (1.22 + 0.375) * sqrt(2)
        radius, _ = self._minimize_error(pizza, radius_range, angle, [2, 3], customer_amounts)
        # TODO: Try both "diagonal" and "antidiagonal" cuts
        return pizza_id, self._get_interpoint(angle, radius), angle

    def choose_and_cut(self, pizzas, remaining_pizza_ids, customer_amounts):
        """Function which based n current game state returns the distance and angle, the shot must be played

        Args:
            pizzas (list): List of size [10,24,3], where 10 is the pizza id, 24 is the topping id, innermost list of size 3 is [x coordinate of topping, y coordinate of topping, topping number of topping(1/2/3/4)]
            remaining_pizza_ids (list): A list of remaining pizza's ids
            customer_amounts (list): The amounts in which the customer wants their pizza

        Returns:
            Tuple[int, center, first cut angle]: Return the pizza id you choose, the center of the cut in format [x_coord, y_coord] where both are in inches relative of pizza center of radius 6, the angle of the first cut in radians. 
        """
        if self.num_toppings == 2:
            return self._get_cut_2(pizzas, remaining_pizza_ids, customer_amounts)
        elif self.num_toppings == 3:
            return self._get_cut_3(pizzas, remaining_pizza_ids, customer_amounts)
        elif self.num_toppings == 4:
            return self._get_cut_4(pizzas, remaining_pizza_ids, customer_amounts)
        else:
            return self._get_cut_default(pizzas, remaining_pizza_ids, customer_amounts)
