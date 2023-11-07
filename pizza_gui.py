
from random import uniform
import tkinter as Tkinter
import numpy as np
from tkinter import *
import math	# Required For Coordinates Calculation
import time	# Required For Time Handling
import constants as constants
import pickle as pkl
import string
from functools import reduce
import time
import copy
import argparse
from utils import pizza_calculations
from players.default_player import Player as default_player
from players.team_1 import Player as p1
from players.team_2 import Player as p2
from players.team_3 import Player as p3
from players.team_4 import Player as p4
from players.team_5 import Player as p5
from players.team_6 import Player as p6

class gui():

    def __init__(self, args):
        self.use_gui = True
        self.rng = np.random.default_rng(int(args.seed))
        self.no_of_constraints = constants.number_of_constraints_pp
        
        self.multiplier=40	# Pizza radius = 6*multiplier units
        self.x = 12*self.multiplier	# Center Point x of pizza
        self.y = 10*self.multiplier	# Center Point y of pizza
        self.xs = [30, 60, 90, 120, 150, 30, 60, 90, 120, 150]
        self.ys = [30, 30, 30, 30, 30, 60, 60, 60, 60, 60]

        self.pizzas = np.zeros((10, 24, 3))   #10 pizzas, 27 toppings, each has [x, y, topping type] (x and y wrt pizza center)
        self.pizza_id = 0
        self.cuts = list(np.zeros((10,3)))  #10 pizzas, x, y coordinates of cut intscn wrt pizza center and angle of cut in the 0-45 degree range
        self.type_p = ""
        self.pizzas_drawn = 0
        self.options_player = ["custom_player","default_player", "p1", "p2", "p3","p4","p5", "p6"]
        self.options_topping = [2,3,4]
        self.topping_id = 0 #Current topping id
        self.template_adjustor = 2*self.multiplier #if this goes badly set it to 20     #Just to arrange the difference in sizes of both display screens of 1 and 10 pizzas
        #self.pizza_cuts = list(np.zeros((constants.number_of_initial_pizzas ,3)))           #Here cuts positions are absolute and NOT WRT pizza centers, as it is much easier to deal with them that way. It we are not using gui, we assume self.x, self.y =0 and self.multiplier = 1
        self.customer_id = 0
        self.player_instance = None
        self.preferences_100 = None
        #Inititalise preferences in the begining only
        self.click_indic = 0
        self.final_preferences = []
        self.pizza_choice_order = []
        self.calculator = pizza_calculations()

        #replace with arguments
        #self.autoplayer_number = args.autoplayer_number
        self.generator_number = int(args.generator_number)
        self.multiplier = int(args.interface_size) #(default 40)
        self.rng_generator_100 = np.random.default_rng(int(args.gen_100_seed))
        self.rng_generator_10 = np.random.default_rng(int(args.gen_10_seed))

    def initialise_player(self, player_px, autoplayer) :
            #setting player
            if player_px == 0:
                self.player_instance = default_player(self.num_toppings, self.rng)
            elif player_px == 1:
                self.player_instance = p1(self.num_toppings, self.rng)
            elif player_px == 2:
                # print("initialising player 2")
                self.player_instance = p2(self.num_toppings, self.rng)
            elif player_px == 3:
                self.player_instance = p3(self.num_toppings, self.rng)
            elif player_px == 4:
                self.player_instance = p4(self.num_toppings, self.rng)
            elif player_px == 5:
                self.player_instance = p5(self.num_toppings, self.rng)
            elif player_px == 6:
                self.player_instance = p6(self.num_toppings, self.rng)
            else:
                self.player_instance = default_player(self.num_toppings, self.rng)
            #setting autoplayer
            if autoplayer == 0:
                self.auto_player = default_player(self.num_toppings, self.rng)
            elif autoplayer == 1:
                self.auto_player = p1(self.num_toppings, self.rng)
            elif autoplayer == 2:
                self.auto_player = p2(self.num_toppings, self.rng)
            elif autoplayer == 3:
                self.auto_player = p3(self.num_toppings, self.rng)
            elif autoplayer == 4:
                self.auto_player = p4(self.num_toppings, self.rng)
            elif autoplayer == 5:
                self.auto_player = p5(self.num_toppings, self.rng)
            elif autoplayer == 6:
                self.auto_player = p6(self.num_toppings, self.rng)
            else:
                self.auto_player = default_player(self.num_toppings, self.rng)
            
# creating Canvas
    def create_canvas_for_shapes(self):
        self.canvas=Tkinter.Canvas(self.root, width = 35*self.multiplier, height = 27*self.multiplier, bg='#E5E6DC')
        self.canvas.pack(expand='yes',fill='both')
        return

    def clickevent_topping(self, event):
        x_coord = event.x
        y_coord = event.y
        if self.topping_id < 24/self.num_toppings:
            topping_number = 1
        elif self.topping_id < 48/self.num_toppings:
            topping_number = 2
        elif self.topping_id < 72/self.num_toppings:
            topping_number = 3
        else:
            topping_number = 4
        #topping_number = self.topping_id%self.num_toppings + 1
        if topping_number == 1:
            color_top = "black"
        elif topping_number == 2:
            color_top = "blue"
        elif topping_number == 3:
            color_top = "red"
        elif topping_number == 4:
            color_top = "yellow"
        #Code to ensure no clashes
        x_relative = (x_coord - self.x)/self.multiplier
        y_relative = -(y_coord - self.y)/self.multiplier
        pizza = self.pizzas[self.pizza_id]
        clash_exists = pizza_calculations.clash_exists(x_relative, y_relative, pizza, self.topping_id)
        if clash_exists:
            self.label.config( text = "Invalid placement. Try again.")
        else : 
            self.canvas.create_oval(x_coord - (0.375*self.multiplier), y_coord - (0.375*self.multiplier), x_coord + (0.375*self.multiplier), y_coord + (0.375*self.multiplier), fill = color_top)
            self.pizzas[self.pizza_id][self.topping_id][0] = (x_coord - self.x)/self.multiplier
            self.pizzas[self.pizza_id][self.topping_id][1] = -(y_coord - self.y)/self.multiplier
            self.pizzas[self.pizza_id][self.topping_id][2] = topping_number
            self.topping_id = self.topping_id + 1   #Used to track overall which toppings should be shown on a single pizza
            self.label.config( text = "Make pizza number "+str(self.pizza_id)+ " with type "+str(topping_number)+ " of topping and "+ str(24-self.topping_id) + " toppings left.")
            if self.topping_id >= 24:
                self.pizza_id = self.pizza_id + 1
                self.topping_id = 0
                self.label.config( text = "Make pizza number "+str(self.pizza_id)+ " with type "+str(topping_number)+ " of topping and "+ str(24-self.topping_id) + " toppings left.")
                if self.pizza_id<constants.number_of_initial_pizzas:
                    self.draw_pizza(self.pizza_id)
                    #add an autoplay button for the next pizza

                else:
                    self.canvas.unbind("<Button-1>")
                    self.button.destroy()
                    self.button = Button( self.root , text = "Start Serving!!" , command = self.pizza_choice)
                    self.button.place(x=123, y=20)
                    self.label.config( text = "Here are all of your pizzas!!")
                    self.draw_pizzas()

    def clickevent_pizzacenter(self, event):
        self.button.destroy()
        self.button_1.destroy()
        self.pizza_number_choice.destroy()
        x_coord = event.x
        y_coord = event.y
        if (x_coord-self.x)**2 + (y_coord-self.y)**2 > (6*self.multiplier)**2 :
            self.label.config( text = "Invalid placement. Try again.")
            self.canvas.unbind("<Button-1>")
            self.choose_cuts()
        else:
            self.cuts[self.pizza_id][0] = x_coord
            self.cuts[self.pizza_id][1] = y_coord
            self.click_indic = self.click_indic + 1
            self.label.config( text = "You chose your center!")
            self.canvas.create_oval(x_coord - (0.1*self.multiplier), y_coord - (0.1*self.multiplier), x_coord + (0.1*self.multiplier), y_coord + (0.1*self.multiplier), fill = "black")
            self.canvas.unbind("<Button-1>")
            self.canvas.bind("<Button-1>", self.clickevent_cut)

    def clickevent_cut(self, event):
        x_coord = event.x
        y_coord = event.y
        piz_center = [self.cuts[self.pizza_id][0], self.cuts[self.pizza_id][1]]
        if x_coord == piz_center[0]:
            thetaabs = 0
        else:
            thetaabs = np.arctan(-(y_coord - piz_center[1])/(x_coord - piz_center[0]))
            if (x_coord - piz_center[0]) <= 0:
                thetaabs = thetaabs + np.pi
        if self.x == piz_center[0]:
            centangle = 0
        else:
            centangle = np.arctan(-(piz_center[1] - self.y) / (piz_center[0]-self.x))
        theta = (centangle - thetaabs)
        self.cuts[self.pizza_id][2] = thetaabs
        for i in range(8):
            if i==0 or i==4:
                self.draw_cuts(piz_center, thetaabs+i*np.pi/4, color = "yellow")
            else:
                self.draw_cuts(piz_center, thetaabs+i*np.pi/4)
        self.click_indic = self.click_indic + 1
        self.canvas.unbind("<Button-1>")
        #Create a label stating results
        results, temp = self.calculator.ratio_calculator(self.pizzas[self.pizza_id], self.cuts[self.pizza_id], self.num_toppings, self.multiplier, self.x, self.y )
        self.final_preferences.append(results)
        self.pizza_choice_order.append(self.pizza_id)
        self.label.config( text = "Preferences are : "+ str(np.round(self.preferences[self.customer_id])) +". Results are " + str(np.round(results,2)) + ".")
        #create a button to go next
        game_over_indic = 1
        for i in range(len(self.cuts)):
            if self.cuts[i][0] == 0 and self.cuts[i][1] == 0 and self.cuts[i][2] == 0:
                game_over_indic = 0
        if game_over_indic == 0:
            self.button = Button( self.root , text = "Next Customer" , command = self.pizza_choice)
            self.button.place(x=153, y=20)
        else:
            self.button = Button( self.root , text = "See results" , command = self.see_score)
            self.button.place(x=153, y=20)
        self.customer_id = self.customer_id + 1
        
    def draw_pizza(self, pizza_id):
        self.canvas.create_oval(self.x - (self.multiplier*6), self.y - (self.multiplier*6), self.x + (self.multiplier*6), self.y + (self.multiplier*6), fill = "navajo white")
        self.canvas.create_oval(self.x - (self.multiplier*5.5), self.y - (self.multiplier*5.5), self.x + (self.multiplier*5.5), self.y + (self.multiplier*5.5), fill = "red3")
        for pizza_top_i in list(self.pizzas[pizza_id]):
            if pizza_top_i[2]!=0:     #If they have been initialized
                if pizza_top_i[2] == 1:
                    color_top = "black"
                elif pizza_top_i[2] == 2:
                    color_top = "blue"
                elif pizza_top_i[2] == 3:
                    color_top = "red"
                elif pizza_top_i[2] == 4:
                    color_top = "yellow"
                self.canvas.create_oval(self.x + pizza_top_i[0]*self.multiplier - (0.375*self.multiplier), self.y - pizza_top_i[1]*self.multiplier - (0.375*self.multiplier), self.x + pizza_top_i[0]*self.multiplier + (0.375*self.multiplier), self.y - pizza_top_i[1]*self.multiplier + (0.375*self.multiplier), fill = color_top)

    def draw_pizzas(self):
        self.canvas.delete('all')
        for pizza_id in range(constants.number_of_initial_pizzas):
            column = pizza_id%5
            row = pizza_id//5
            x_small = self.x - (2.5-(column+1))*self.x/2
            if self.multiplier>=35:
                y_small = self.y - (1-(row+1))*self.y - 100
            else:
                y_small = self.y - (1-(row+1))*0.6*self.y - 100
            multiplier_small = self.multiplier/2
            self.canvas.create_oval(self.template_adjustor + x_small - (multiplier_small*6), -self.template_adjustor + y_small - (multiplier_small*6), self.template_adjustor + x_small + (multiplier_small*6), -self.template_adjustor + y_small + (multiplier_small*6), fill = "navajo white")
            self.canvas.create_oval(self.template_adjustor + x_small - (multiplier_small*5.5), -self.template_adjustor + y_small - (multiplier_small*5.5), self.template_adjustor + x_small + (multiplier_small*5.5), -self.template_adjustor + y_small + (multiplier_small*5.5), fill = "red3")
            for pizza_top_i in list(self.pizzas[pizza_id]):
                if pizza_top_i[2]!=0:
                    if pizza_top_i[2] == 1:
                        color_top = "black"
                    elif pizza_top_i[2] == 2:
                        color_top = "blue"
                    elif pizza_top_i[2] == 3:
                        color_top = "red"
                    elif pizza_top_i[2] == 4:
                        color_top = "yellow"
                    self.canvas.create_oval(self.template_adjustor + x_small + pizza_top_i[0]*multiplier_small - (0.375*multiplier_small), -self.template_adjustor + y_small - pizza_top_i[1]*multiplier_small - (0.375*multiplier_small), self.template_adjustor + x_small + pizza_top_i[0]*multiplier_small + (0.375*multiplier_small), -self.template_adjustor + y_small - pizza_top_i[1]*multiplier_small + (0.375*multiplier_small), fill = color_top)
            self.canvas.create_text(self.template_adjustor + x_small, -self.template_adjustor + y_small + 7*multiplier_small , text=str(pizza_id), fill="black", font=('Helvetica 15 bold'))

    def auto_pizza(self):
        self.pizzas[self.pizza_id] = self.auto_player.choose_toppings(self.preferences_100)[0]
        self.pizza_id = self.pizza_id + 1
        self.topping_id = 0
        self.label.config( text = "Make pizza number "+str(self.pizza_id)+ " with "+str(self.num_toppings)+ " types of toppings and "+ str(24-self.topping_id) + " toppings left.")
        if self.pizza_id<constants.number_of_initial_pizzas:
            self.draw_pizza(self.pizza_id)
        else:
            self.canvas.unbind("<Button-1>")
            self.button.destroy()
            self.button = Button( self.root , text = "Start Serving!!" , command = self.pizza_choice)
            self.button.place(x=123, y=20)
            self.label.config( text = "Here are all of your pizzas!!")
            self.draw_pizzas()

    def end_run(self):
        exit(1)
        
    def draw_cuts(self, center, theta, color="black"):     #theta is in radians here
        dist_centers = math.sqrt((center[0]-self.x)**2 + (center[1]- self.y)**2)
        if dist_centers/self.multiplier >= 6:
            self.label.config( text = "You tried to place the center outside the pizza. That's not cool bro.")
        if center[0] == self.x:
            angle_centerline = 0
        else:
            angle_centerline = math.atan(- (center[1] - self.y)/(center[0] - self.x))
        theta_diag = angle_centerline - theta
        sinin_1 = math.asin(math.sin(theta_diag) * dist_centers/(self.multiplier*6))
        phi_1 = theta_diag - sinin_1
        phi_2 = theta_diag - math.pi + sinin_1
        if np.round(math.sin(theta_diag), 4)==0:
            point_1 = [self.x + 6*self.multiplier*math.cos(angle_centerline)  ,  self.y - 6*self.multiplier*math.sin(angle_centerline)]
            point_2 = [self.x - 6*self.multiplier*math.cos(angle_centerline)  ,  self.y + 6*self.multiplier*math.sin(angle_centerline)]
        else:
            y1 = self.multiplier*6*math.sin(phi_1)/math.sin(theta_diag)
            y2 = self.multiplier*6*math.sin(phi_2)/math.sin(theta_diag)
            #point_1 = [center[0] - y1*math.sin(theta + angle_centerline) , center[1] - y1*math.cos(theta + angle_centerline)]
            #point_2 = [center[0] - y2*math.sin(theta + angle_centerline) , center[1] - y2*math.cos(theta + angle_centerline)]
            if center[0] < self.x:
                point_1 = [center[0] - y1*math.cos(angle_centerline - theta_diag) , center[1] + y1*math.sin(angle_centerline - theta_diag)]
                point_2 = [center[0] - y2*math.cos(angle_centerline - theta_diag) , center[1] + y2*math.sin(angle_centerline - theta_diag)]
            else:
                point_1 = [center[0] + y1*math.cos(angle_centerline - theta_diag) , center[1] - y1*math.sin(angle_centerline - theta_diag)]
                point_2 = [center[0] + y2*math.cos(angle_centerline - theta_diag) , center[1] - y2*math.sin(angle_centerline - theta_diag)]
        self.canvas.create_line(point_1[0],point_1[1], point_2[0], point_2[1], fill = color)

    def create_pizza(self):
        self.canvas.bind("<Button-1>", clickevent)

    def end_run(self):
        exit(1)

    def get_pizzas(self):
        self.type_players.destroy()
        self.num_top.destroy()
        self.update_indicator = 1
        self.type_player = self.type_p.get() 
        self.num_player = self.options_player.index(self.type_player) - 1
        # print("self.num_player", self.num_player)
        self.num_toppings = int(self.num_p.get())
        self.all_player_instances = [ default_player(self.num_toppings, self.rng), p1(self.num_toppings, self.rng), p2(self.num_toppings, self.rng), p3(self.num_toppings, self.rng), p4(self.num_toppings, self.rng), p5(self.num_toppings, self.rng), p6(self.num_toppings, self.rng)]
        #self.preferences = np.zeros((constants.number_of_initial_pizzas, 2, self.num_toppings))
        self.preferences = self.all_player_instances[self.generator_number].customer_gen(10, self.rng_generator_10)
        self.preferences_100 = self.all_player_instances[self.generator_number].customer_gen(100, self.rng_generator_100)
        self.initialise_player(self.num_player, self.num_player)
        if self.type_player != "custom_player":
            #self.pizzas = self.player.create_pizzas(self.num_toppings)      #This line should come in other pizza_game.py. There te self gets updated and transferred here.
            self.button.destroy()
            self.pizzas = self.player_instance.choose_toppings(self.preferences_100)
            self.pizzas_drawn = constants.number_of_initial_pizzas
            clash_exists_overall = False
            for i in range(constants.number_of_initial_pizzas):
                for j in range(24):
                    pizza = self.pizzas[i]
                    clash_exists = pizza_calculations.clash_exists(self.pizzas[i][j][0], self.pizzas[i][j][1], pizza, j)
                    if clash_exists == True:
                        clash_exists_overall = True
            if clash_exists_overall:
                self.label.config( text = "Overlapping placement. You cannot serve customers now.")
                self.button.destroy()
                self.button = Button( self.root , text = "Exit" , command = self.end_run)
                self.button.place(x=123, y=20)
            else:
                self.button = Button( self.root , text = "Start Serving!!" , command = self.pizza_choice)
                self.button.place(x=123, y=20)
                self.draw_pizzas()
        else:
            self.button.destroy()
            self.button = Button( self.root , text = "Autoplay turn" , command = self.auto_pizza)
            self.button.place(x=123, y=20)
            if self.pizza_id >= 10:
                self.button.destroy()
                self.label.config( text = "Congratulations chef all your pizzas are made!!")
                self.button = Button( self.root , text = "Start Serving!!" , command = self.pizza_choice)
                self.button.place(x=123, y=20)
                my_dict = self.convert_to_dict()
                with open("pizza_gui.pkl", "wb") as f:
                    pkl.dump(my_dict, f)
            else:
                self.draw_pizza(self.pizza_id)
                self.label.config( text = "Make pizza number "+str(self.pizza_id)+ " with type "+str(1)+ " of topping and "+ str(24-self.topping_id) + " toppings left.")
                #frame = Frame(self.root, width=300, height=250)
                self.canvas.bind("<Button-1>", self.clickevent_topping)
                #frame.pack()
                #ensure it's not in a radius of other topping

    def pizza_choice(self):
        #add if condition for when no preference and auto cut, so no time wasted
        self.canvas.delete('all')
        self.button.destroy()
        self.draw_pizzas()
        #print("hi")
        if self.customer_id == constants.number_of_initial_pizzas:
            self.button = Button( self.root , text = "See final scores" , command = self.see_score)
            self.button.place(x=153, y=20)
        else:
            self.button = Button( self.root , text = "Autoplay" , command = self.autoplay_cuts)
            self.button.place(x=153, y=20)
            self.button_1 = Button( self.root , text = "Manual play" , command = self.choose_cuts)
            self.button_1.place(x=253, y=20)
            self.label.config( text = "Customer number "+str(self.customer_id)+ " with preferences "+str(self.preferences[self.customer_id][0])+ " and "+ str(self.preferences[self.customer_id][1]))
            self.pizza_cut_choice = StringVar()
            self.pizza_cut_choice.set("Choose your pizza")
            options_pizza = []
            for i in range(len(self.cuts)):
                if list(self.cuts[i]) == [0,0,0]:
                    options_pizza.append(i)
            self.pizza_number_choice = OptionMenu( self.root , self.pizza_cut_choice , *options_pizza )
            self.pizza_number_choice.pack()

    def autoplay_cuts(self):
        self.canvas.delete('all')
        self.canvas.unbind("<Button-1>")
        self.pizza_number_choice.destroy()
        options_pizza = []
        for i in range(len(self.cuts)):
            if list(self.cuts[i]) == [0,0,0]:
                options_pizza.append(i)
        pizza_id, center, theta = self.player_instance.choose_and_cut(self.pizzas, options_pizza, self.preferences[self.customer_id])
        center_x_temp = center[0]
        center_y_temp = center[1]
        if center_x_temp**2 + center_y_temp**2 > 36:
            print("You are trying to choose a center outside the pizza!")
        self.pizza_id = pizza_id
        self.cuts[pizza_id][0] = (self.x + center[0]*self.multiplier)
        self.cuts[pizza_id][1] = (self.y - center[1]*self.multiplier)
        self.cuts[pizza_id][2] = theta
        self.draw_pizza(pizza_id)
        for i in range(8):
            if i==0 or i==4:
                self.draw_cuts([self.cuts[pizza_id][0], self.cuts[pizza_id][1]], theta+i*np.pi/4, color="yellow")
            else:
                self.draw_cuts([self.cuts[pizza_id][0], self.cuts[pizza_id][1]], theta+i*np.pi/4)
        self.button.destroy()
        self.button_1.destroy()
        game_over_indic = 1
        for i in range(len(self.cuts)):
            if self.cuts[i][0] == 0 and self.cuts[i][1] == 0 and self.cuts[i][2] == 0:
                game_over_indic = 0
        if game_over_indic == 0:
            self.button = Button( self.root , text = "Next Customer" , command = self.pizza_choice)
            self.button.place(x=153, y=20)
            results, temp = self.calculator.ratio_calculator(self.pizzas[pizza_id], self.cuts[pizza_id], self.num_toppings, self.multiplier, self.x, self.y )
            self.final_preferences.append(results)
            self.label.config( text = "Pizza chosen "+  str(pizza_id) +". Customer preferences : "+str(np.round(self.preferences[self.customer_id], 2))+ ". Obtained preferences : "+str(np.round(results, 2)))
        else:
            self.button = Button( self.root , text = "See results" , command = self.see_score)
            self.button.place(x=153, y=20)
            self.label.config( text = "Game over")
        self.pizza_choice_order.append(self.pizza_id)
        self.customer_id = self.customer_id + 1

    def choose_cuts(self):
        self.pizza_id = int(self.pizza_cut_choice.get())
        self.canvas.delete('all')
        self.draw_pizza(self.pizza_id)
        self.canvas.unbind("<Button-1>")
        if self.click_indic % 2 ==0:
            self.canvas.bind("<Button-1>", self.clickevent_pizzacenter)
        else:
            self.canvas.bind("<Button-1>", self.clickevent_cut)

    def see_score(self):
        B, C, U, obtained_preferences, center_offsets, slice_amount_metrics = self.calculator.final_score(self.pizzas, self.pizza_choice_order, self.preferences, self.cuts, self.num_toppings, self.multiplier, self.x, self.y)
        list_scores = [('Customer Number', "Pizza Number", "U", "B", "C", "S" , "Center offsets", "Slice metric")]
        with open("summary_log_gui.txt", "w") as f:
            U_total = 0
            B_total = 0
            C_total = 0
            S_total = 0
            for i in range(len(self.pizzas)):
                pizza_id = self.pizza_choice_order[i]
                f.write('\n')
                f.write('\n')
                f.write("Customer " + str(i+1) + " :" )
                f.write('\n')
                f.write("Pizza " + str(pizza_id))
                f.write('\n')
                f.write("Cut at (" + str((self.cuts[pizza_id][0]-self.x)/self.multiplier) + ", " + str((self.cuts[pizza_id][1]-self.y)/self.multiplier) + ") and angle " + str(self.cuts[pizza_id][2]) + "radians.")
                f.write('\n')
                f.write("Center offset : " + str(center_offsets[i]))
                f.write('\n')
                for j in range(24):
                    f.write("Topping " + str(self.pizzas[pizza_id][j][2]) + " at (" + str(self.pizzas[pizza_id][j][0]) + "," + str(self.pizzas[pizza_id][j][1]) + ")")
                    f.write('\n')
                f.write("U : " + str(U[i]))
                f.write('\n')
                f.write("Total : " + str(U[i].sum()))
                f.write('\n')
                U_total = U_total + U[i].sum()
                f.write("B : " + str(B[i]))
                f.write('\n')
                f.write("Total : " + str(B[i].sum()))
                f.write('\n')
                B_total = B_total + B[i].sum()
                f.write("C : " + str(C[i]))
                f.write('\n')
                f.write("Total : " + str(C[i].sum()))
                f.write('\n')
                C_total = C_total + C[i].sum()
                f.write("S : " + str((B[i] - C[i])))
                f.write('\n')
                f.write("Total : " + str((B[i] - C[i]).sum()))
                f.write('\n')
                S_total = S_total + (B[i] - C[i]).sum()
                f.write("Desired Preferences : " + str(self.preferences[i]))
                f.write('\n')
                f.write("Obtained Preferences : " + str(obtained_preferences[i]))
                f.write('\n')
                f.write("Slice by slice amount differences sum : " + str(slice_amount_metrics[i]))
                f.write('\n')
                f.write('\n')
                f.write('\n')
                #list_scores.append((str(i+1), str(pizza_id), str(np.round(U[i].sum(), 2)), str(np.round(B[i].sum(), 2)), str(np.round(C[i].sum(), 2 )), str(np.round((B[i] - C[i]).sum(), 2))))
                list_scores.append((str(i+1), str(pizza_id), str(np.round(U[i].sum(), 2)), str(np.round(B[i].sum(), 2)), str(np.round(C[i].sum(), 2 )), str(np.round((np.sum(B[i], axis = 1) - np.sum(C[i], axis = 1)).sum(), 2)),  str(np.round(center_offsets[i], 2)),  str(np.round(slice_amount_metrics[i], 2)  )))
            f.write("Total Score U : " + str(U_total))
            f.write('\n')
            f.write("Total score B : " + str(B_total))
            f.write('\n')
            f.write("Total score C : " + str(C_total))
            f.write('\n')
            f.write("Total score S : " + str(S_total))
            f.write('\n')
            f.write("Total Slice by slice metric : " + str(np.sum(slice_amount_metrics)))
            f.write('\n')
            f.write("Total center offsets : " + str(np.sum(center_offsets)))
            f.write('\n')
            f.write('\n')
        
        self.root_1 = Tkinter.Tk()
        for i in range(constants.number_of_initial_pizzas + 1):
            for j in range(8):
                if i==1:
                    self.e = Entry(self.root_1, width=10, fg='black',
                                font=('Arial',16,'bold'))
                elif i==2:
                    self.e = Entry(self.root_1, width=10, fg='black',
                                font=('Arial',16,'bold'))
                elif i==3:
                    self.e = Entry(self.root_1, width=10, fg='black',
                                font=('Arial',16,'bold'))
                else:
                    self.e = Entry(self.root_1, width=10, fg='black',
                                font=('Arial',16,'bold'))
                self.e.grid(row=i, column=j)
                self.e.insert(END, list_scores[i][j])
        button_global = Button( self.root_1 , text = "Exit App" , command = self.end_run )
        button_global.place(x=123, y=20)
            

    def end_run(self):
        print("game over")
        exit(1)


    def cut_pizzas(self):
        self.update_indicator = 2
        my_dict = self.convert_to_dict()
        with open("pizza_gui.pkl", "wb") as f:
            pkl.dump(my_dict, f)
        self.button = Button( self.root , text = "See results!!" , command = self.score)
        self.button.place(x=123, y=20)
        if self.type_player != "custom_player":
            #self.pizzas = self.player.create_pizzas(self.num_toppings)      #This line should come in other pizza_game.py. There te self gets updated and transferred here.
            time.sleep(5)
            self.update_variables()
            self.pizzas_drawn = constants.number_of_initial_pizzas
            self.button = Button( self.root , text = "See results!!" , command = self.score)
            self.button.place(x=123, y=20)
            self.draw_pizzas()
        else:
            self.button.destroy()
            self.button = Button( self.root , text = "Autoplay turn" , command = self.auto_pizza)
            self.button.place(x=123, y=20)
            if self.pizza_id >= 10:
                self.button.destroy()
                self.label.config( text = "Congratulations chef all your pizzas are made!!")
                self.button = Button( self.root , text = "Start Serving!!" , command = self.cut_pizzas)
                self.button.place(x=123, y=20)
                my_dict = self.convert_to_dict()
                with open("pizza_gui.pkl", "wb") as f:
                    pkl.dump(my_dict, f)
            else:
                self.draw_pizza(self.pizza_id)
                self.label.config( text = "Make pizza number "+str(self.pizza_id)+ " with "+str(self.num_toppings)+ " types of toppings and "+ str(24-self.topping_id) + " toppings left.")
                #frame = Frame(self.root, width=300, height=250)
                self.canvas.bind("<Button-1>", self.clickevent_topping)
                #frame.pack()
                #ensure it's not in a radius of other topping

    def run(self):  
        self.root = Tkinter.Tk()
        #creating the background canva
        self.canvas=Tkinter.Canvas(self.root, width = 35*self.multiplier, height = 20*self.multiplier, bg='#E5E6DC')
        self.canvas.bind("<Key>", self.clickevent_topping)
        self.canvas.pack(expand='yes',fill='both')
        self.label = Label( self.root , text = "You can customize your pizza here!" )
        self.num_p = StringVar()
        self.num_p.set("Choose number of toppings")
        self.type_p = StringVar()
        self.type_p.set("Choose the player you want")
        self.num_top = OptionMenu( self.root , self.num_p, *self.options_topping )
        self.num_top.pack()
        self.type_players = OptionMenu( self.root , self.type_p, *self.options_player)
        self.type_players.pack()
        # Create Label
        self.draw_pizza(0)
        self.canvas.create_text(self.x, self.y ,text="Hi from FlexPizza!!", fill="navajo white", font=('Helvetica 23 bold'))
        self.button = Button( self.root , text = "Start Game" , command = self.get_pizzas )
        self.button.place(x=123, y=20)
        self.label.pack()
        self.root.mainloop()
    





# Main Function Trigger
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", "-s", default = 5, help="Choose seed number")
    args = parser.parse_args()
    instance = gui(args)
    my_dict = instance.convert_to_dict()
    with open("pizza_gui.pkl", "wb") as f:
        pkl.dump(my_dict, f)
    instance.run()
