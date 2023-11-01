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
        self.x = 12*self.multiplier	# Center Point x of pizza
        self.y = 10*self.multiplier	# Center Point y of pizza
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
        for j in range(10):  # Assuming we want to make 10 pizzas
            pizza_indiv = np.zeros((24, 3))
            # Define the radius of the circle where the toppings will be placed
            inner_circle_radius = 3  # Radius for toppings 1 and 2
            outer_circle_radius = 4.5  # Radius for toppings 3 and 4

            for i in range(24):
                if self.num_toppings == 2:
                    angle = 2 * np.pi * i / 24
                    x = inner_circle_radius * np.cos(angle)
                    y = inner_circle_radius * np.sin(angle)
                    topping_type = 1 if angle < np.pi else 2

                elif self.num_toppings == 3:
                    if i < 16:  # Toppings 1 and 2
                        angle = 2 * np.pi * i / 16
                        x = inner_circle_radius * np.cos(angle)
                        y = inner_circle_radius * np.sin(angle)
                        topping_type = 1 if i < 8 else 2
                    else:  # Topping 3
                        angle = 2 * np.pi * (i - 8) / 16 + np.pi/8
                        x = outer_circle_radius * np.cos(angle)
                        y = outer_circle_radius * np.sin(angle)
                        topping_type = 3

                elif self.num_toppings == 4:
                    if i < 12:  # Toppings 1 and 2
                        angle = 2 * np.pi * i / 12
                        x = inner_circle_radius * np.cos(angle)
                        y = inner_circle_radius * np.sin(angle)
                        topping_type = 1 if y > 0 else 2
                    else:  # Toppings 3 and 4
                        angle = 2 * np.pi * (i - 6) / 24
                        if i < 18:  # Topping 3
                            angle += np.pi/4 + np.pi/24  
                            x = outer_circle_radius * np.cos(angle)
                            y = outer_circle_radius * np.sin(angle)
                            topping_type = 3
                        else:  # Topping 4
                            angle += np.pi/2 + np.pi/4  
                            x = outer_circle_radius * np.cos(angle)  
                            y = outer_circle_radius * np.sin(angle)
                            topping_type = 4

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
        final_id = remaining_pizza_ids[0]
        final_center = [-3,-3]
        final_angle = 360
        max_score = 0
        angles = [final_angle]
        for id in remaining_pizza_ids:
            test_center = [0,0]
            test_angle = np.pi/8
            
            for i in range(0,100):
                test_angle = i
                cut = [self.x + test_center[0]*self.multiplier, self.y - test_center[1]*self.multiplier, test_angle]
                score = self.get_score([pizzas[id]], [0], [customer_amounts], [cut])

                if score > max_score:
                    final_id = id
                    final_center = test_center
                    final_angle = test_angle
        
        return final_id, final_center, final_angle

    def get_score(self, pizzas, ids, preferences, cuts):
        B, C, U, obtained_preferences, center_offsets, slice_amount_metric = self.calculator.final_score(pizzas, ids, preferences, cuts, self.num_toppings, self.multiplier, self.x, self.y)
        usum = self.sum(U[0])
        bsum = self.sum(B[0])
        csum = self.sum(C[0])
        return bsum - csum

    def sum(self, array):
        sum = 0
        for a in array:
            for b in a:
                sum += b
        return sum