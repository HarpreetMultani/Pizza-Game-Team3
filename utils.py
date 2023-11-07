from turtle import distance
import numpy as np
import constants
import copy
import math
import shapely
from shapely.geometry import LineString, Point

class pizza_calculations():
    def __init__(self):
        self.num_pizzas = constants.number_of_initial_pizzas
        self.rng = np.random.default_rng(int(9))


    def final_score(self, pizzas, pizza_choices, preferences, cuts, num_toppings, multiplier, x, y):
        #calculate U for all 10 pizzas
        #calculate S for all 10 pizzas
        #self.pizzas[self.pizza_id], self.cuts[self.pizza_id], self.num_toppings, self.multiplier, self.x, self.y 
        B = []
        C = []
        U = []
        obtained_preferences = []
        center_offsets = []
        slice_amount_metric = []

        for i in range(len(preferences)):
            pizza_id = pizza_choices[i]
            obtained_pref, slice_areas_toppings = self.ratio_calculator(pizzas[pizza_id], cuts[pizza_id], num_toppings, multiplier, x, y)
            obtained_pref = np.array(obtained_pref)
            slice_areas = self.slice_area_calculator(cuts[pizza_id], multiplier, x, y)
            #Try to fix if theta is 0
            random_pref, temp = self.ratio_calculator(pizzas[pizza_id], [x, y, self.rng.random()*2*np.pi], num_toppings, multiplier, x, y)
            random_pref = np.array(random_pref)
            required_pref = np.array(preferences[i])
            uniform_pref = np.ones((2, num_toppings))*(12/num_toppings)
            b = np.round(np.absolute(required_pref - uniform_pref), 3)
            c = np.round(np.absolute(obtained_pref - required_pref), 3)
            u = np.round(np.absolute(random_pref - uniform_pref), 3)
            B.append(b)
            C.append(c)
            U.append(u)
            obtained_preferences.append(np.round(obtained_pref, 3))
            

            #2 extra metrics here
            x_offset = (cuts[pizza_id][0] - x)/ multiplier
            y_offset = (cuts[pizza_id][1] - y)/ multiplier
            center_offsets.append(np.sqrt(x_offset**2 + y_offset**2))
            sum = 0
            sum_1 = 0
            sum_2 = 0
            for j in range(8):
                if j%2 == 0:
                    sum_2 = sum_2 + slice_areas[j]
                else:
                    sum_1 = sum_1 + slice_areas[j]
            for k in range(num_toppings):
                for l in range(8):
                    if l%2 == 0:
                        sum = sum + abs((preferences[i][1][k]*slice_areas[l]/sum_2) - slice_areas_toppings[l][k])
                    else:
                        sum = sum + abs((preferences[i][0][k]*slice_areas[l]/sum_1) - slice_areas_toppings[l][k])
            slice_amount_metric.append(sum)

        return B, C, U, obtained_preferences, center_offsets, slice_amount_metric


    
    def ratio_calculator(self, pizza, cut_1, num_toppings, multiplier, x, y):
        cut = copy.deepcopy(cut_1)
        result = np.zeros((2, num_toppings))
        cut[0] = (cut[0]-x)/multiplier
        cut[1] = -(cut[1]-y)/multiplier         #Because y axis is inverted in tkinter window
        center = [cut[0], cut[1]]
        theta  = cut[2]                

        if cut[0]**2 + cut[1]**2 > 36:
            print("You are trying to pass a cut with center outside the pizza to the utils function. This may fail.")

        topping_amts = [[0 for x in range(num_toppings)] for y in range(8)]
        for topping_i in pizza:
            top_abs_x = topping_i[0]
            top_abs_y = topping_i[1]
            distance_to_top = np.sqrt((top_abs_x-center[0])**2 + (top_abs_y - center[1])**2)
            theta_edge = np.arctan(0.375 / distance_to_top)
            
            if top_abs_x == center[0]:
                theta_top = 0
            else:
                theta_top = np.arctan((top_abs_y - center[1])/(top_abs_x-center[0]))
            #print(theta, theta_edge, theta_distance, theta_top)
            if (top_abs_x-center[0])<=0 and (top_abs_y-center[1])>=0:
                theta_top = theta_top + np.pi
            if (top_abs_x-center[0])<=0 and (top_abs_y-center[1])<=0:
                theta_top = theta_top + np.pi
            topping_i[2] = int(topping_i[2])
        
            theta_distance = (theta_top - theta + (np.pi * 10))%(2*np.pi)

            if distance_to_top <= 0.375:                                                                    #Chosen center is withing pizza topping. Then by pizza theorem, 2 equal sized topping pieces
                result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + (np.pi*0.375*0.375/2)
                result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + (np.pi*0.375*0.375/2)
            
            elif (theta_edge + theta_distance)*4//np.pi   ==  (-theta_edge + theta_distance)*4//np.pi:
                if (theta_distance*4//np.pi) %2 == 0:
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + (np.pi*0.375*0.375)
                else:
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + (np.pi*0.375*0.375)
                topping_amts[int(theta_distance*4//np.pi)][int(topping_i[2]) - 1] = topping_amts[int(theta_distance*4//np.pi)][int(topping_i[2]) - 1] + (np.pi*0.375*0.375)
            
            elif (theta_edge + theta_distance)*4//np.pi ==  (-theta_edge + theta_distance)*4//np.pi + 1:    #Topping falls in 2 slices
                if (theta_distance*4//np.pi) %2 == 0:
                    small_angle_theta = min(theta_distance%(np.pi/4), (np.pi/4 - (theta_distance%(np.pi/4))))
                    phi = np.arcsin(distance_to_top*np.sin(small_angle_theta)/0.375)
                    area_smaller = (np.pi/2 - phi - (np.cos(phi)*np.sin(phi)))*0.375*0.375
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + (np.pi*0.375*0.375) - area_smaller
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + area_smaller
                else:
                    small_angle_theta = min(theta_distance%(np.pi/4), (np.pi/4 - (theta_distance%(np.pi/4))))
                    phi = np.arcsin(distance_to_top*np.sin(small_angle_theta)/0.375)
                    area_smaller = (np.pi/2 - phi - (np.cos(phi)*np.sin(phi)))*0.375*0.375
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + area_smaller
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + (np.pi*0.375*0.375) - area_smaller
                if small_angle_theta == theta_distance%(np.pi/4):
                    topping_amts[int(theta_distance*4//np.pi)][int(topping_i[2]) - 1] = topping_amts[int(theta_distance*4//np.pi)][int(topping_i[2]) - 1] + (np.pi*0.375*0.375) - area_smaller
                    topping_amts[int(((theta_distance*4//np.pi) - 1)%8)][int(topping_i[2]) - 1] = topping_amts[int(((theta_distance*4//np.pi) - 1)%8)][int(topping_i[2]) - 1] + area_smaller
                else:
                    topping_amts[int(theta_distance*4//np.pi)][int(topping_i[2]) - 1] = topping_amts[int(theta_distance*4//np.pi)][int(topping_i[2]) - 1] + (np.pi*0.375*0.375) - area_smaller
                    topping_amts[int(((theta_distance*4//np.pi) + 1)%8)][int(topping_i[2]) - 1] = topping_amts[int(((theta_distance*4//np.pi) + 1)%8)][int(topping_i[2]) - 1] + area_smaller
            
            
            
            elif (theta_edge + theta_distance)*4//np.pi ==  (-theta_edge + theta_distance)*4//np.pi + 2:    #Topping falls in 3 slices
                small_angle_theta_1 = theta_distance%(np.pi/4)
                small_angle_theta_2 = (np.pi/4)-small_angle_theta_1
                phi_1 = np.arcsin(distance_to_top*np.sin(small_angle_theta_1)/0.375)
                phi_2 = np.arcsin(distance_to_top*np.sin(small_angle_theta_2)/0.375)
                area_smaller_1 = (np.pi/2 - phi_1 - (np.cos(phi_1)*np.sin(phi_1)))*0.375*0.375
                area_smaller_2 = (np.pi/2 - phi_2 - (np.cos(phi_2)*np.sin(phi_2)))*0.375*0.375
                if (theta_distance*4//np.pi) %2 == 0:
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + (np.pi*0.375*0.375) - area_smaller_1 - area_smaller_2
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + area_smaller_1 + area_smaller_2
                else:
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + area_smaller_1 + area_smaller_2
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + (np.pi*0.375*0.375) - area_smaller_1 - area_smaller_2
                topping_amts[int(theta_distance*4//np.pi)][int(topping_i[2]) - 1] = topping_amts[int(theta_distance*4//np.pi)][int(topping_i[2]) - 1] + (np.pi*0.375*0.375) - area_smaller_1 - area_smaller_2
                topping_amts[int(((theta_distance*4//np.pi) + 1)%8)][int(topping_i[2]) - 1] = topping_amts[int(((theta_distance*4//np.pi) + 1)%8)][int(topping_i[2]) - 1] + area_smaller_2
                topping_amts[int(((theta_distance*4//np.pi) - 1)%8)][int(topping_i[2]) - 1] = topping_amts[int(((theta_distance*4//np.pi) - 1)%8)][int(topping_i[2]) - 1] + area_smaller_1
            
            
            else:       #just see the pattern from the above 2, draw some diagrams and you'll see how this came. Find areas of all small sectors, then minus accordingly later. This also takes care of the
                # above conditions. It's a general case, but let's have everything here because why not
                small_angle_theta = theta_distance%(np.pi/4)
                small_areas_1 = []
                small_areas_2 = []
                while small_angle_theta<theta_edge:
                    phi = np.arcsin(distance_to_top*np.sin(small_angle_theta)/0.375)
                    area_smaller = (np.pi/2 - phi - (np.cos(phi)*np.sin(phi)))*0.375*0.375
                    small_areas_1.append(area_smaller)
                    small_angle_theta = small_angle_theta + (np.pi/4)
                for i in range(len(small_areas_1)-1):
                    small_areas_1[i] = small_areas_1[i] - small_areas_1[i+1]
                
                small_angle_theta = np.pi/4 - (theta_distance%(np.pi/4))
                while small_angle_theta<theta_edge:
                    phi = np.arcsin(distance_to_top*np.sin(small_angle_theta)/0.375)
                    area_smaller = (np.pi/2 - phi - (np.cos(phi)*np.sin(phi)))*0.375*0.375
                    small_areas_2.append(area_smaller)
                    small_angle_theta = small_angle_theta + (np.pi/4)
                for i in range(len(small_areas_2)-1):
                    small_areas_2[i] = small_areas_2[i] - small_areas_2[i+1]

                area_center = (np.pi*0.375*0.375) - np.sum(small_areas_1) - np.sum(small_areas_2)       #area of topping in slice where it's center lies.
                
                #To calculate the metric for slice areas
                topping_amts[int(theta_distance*4//np.pi)][int(topping_i[2]) - 1] = topping_amts[int(theta_distance*4//np.pi)][int(topping_i[2]) - 1] + area_center
                for i in range(len(small_areas_1)):
                    topping_amts[int(((theta_distance*4//np.pi) - (i+1))%8)][int(topping_i[2]) - 1] = topping_amts[int(((theta_distance*4//np.pi) - (i+1))%8)][int(topping_i[2]) - 1] + small_areas_1[i]
                for i in range(len(small_areas_2)):
                    topping_amts[int(((theta_distance*4//np.pi) + (i+1))%8)][int(topping_i[2]) - 1] = topping_amts[int(((theta_distance*4//np.pi) + (i+1))%8)][int(topping_i[2]) - 1] + small_areas_2[i]

                for i in range(len(small_areas_1)):
                    if i%2 == 1:
                        area_center = area_center + small_areas_1[i]
                    
                for i in range(len(small_areas_2)):
                    if i%2 == 1:
                        area_center = area_center + small_areas_2[i]
                if (theta_distance*4//np.pi) %2 == 0:
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + area_center
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + (np.pi*0.375*0.375) - area_center
                else:
                    result[1][int(topping_i[2]) - 1] = result[1][int(topping_i[2]) - 1] + (np.pi*0.375*0.375) - area_center
                    result[0][int(topping_i[2]) - 1] = result[0][int(topping_i[2]) - 1] + area_center

        for i in range(num_toppings):
            result[0][i] = result[0][i]/(np.pi*0.375*0.375)
            result[1][i] = result[1][i]/(np.pi*0.375*0.375)
        return result, topping_amts

    def triangle_area(self, a,b,c):
        x1 = a[0]
        y1 = a[1]
        x2 = b[0]
        y2 = b[1]
        x3 = c[0]
        y3 = c[1]
        return (0.5*abs((x1*(y2 - y3)) + (x2*(y3 - y1)) + (x3*(y1 - y2))))

    def slice_area_calculator(self, cut_1, multiplier, x, y):
        center_x = (copy.deepcopy(cut_1[0])-x)/multiplier
        center_y = -(copy.deepcopy(cut_1[1])-y)/multiplier
        center = [center_x, center_y]
        theta1 = copy.deepcopy(cut_1[-1])
        circ_pts = [0,0,0,0,0,0,0,0]
        ints_pts = [0,0,0,0,0,0,0,0]
        area_slice = [0,0,0,0,0,0,0,0]
        for i in range(4):
            theta = theta1 + i*np.pi/4
            dist_centers = math.sqrt((center[0])**2 + (center[1])**2)
            if center[0] == 0:
                angle_centerline = 0
            else:
                angle_centerline = math.atan((center[1])/(center[0]))
            theta_diag = angle_centerline - theta
            sinin_1 = math.asin(math.sin(theta_diag) * dist_centers/6)
            phi_1 = theta_diag - sinin_1
            phi_2 = theta_diag - math.pi + sinin_1
            if math.sin(theta_diag)==0:
                point_1 = [6*math.cos(angle_centerline)  ,  6*math.sin(angle_centerline)]
                point_2 = [-6*math.cos(angle_centerline)  , -6*math.sin(angle_centerline)]
            else:
                y1 = 6*math.sin(phi_1)/math.sin(theta_diag)
                y2 = 6*math.sin(phi_2)/math.sin(theta_diag)
                #point_1 = [center[0] - y1*math.sin(theta + angle_centerline) , center[1] - y1*math.cos(theta + angle_centerline)]
                #point_2 = [center[0] - y2*math.sin(theta + angle_centerline) , center[1] - y2*math.cos(theta + angle_centerline)]
                if center[0] < 0:
                    point_1 = [center[0] - y1*math.cos(angle_centerline - theta_diag) , center[1] - y1*math.sin(angle_centerline - theta_diag)]
                    point_2 = [center[0] - y2*math.cos(angle_centerline - theta_diag) , center[1] - y2*math.sin(angle_centerline - theta_diag)]
                else:
                    point_1 = [center[0] + y1*math.cos(angle_centerline - theta_diag) , center[1] + y1*math.sin(angle_centerline - theta_diag)]
                    point_2 = [center[0] + y2*math.cos(angle_centerline - theta_diag) , center[1] + y2*math.sin(angle_centerline - theta_diag)]
            circ_pts[i] = point_1
            circ_pts[i+4] = point_2
        
        for i in range(8):
            line1 = LineString(Point(circ_pts[i]).coords[:] + Point(center).coords[:])
            line2 = LineString(Point(circ_pts[(i+1)%8]).coords[:] + Point([0,0]).coords[:])
            line3 = LineString(Point(circ_pts[i]).coords[:] + Point([0,0]).coords[:])
            line4 = LineString(Point(circ_pts[(i+1)%8]).coords[:] + Point(center).coords[:])
            int_pt_1 = line1.intersection(line2)
            int_pt_2 = line3.intersection(line4)
            if hasattr(int_pt_1, "x"):
                int_pt = [int_pt_1.x, int_pt_1.y]
                origin = [0,0]
                area_1 = self.triangle_area(origin, int_pt, circ_pts[i])
                area_2 = self.triangle_area(center, circ_pts[(i+1)%8], int_pt)
                product_magnitudes = np.sqrt(circ_pts[i][0]**2 + circ_pts[i][1]**2)*np.sqrt(circ_pts[(i+1)%8][0]**2 + circ_pts[(i+1)%8][1]**2)
                theta_sector = math.acos(np.round( np.dot(circ_pts[i], circ_pts[(i+1)%8]), 4 )/np.round(product_magnitudes, 4))
                area_sector = theta_sector*36/2
                area_slice[i] = area_sector + area_2 - area_1
            elif hasattr(int_pt_2, "x"):
                int_pt = [int_pt_2.x, int_pt_2.y]
                area_1 = self.triangle_area([0,0], int_pt, circ_pts[(i+1)%8])
                area_2 = self.triangle_area(center, int_pt, circ_pts[i])
                product_magnitudes = np.sqrt(circ_pts[i][0]**2 + circ_pts[i][1]**2)*np.sqrt(circ_pts[(i+1)%8][0]**2 + circ_pts[(i+1)%8][1]**2)
                theta_sector = math.acos(np.round( np.dot(circ_pts[i], circ_pts[(i+1)%8]), 4 )/np.round(product_magnitudes, 4))
                area_sector = theta_sector*36/2
                area_slice[i] = area_sector + area_2 - area_1
            else:
                area_1 = self.triangle_area([0,0], center, circ_pts[(i+1)%8])
                area_2 = self.triangle_area(center, [0,0], circ_pts[i])
                product_magnitudes = np.sqrt(circ_pts[i][0]**2 + circ_pts[i][1]**2)*np.sqrt(circ_pts[(i+1)%8][0]**2 + circ_pts[(i+1)%8][1]**2)
                theta_sector = math.acos(np.round( np.dot(circ_pts[i], circ_pts[(i+1)%8]), 4 )/np.round(product_magnitudes, 4))
                area_sector = theta_sector*36/2
                if theta_sector>=np.pi/4:
                    area_slice[i] = area_sector + area_2 + area_1
                else:
                    area_slice[i] = area_sector - area_2 - area_1
        return area_slice
                    




    def clash_exists(x, y, pizza, topping_id):
        current_pizza = np.array(pizza)
        current_topping = np.array([x, y])
        current_distance = np.linalg.norm(current_topping)
        if current_distance + 0.375 > 6:
            return True
        if topping_id == 0:
            return False
        current_pizza = current_pizza[:topping_id]
        current_pizza = current_pizza[:, :2]
        current_topping = np.array([x, y])
        current_topping = np.tile(current_topping,(current_pizza.shape[0],1))
        distances = np.sqrt(np.sum((current_pizza- current_topping)**2,axis=1))
        min_distance = np.min(distances)
        if min_distance < 0.75:
            return True
        return False