import random
import string

world_size = (24, 24)

pokemon_types = ["normal", "fighting", "flying", "poison",
                 "ground", "rock", "bug", "ghost",
                 "steel", "fire", "water", "grass",
                 "electric", "psychic", "ice", "dragon",
                 "dark", "fairy"]
num_gyms = 8
num_points_of_interest = 8
num_major_dungeons = 4
subregion_len = 3
subregion_width = 3
subsample_region_len = int(world_size[0] / subregion_len)
subsample_region_width = int(world_size[1] / subregion_width)
padding = 1


bcolors = ['\033[95m', '\033[96m', '\033[94m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m', '\033[4m']


def print_map(towns: {}):
    for ycoord in range(world_size[1]):
        line_to_print = ""
        for xcoord in range(world_size[0]):
            # min_poi = -1
            # min_distance = float("inf")
            text_to_print = "_"
            # for j in range(len(pois)):
            #     if pois[j]["coordinates"] == (xcoord, ycoord):
            #         min_poi = j
            #         text_to_print = "_"
            #         break
            #     distance = ((pois[j]["coordinates"][0] - xcoord) ** 2) + ((pois[j]["coordinates"][1] - ycoord) ** 2)
            #     if distance < min_distance:
            #         min_distance = distance
            #         min_poi = j
            for town in towns:
                if town["coordinates"] == (xcoord, ycoord):
                    text_to_print = town["map_character"]
                    break
            bcolor_index = int((xcoord/subsample_region_width)) + int((ycoord/subsample_region_len))
            color = bcolors[bcolor_index]
            line_to_print += f"{color}|{text_to_print}"
        print(line_to_print + "|")


# on our world grid, place our points of interest.
# points of interest determine the typing of the surrounding area, may contain dungeons
# points_of_interest = []
# towns = []
# poi_types = random.sample(pokemon_types, num_points_of_interest)
# poi_locations = random.sample(range(world_size[0]*world_size[1]), num_points_of_interest)
# for i in range(num_points_of_interest):
#     remainder = poi_locations[i] % world_size[0]
#     new_poi = {
#         "coordinates": (remainder, (poi_locations[i] - remainder)/world_size[0]),
#         "type": poi_types[i],
#     }
#     # print(new_poi)
#     points_of_interest.append(new_poi)

# generate towns
towns = []
# print(subsample_region_len, subsample_region_width)
random_sit_out = (random.choice(range(subregion_len)), random.choice(range(subregion_width)))
home_subsample_region = (random.choice([x for x in range(subregion_len) if (x != random_sit_out[0])]),
                         random.choice([x for x in range(subregion_width) if (x != random_sit_out[1])]))
# print(random_sit_out)
print(home_subsample_region, "home")
for i in range(subregion_len):
    # print(i)
    for j in range(subregion_width):
        # print(j)
        if (i, j) == random_sit_out:
            continue
        new_gym = {
            # int cast here is not needed but it makes pycharm not complain lmao
            "coordinates": (int(random.choice(range(padding + subsample_region_width * i,
                                                    subsample_region_width * (i+1) - padding))),
                            int(random.choice(range(padding + subsample_region_len * j,
                                                    subsample_region_len * (j + 1) - padding)))),
            "has_gym": True,
            "map_character": "G",
            "subregion": (i, j),
            "gym_number": -1
        }
        towns.append(new_gym)

        if (i, j) != home_subsample_region:
            continue
        # generate the home town in its region, excluding the padded area around the first gym

        excluded_area_x = range(new_gym["coordinates"][0] - padding, new_gym["coordinates"][0] + padding + 1)
        excluded_area_y = range(new_gym["coordinates"][1] - padding, new_gym["coordinates"][1] + padding + 1)
        home_generator_xcoord = [x for x in range(padding + subsample_region_width * i,
                                                  subsample_region_width * (i+1) - padding)
                                 if (x not in excluded_area_x)]
        home_generator_ycoord = [y for y in range(padding + subsample_region_len * j,
                                                  subsample_region_len * (j + 1) - padding)
                                 if (y not in excluded_area_y)]
        print(excluded_area_x, excluded_area_y)
        hometown = {
            "coordinates": (random.choice(home_generator_xcoord),
                            random.choice(home_generator_ycoord)),
            "has_gym": False,
            "map_character": 'H',
            "subregion": (i, j)
        }
        print(hometown)
        towns.append(hometown)

# next todo:
# write a path creation function
# it should: prefer already created routes
# choose from a group of types for tiebreaks, for that one set of routes
# avoid 2x squares, no filling in "corners" - check diagonally for routes before placing one.
#   * if you see one, move onto it, we can guarantee it moves in the direction we care about for at least one tile

# now that we have a full set of gyms with locations, and a starting town, we can generate our routes.
# start by mapping all gyms and the home town to a dictionary that holds based on coordinates, for easy access while
# traversing the map graph

# test code for cube validation
# towns.append({
#             "coordinates": (hometown["coordinates"][0] - 1, hometown["coordinates"][1] + 1),
#             "has_gym": False,
#             "map_character": 'R',
#             "subregion": hometown["subregion"]
#         })
# towns.append({
#             "coordinates": (hometown["coordinates"][0], hometown["coordinates"][1] + 1),
#             "has_gym": False,
#             "map_character": 'R',
#             "subregion": hometown["subregion"]
#         })
valid_map_coordinates = set()
for town in towns:
    valid_map_coordinates.add(town["coordinates"])


# Some helper functions for world traversal
def get_neighbors(current_coordinates: (int,int)) -> {}:
    # Top left corner is 0,0 for the sake of drawing
    all_neighbors = [
        (current_coordinates[0], current_coordinates[1] + 1),  # S
        (current_coordinates[0] + 1, current_coordinates[1]),  # E
        (current_coordinates[0], current_coordinates[1] - 1),  # N
        (current_coordinates[0] - 1, current_coordinates[1])   # W
    ]
    # print("neighbors", all_neighbors)
    neighbors = {}
    for neighbor_index in range(len(all_neighbors)):
        # bounds check - if we fail it, just don't return the square as a neighbor
        if 0 > all_neighbors[neighbor_index][0] or all_neighbors[neighbor_index][0] >= world_size[0] \
                or 0 > all_neighbors[neighbor_index][1] or all_neighbors[neighbor_index][1] >= world_size[1]:
            continue
        neighbor_info = {}
        if all_neighbors[neighbor_index] in valid_map_coordinates:
            neighbor_info["valid"] = True
            neighbor_info["already_exists"] = True
        else:
            neighbor_info["already_exists"] = False
            # This is to avoid "cube" routes. We NEVER want a route that does this, with C as our current spot:
            # |_|_|_|
            # |_|C|R|
            # |_|R|R|
            # so, we see if N can be a valid point. Check the X's of the 3x3 area around C to see if we have neighbors
            # |_|_|_|
            # |_|C|X|
            # |_|N|X|
            direction_vector = (all_neighbors[neighbor_index][0] - current_coordinates[0], all_neighbors[neighbor_index][1] - current_coordinates[1])
            check_positive = not ((all_neighbors[neighbor_index][0] + direction_vector[1], all_neighbors[neighbor_index][1] + direction_vector[0])
                                  in valid_map_coordinates and
                                  (current_coordinates[0] + direction_vector[1], current_coordinates[1] + direction_vector[0])
                                  in valid_map_coordinates)
            # and the opposite side
            # |_|_|_|
            # |X|C|_|
            # |X|N|_|
            check_negative = not ((all_neighbors[neighbor_index][0] - direction_vector[1], all_neighbors[neighbor_index][1] - direction_vector[0])
                                  in valid_map_coordinates and
                                  (current_coordinates[0] - direction_vector[1], current_coordinates[1] - direction_vector[0])
                                  in valid_map_coordinates)
            # If both pass, we can validly say we won't create a cube by placing a route here
            if check_positive and check_negative:
                neighbor_info["valid"] = True
            else:
                neighbor_info["valid"] = False
        neighbors[all_neighbors[neighbor_index]] = neighbor_info
    return neighbors


# order gyms based on a subregion traversal
subregions_to_gyms = {}
for i in range(len(towns)):
    if not towns[i]["has_gym"]:
        continue
    subregions_to_gyms[towns[i]["subregion"]] = i

cardinal_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

gym_number = 0


def recursive_visit_gym(subregion: (int, int)):
    global gym_number
    gym_number += 1
    # print("rvg", gym_number, subregion)
    towns[subregions_to_gyms[subregion]]["gym_number"] = gym_number

    adjacent_subregions = []
    for direction in cardinal_directions:
        new_subregion = (direction[0] + subregion[0], direction[1] + subregion[1])
        if 0 > new_subregion[0] or new_subregion[0] >= subregion_len \
                or 0 > new_subregion[1] or new_subregion[1] >= subregion_width:
            continue
        adjacent_subregions.append(new_subregion)
    # print(adjacent_subregions)

    while len(adjacent_subregions):
        index_to_traverse = random.choice(range(len(adjacent_subregions)))
        if adjacent_subregions[index_to_traverse] in subregions_to_gyms:
            # print("new index", adjacent_subregions[index_to_traverse])
            gym_index = subregions_to_gyms[adjacent_subregions[index_to_traverse]]
            if towns[gym_index]["gym_number"] == -1:
                recursive_visit_gym(adjacent_subregions[index_to_traverse])

        del adjacent_subregions[index_to_traverse]


# this is fragile to reference hometown here by I don't play by the rules lol
recursive_visit_gym(hometown["subregion"])
for i in range(len(towns)):
    if not towns[i]["has_gym"]:
        continue
    towns[i]["map_character"] = str(towns[i]["gym_number"])


def find_gym(number) -> (int, int):
    for gym_town in towns:
        if not gym_town["has_gym"]:
            continue
        if gym_town["gym_number"] == number:
            return gym_town["coordinates"]
    return -1, -1


# woo time for route generation
# long story short, greedy a* paths to the next gym for now.
# tiebreak based on already_exists, validity, then randomly?
#   Alternative to randomness:
#       choose a method between horiz-first, vert-first, and probability-random to make different shaped paths
#       I'll implement that after route gen is working

# store our routes for later steps (town generation pt 2)
route_zones = []


class RouteNode:
    # blatantly stolen and adapted from https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
    # because I'm too lazy to rewrite the wheel
    def __init__(self, parent=None, position=None, already_created=False):
        self.parent = parent
        self.position = position
        self.already_created = already_created

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

    @staticmethod
    def astar(start, end):

        # Create start and end node
        start_node = RouteNode(None, start)
        start_node.g = start_node.h = start_node.f = 0
        end_node = RouteNode(None, end)
        end_node.g = end_node.h = end_node.f = 0

        # Initialize both open and closed list
        open_list = []
        closed_list = []

        # Add the start node
        open_list.append(start_node)

        # Loop until you find the end
        while_iterations = 0
        while len(open_list) > 0:

            # Get the current node
            while_iterations += 1
            if while_iterations % 10000 == 0:
                print(while_iterations, len(open_list), len(closed_list))
            current_node = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            # Pop current off open list, add to closed list
            open_list.pop(current_index)
            closed_list.append(current_node)

            # Found the goal
            if current_node == end_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]  # Return reversed path

            # Generate children
            neighbors = get_neighbors((current_node.position[0], current_node.position[1]))
            children = []
            for neighbor in neighbors.keys():
                if neighbors[neighbor]["valid"]:
                    children.append(RouteNode(current_node, (neighbor[0], neighbor[1]),
                                              neighbors[neighbor]["already_exists"]))

            for child in children:

                # Child is on the closed list
                found_closed = False
                for closed_child_index in range(len(closed_list)):
                    if child == closed_list[closed_child_index]:
                        found_closed = True
                        break
                if found_closed:
                    continue
                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = (abs(child.position[0] - end_node.position[0])) + abs(
                            (child.position[1] - end_node.position[1])) + (0 if child.already_created else 2)
                child.f = child.g + child.h

                # Child is already in the open list
                found_open = False
                previous_node_index = -1
                for open_node_index in range(len(open_list)):
                    if child == open_list[open_node_index] and child.g > open_list[open_node_index].g:
                        found_open = True
                        previous_node_index = open_node_index
                        break
                if found_open:
                    continue
                if previous_node_index == -1:
                    # print("new node")
                    open_list.append(child)
                else:
                    print("replacing dupe")
                    open_list[previous_node_index] = child


route_number = 0

print_map(towns)


def add_route(route: []):
    global route_number
    route_number += 1
    for zone in route:
        valid_map_coordinates.add(zone)
    for route_zone in route:
        route_zones.append({
            "coordinates": route_zone,
            "route_number": route_number,
            "map_character": string.ascii_lowercase[route_number-1]
        })


add_route(RouteNode.astar(hometown["coordinates"], find_gym(1)))
for i in range(1, 8):
    print("generating route ", i, i+1)
    add_route(RouteNode.astar(find_gym(i), find_gym(i+1)))

print(len(route_zones))
print_map(towns + route_zones)







