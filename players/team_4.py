from tokenize import String
import numpy as np
from typing import Tuple, List
import constants
from utils import pizza_calculations
from itertools import chain

class Player:
    def __init__(self, num_toppings, rng: np.random.Generator) -> None:
        """Initialise the player"""
        self.rng = rng
        self.num_toppings = num_toppings

    # def customer_gen(self, num_cust, rng = None):
        
    #     """Function in which we create a distribution of customer preferences

    #     Args:
    #         num_cust(int) : the total number of customer preferences you need to create
    #         rng(int) : A random seed that you can use to generate your customers. You can choose to not pass this, in that case the seed taken will be self.rng

    #     Returns:
    #         preferences_total(list) : List of size [num_cust, 2, num_toppings], having all generated customer preferences
    #     """
    #     preferences_total = []
    #     if rng==None:
    #         for i in range(num_cust):
    #             preferences_1 = self.rng.random((self.num_toppings,))
    #             preferences_1 = 12*preferences_1/np.sum(preferences_1)
    #             preferences_2 = self.rng.random((self.num_toppings,))
    #             preferences_2 = 12*preferences_2/np.sum(preferences_2)
    #             preferences = [preferences_1, preferences_2]
    #             equal_prob = self.rng.random()
    #             if equal_prob <= 0.0:
    #                 preferences = (np.ones((2,self.num_toppings))*12/self.num_toppings).tolist()
    #             preferences_total.append(preferences)
    #     else : 
    #         for i in range(num_cust):
    #             preferences_1 = rng.random((self.num_toppings,))
    #             preferences_1 = 12*preferences_1/np.sum(preferences_1)
    #             preferences_2 = rng.random((self.num_toppings,))
    #             preferences_2 = 12*preferences_2/np.sum(preferences_2)
    #             preferences = [preferences_1, preferences_2]
    #             equal_prob = rng.random()
    #             if equal_prob <= 0.0:       #change this if you want toppings to show up
    #                 preferences = (np.ones((2,self.num_toppings))*12/self.num_toppings).tolist()
    #             preferences_total.append(preferences) 
    #     return preferences_total

        
    def customer_gen(self, num_cust, rng=None, alpha=2, beta=2):
        """
        Function to create non-uniform customer preferences using a beta distribution.

        Args:
            num_cust (int): The total number of customer preferences to create.
            rng (int): A random seed for generating customers. If None, self.rng will be used.
            alpha (float): Alpha parameter for the beta distribution.
            beta (float): Beta parameter for the beta distribution.

        Returns:
            preferences_total (list): List of size [num_cust, 2, num_toppings], containing generated customer preferences.
        """

        preferences_total = []

        if rng is None:
            for i in range(num_cust):
                preferences_1 = self.rng.beta(alpha, beta, self.num_toppings)
                preferences_1 = 12*preferences_1/np.sum(preferences_1)
                preferences_2 = self.rng.beta(alpha, beta, self.num_toppings)
                preferences_2 = 12*preferences_2/np.sum(preferences_2)
                preferences = [preferences_1, preferences_2]
                preferences_total.append(preferences)
        else:
            for i in range(num_cust):
                preferences_1 = rng.beta(alpha, beta, self.num_toppings)
                preferences_1 = 12*preferences_1/np.sum(preferences_1)
                preferences_2 = rng.beta(alpha, beta, self.num_toppings)
                preferences_2 = 12*preferences_2/np.sum(preferences_2)
                preferences = [preferences_1, preferences_2]
                preferences_total.append(preferences)

        return preferences_total

    def toppings_2(self):
        pizzas = np.zeros((10, 24, 3))

        for j in range(constants.number_of_initial_pizzas):
                pizza_indiv = np.zeros((24,3))
                for i in range(24):
                    angle = (i * np.pi / 12) + np.pi / 24
                    dist = 3.0
                    x = dist * np.cos(angle)
                    y = dist * np.sin(angle)
                    pizza_indiv[i] = [x, y, (i/12) + 1]
                pizza_indiv = np.array(pizza_indiv)
                pizzas[j] = pizza_indiv

        return list(pizzas)

    def toppings_4(self, prefs):
        arr = np.stack(prefs)
        corr = np.corrcoef(arr, rowvar=False)
        idx = np.argsort(corr)

        pizzas = np.zeros((10, 24, 3))
        for j in range(constants.number_of_initial_pizzas):
                pizza_indiv = np.zeros((24,3))
                for i, t in enumerate(reversed(list(idx[0]))):
                    if not i:
                        doffset, thoffset = 0, 0
                    if i == 1:
                        doffset, thoffset = 1, np.pi / 2
                    if i == 2:
                        doffset, thoffset = 1, -(np.pi / 2)
                    if i == 3:
                        doffset, thoffset = 0, np.pi

                    for k in range(6):
                        angle = (k * np.pi / 6) + (np.pi / 12) + thoffset
                        dist = 1.5 + doffset
                        x = dist * np.cos(angle)
                        y = dist * np.sin(angle)
                        pizza_indiv[6 * i + k] = [x, y, t+1]
                pizza_indiv = np.array(pizza_indiv)
                pizzas[j] = pizza_indiv

        return list(pizzas)
        

    def opt_ratio(self, amounts):
        p, q, n = amounts[0], amounts[1], self.num_toppings
        return np.array([0.5 * (p[i] - q[i]) + 12 / n for i in range(n)]) 

    #def choose_discard(self, cards: list[str], constraints: list[str]):
    def choose_toppings(self, preferences):
        """Function in which we choose position of toppings

        Args:
            num_toppings(int) : the total number of different topics chosen among 2, 3 and 4
            preferences(list) : List of size 100*2*num_toppings for 100 generated preference pairs(actual amounts) of customers.

        Returns:
            pizzas(list) : List of size [10,24,3], where 10 is the pizza id, 24 is the topping id, innermost list of size 3 is [x coordinate of topping center, y coordinate of topping center, topping number of topping(1/2/3/4) (Note that it starts from 1, not 0)]
        """

        if self.num_toppings == 2:
            return self.toppings_2()

        pref_opt = [self.opt_ratio(p) for p in preferences]
        
        if self.num_toppings == 4:
            return self.toppings_4(pref_opt)
        else:
            for j in range(constants.number_of_initial_pizzas):
                        pizza_indiv = np.zeros((24,3))
                        i = 0
                        while i<24:
                            angle = self.rng.random()*2*np.pi
                            dist = self.rng.random()*6
                            x = dist*np.cos(angle)
                            y = dist*np.sin(angle)
                            clash_exists = pizza_calculations.clash_exists(x, y, pizza_indiv, i)
                            if not clash_exists:
                                pizza_indiv[i] = [x, y, i%self.num_toppings + 1]
                                i = i+1
                        pizza_indiv = np.array(pizza_indiv)
                        pizzas[j] = pizza_indiv

        return list(pizzas)


    #def play(self, cards: list[str], constraints: list[str], state: list[str], territory: list[int]) -> Tuple[int, str]:
    def choose_and_cut(self, pizzas, remaining_pizza_ids, customer_amounts):
        """Function which based n current game state returns the distance and angle, the shot must be played

        Args:
            pizzas (list): List of size [10,24,3], where 10 is the pizza id, 24 is the topping id, innermost list of size 3 is [x coordinate of topping, y coordinate of topping, topping number of topping(1/2/3/4)]
            remaining_pizza_ids (list): A list of remaining pizza's ids
            customer_amounts (list): The amounts in which the customer wants their pizza

        Returns:
            Tuple[int, center, first cut angle]: Return the pizza id you choose, the center of the cut in format [x_coord, y_coord] where both are in inches relative of pizza center of radius 6, the angle of the first cut in radians. 
        """
        pizza_id = remaining_pizza_ids[0]
        pref = self.opt_ratio(customer_amounts)
        if len(pref) == 3:
            return  remaining_pizza_ids[0], [0,0], np.pi/8
        
        angle = (pref[0] / (24 / self.num_toppings)) * np.pi
        dist = 5.999
        x = dist*np.cos(angle)
        y = dist*np.sin(angle)

        return remaining_pizza_ids[0], [x,y], angle
