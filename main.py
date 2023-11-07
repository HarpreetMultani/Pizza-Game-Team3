#autoplayer_number is an argument
#chooser_number is an argument
#chosen auto pizza generator is an argument


import argparse
from pizza_gui import gui
from pizza_no_gui import no_gui

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", "-g", default="True", help="GUI")
    parser.add_argument("--interface_size", "-sz", default=40, help="GUI Size")
    parser.add_argument("--seed", "-s", default=48, help="General seed for your own functions")
    parser.add_argument("--gen_100_seed", "-s100", default=45, help="Seed for generating 100 preferences")
    parser.add_argument("--gen_10_seed", "-s10", default=50, help="Seed for generating 10 preferences")
    #parser.add_argument("--autoplayer_number", "-a_num", default=0, help="Which player is the autoplayer")
    parser.add_argument("--generator_number", "-g_num", default=0, help="Which player is the preference generator")
    #only for no gui case
    parser.add_argument("--player", "-p", default=1, help="Team number playing the game if no gui")
    parser.add_argument("--num_toppings", "-num_top", default=4, help="Total different types of toppings")
    
    parser.add_argument("--tournament", "-tmnt", default=False, help="Is this a tournament run or not")
    args = parser.parse_args()
    args.tournament = "False"
    if args.gui == "True":
        instance = gui(args)
        instance.run()
    else:
        instance = no_gui(args)
        instance.run()
