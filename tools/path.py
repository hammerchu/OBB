import json
from bot.tools import profile
import os
'''

==========OBSELED, integrated into Plan Class=========

Return a goal_list for all the start_station & end_station_pairs

e.g. 

        T3-----------<
        /              \
T1 --<          T4 --- T5
        \      /
        T2 --<
               
        

from T1 to T4 : T1 -> T2 -> T4
from T1 to T5 : T1 -> T2 -> T4 -> T5 or better, T1 -> T3 -> T5
'''


map_connection_data = json.load(open(profile.MAP_DATA_JSON , 'r'))['map_connection_data']

def get_station_data(station):
    # Return the first map data that match the start_station name
    # list -> dict as the input iterator from map_connection_data is a list
    return dict(list(filter(lambda x: x['map_name'] == station, map_connection_data))[0])

# def find_path(start_station, dest_sdtation):
    
#     start_map_dict = get_station_data(start_station)

#     for conn_map in start_map_dict['connect_to']:
        
#         print(conn_map['map_name'])

def find_first_steps(start_map, dest_map, visited=[]):
    '''
    Recursivly finding a path from start to end
    '''
    # Base case: if the starting map is the destination map, return a list with only the starting map
    if start_map == dest_map:
        print('A', start_map )
        return [start_map]

    # Iterate over the map connection data to find connections for the starting map
    for connection in map_connection_data:
        # Check if the map_name matches the starting map
        if connection['map_name'] == start_map:
            # Iterate over the connected maps in the connection
            for connected_map in connection['connect_to']:
                # Check if the connected map has not been visited before
                if connected_map['map_name'] not in visited:
                    # Mark the starting map as visited by appending it to the visited list
                    visited.append(start_map)
                    # print(f' visited : { visited} ')
                    
                    # Recursively call the find_steps function with the connected map as the new starting map
                    steps = find_first_steps(connected_map['map_name'], dest_map, visited)
                    # If a non-empty path is found, append the starting map to the beginning of the steps and return the steps
                    if steps:
                        print('B', [start_map] + steps)
                        return [start_map] + steps
                    # Remove the starting map from the visited list since we are backtracking
                    visited.remove(start_map)

    # If no path is found from the starting map to the destination map, return None
    return None



def find_shortest_steps(start_map, dest_map, visited=[], shortest_path=None):
    '''
    Recursivly finding the shortest num of steps(not physical distance) from start to end
    '''
    # Base case: if the starting map is the destination map, return a list with only the starting map
    if start_map == dest_map:
        return [start_map]

    # Iterate over the map connection data to find connections for the starting map
    for connection in map_connection_data:
        # Check if the map_name matches the starting map
        if connection['map_name'] == start_map:
            # Iterate over the connected maps in the connection
            for connected_map in connection['connect_to']:
                # Check if the connected map has not been visited before
                if connected_map['map_name'] not in visited:
                    # Mark the starting map as visited by appending it to the visited list
                    visited.append(start_map)
                    # Recursively call the find_steps function with the connected map as the new starting map
                    steps = find_shortest_steps(connected_map['map_name'], dest_map, visited, shortest_path)
                    # logger.debug('# ', steps)
                    # If a non-empty path is found, check if it is shorter than the current shortest path
                    if steps:
                        # compare all the possible path and keep the one with less steps
                        if shortest_path is None or len(steps) < len(shortest_path):
                            shortest_path = [start_map] + steps
                    # Remove the starting map from the visited list since we are backtracking
                    visited.remove(start_map)

    # Return the shortest path found, if any
    return shortest_path


if __name__ == '__main__':
    steps = find_shortest_steps('T001', 'T005', )
    print(f' steps : { steps} ')