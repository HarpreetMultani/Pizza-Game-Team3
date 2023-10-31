from tokenize import String
import numpy as np
from typing import Tuple, List
import constants
from utils import pizza_calculations

class Player:
    def __init__(self, num_toppings, rng: np.random.Generator) -> None:
        """Initialise the player"""
        self.rng = rng
        self.num_toppings = num_toppings

    def customer_gen(self, num_cust, rng = None):
        
        """Function in which we create a distribution of customer preferences

        Args:
            num_cust(int) : the total number of customer preferences you need to create
            rng(int) : A random seed that you can use to generate your customers. You can choose to not pass this, in that case the seed taken will be self.rng

        Returns:
            preferences_total(list) : List of size [num_cust, 2, num_toppings], having all generated customer preferences
        """
        
        preferences_total = []
        if rng==None:
            for i in range(num_cust):
                preferences_1 = self.rng.random((self.num_toppings,))
                preferences_1 = 12*preferences_1/np.sum(preferences_1)
                preferences_2 = self.rng.random((self.num_toppings,))
                preferences_2 = 12*preferences_2/np.sum(preferences_2)
                preferences = [preferences_1, preferences_2]
                equal_prob = self.rng.random()
                if equal_prob <= 0.0:
                    preferences = (np.ones((2,self.num_toppings))*12/self.num_toppings).tolist()
                preferences_total.append(preferences)
        else : 
            for i in range(num_cust):
                preferences_1 = rng.random((self.num_toppings,))
                preferences_1 = 12*preferences_1/np.sum(preferences_1)
                preferences_2 = rng.random((self.num_toppings,))
                preferences_2 = 12*preferences_2/np.sum(preferences_2)
                preferences = [preferences_1, preferences_2]
                equal_prob = rng.random()
                if equal_prob <= 0.0:       #change this if you want toppings to show up
                    preferences = (np.ones((2,self.num_toppings))*12/self.num_toppings).tolist()
                preferences_total.append(preferences) 
        return preferences_total

        


    #def choose_discard(self, cards: list[str], constraints: list[str]):
    def choose_toppings(self, preferences):
        """Function in which we choose position of toppings

        Args:
            num_toppings(int) : the total number of different topics chosen among 2, 3 and 4
            preferences(list) : List of size 100*2*num_toppings for 100 generated preference pairs(actual amounts) of customers.

        Returns:
            pizzas(list) : List of size [10,24,3], where 10 is the pizza id, 24 is the topping id, innermost list of size 3 is [x coordinate of topping center, y coordinate of topping center, topping number of topping(1/2/3/4) (Note that it starts from 1, not 0)]
        """
        
        x_coords = [np.sin(np.pi/2)]
        pizzas = np.zeros((10, 24, 3))
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
        return  remaining_pizza_ids[0], [0,0], np.pi/4
