from tokenize import String
import numpy as np
from typing import Tuple, List
import constants
from utils import pizza_calculations
#our team code
class Player:
    def __init__(self, num_toppings, rng: np.random.Generator) -> None:
        """Initialise the player"""
        self.rng = rng
        self.num_toppings = num_toppings
        self.multiplier=40
        self.calculator = pizza_calculations()
        self.counter = 0

    def customer_gen(self, num_cust, rng = None):
        
        """Function in which we create a distribution of customer preferences

        Args:
            num_cust(int) : the total number of customer preferences you need to create
            rng(int) : A random seed that you can use to generate your customers. You can choose to not pass this, in that case the seed taken will be self.rng

        Returns:
            preferences_total(list) : List of size [num_cust, 2, num_toppings], having all generated customer preferences
        """
        
        mean = 0.8
        std_dev = 2.0
        
        preferences_total = []
        if rng==None:
            np.random.seed(self.rng)
            for i in range(num_cust):
                preferences_1 = np.random.normal(mean, std_dev, self.num_toppings)
                print(f'preferences 1 self.rng {preferences_1}')
                preferences_1 = np.clip(preferences_1, 0, None)  # Ensure preferences are non-negative
                preferences_1 /= preferences_1.sum()  # Normalize the preferences
                preferences_total.append([preferences_1.tolist(), preferences_1.tolist()])  # Duplicate preferences
        else :
            np.random.seed(rng)
            for i in range(num_cust):
                preferences_1 = np.random.normal(mean, std_dev, self.num_toppings)
                print(f'preferences 1 rng {preferences_1}')
                preferences_1 = np.clip(preferences_1, 0, None)  # Ensure preferences are non-negative
                preferences_1 /= preferences_1.sum()  # Normalize the preferences
                preferences_total.append([preferences_1.tolist(), preferences_1.tolist()])  # Duplicate preferences

        print(f'preferences total {preferences_total}')
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
            # Define the radius of the circle where the toppings will be placed
            circle_radius = 3 # You can adjust this value as needed
            for i in range(24):
                angle = 2 * np.pi * i / 24
                x = circle_radius * np.cos(angle)
                y = circle_radius * np.sin(angle)
                # Determine topping type based on the angle and number of toppings
                if self.num_toppings == 2:
                    topping_type = 1 if angle < np.pi else 2
                elif self.num_toppings == 3:
                    topping_type = 1 if angle < 2*np.pi/3 else (2 if angle < 4*np.pi/3 else 3)
                else: # self.num_toppings == 4
                    topping_type = 1 if angle < np.pi/2 else (2 if angle < np.pi else (3 if angle < 3*np.pi/2 else 4))
                pizza_indiv[i] = [x, y, topping_type]
            pizzas[j] = pizza_indiv
        return list(pizzas)
        """
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
        """
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
        final_id = 0
        final_center = [1,1]
        final_angle = np.pi/8
        final_score = 0
        
        id = remaining_pizza_ids[final_id]
        x = 1; y = 1; angle = np.pi/8
        cut = [1, 1, angle]
        if self.counter == 0:
            B, C, U, obtained_preferences = self.calculator.final_score(pizzas, [0], [customer_amounts], [cut], self.num_toppings, self.multiplier, 12*self.multiplier, 10*self.multiplier)
            """
            print(B)
            print(self.sum(B[0]))
            print(C)
            print(self.sum(C[0]))
            print(U)
            print(self.sum(U[0]))
            print(obtained_preferences)
            print(self.sum(obtained_preferences[0]))
            """
            self.counter += 1
        
        return remaining_pizza_ids[final_id], final_center, final_angle

    def sum(self, array):
        sum = 0
        for a in array:
            for b in a:
                sum += b
        return sum

