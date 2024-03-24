from typing import Tuple, List, Dict, Union # for python 3.8
import logging
import json
from bot.tools import profile
class Plan():
    
    '''Provide map_steps and goals_list for all the start_station & end_station_pairs'''

    # e.g. 

    #         T3-----------<
    #         /              \
    # T1 --<          T4 --- T5
    #         \      /
    #         T2 --<
                
            
    # result map_steps
    # from T1 to T4 : T1 -> T2 -> T4
    # from T1 to T5 : T1 -> T2 -> T4 -> T5 or better, T1 -> T3 -> T5

    
    def __init__(self):
        self.goal_list = []
        self.current_map = None 
        self.dest_station = None 
        self.goal_list = []
        self.map_data = json.load(open(profile.MAP_DATA_JSON , 'r'))['map_data']


    def get_map_station_steps(self, current_map, dest_map, dest_station):
        '''
        Given the global start and dest, find out a list of goals and maps as use them as input
        for the navigation stack.

        retrun map_station_steps -> List of {}
        '''

        # dest_map = self.get_map_from_station(dest_station) # find out what map the station is located on
        if dest_map:
            # get the map_steps(e.g. map1 => map3 => map5 -> (dest station) )
            map_steps = self.find_shortest_map_steps(current_map, dest_map)
            print(f' map_steps : { map_steps} ')

            map_station_steps = []
            if map_steps and len(map_steps) > 0:
                for index, map_step in enumerate(map_steps):
                    if index + 1 < len(map_steps):
                        station_name = self.get_goal_station_on_current_map(map_steps[index], map_steps[index+1])
                        print('A', map_step, station_name )
                        map_station_steps.append({
                            "goal_map_name" : map_step,
                            "goal_station" : station_name,
                            # "goal_position" : station_position
                            }
                        )
                    else:
                        station_name = dest_station
                        print('B', map_step, station_name)
                        map_station_steps.append({
                            "goal_map_name" : map_step,
                            "goal_station" : station_name,
                            # "goal_position" : station_position
                            }
                        )

                
                return map_station_steps

            else:
                logging.error(f'ERROR - unable to obtain map-steps')
        else:
            logging.error(f'ERROR - dest_station not found')
        

    def find_shortest_map_steps(self, start_map, dest_map, visited=[], shortest_path=[]) -> List :
        '''
        Recursivly finding the shortest num of steps(not physical distance) from start to end

        return -> List of map_name(str) 
        '''
        # Base case: if the starting map is the destination map, return a list with only the starting map
        if start_map == dest_map:
            return [start_map]

        # Iterate over the map connection data to find connections for the starting map
        for map in self.map_data:
            # Check if the map_name matches the starting map
            if map['map_name'] == start_map:
                # Iterate over the connected maps in the connection
                for connected_map in map['connect_to']:
                    # Check if the connected map has not been visited before
                    if connected_map['map_name'] not in visited:
                        # Mark the starting map as visited by appending it to the visited list
                        visited.append(start_map)
                        # Recursively call the find_steps function with the connected map as the new starting map
                        steps = self.find_shortest_map_steps(connected_map['map_name'], dest_map, visited, shortest_path)
                        logging.debug('# ', steps)
                        # If a non-empty path is found, check if it is shorter than the current shortest path
                        if steps:
                            # compare all the possible path and keep the one with less steps
                            # if shortest_path is None or len(steps) < len(shortest_path): # !! under review
                            if len(shortest_path)==0 or len(steps) < len(shortest_path):
                                shortest_path = [start_map] + steps
                        # Remove the starting map from the visited list since we are backtracking
                        visited.remove(start_map)

        # Return the shortest path found, if any
        return shortest_path
    

    def find_first_steps(self, start_map, dest_map, visited=[]):
        '''
        Recursivly finding a path from start to end, return the first solution
        '''
        # Base case: if the starting map is the destination map, return a list with only the starting map
        if start_map == dest_map:
            # print('A', start_map )
            return [start_map]

        # Iterate over the map connection data to find connections for the starting map
        for connection in self.map_data:
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
                        steps = self.find_first_steps(connected_map['map_name'], dest_map, visited)
                        # If a non-empty path is found, append the starting map to the beginning of the steps and return the steps
                        if steps:
                            # print('B', [start_map] + steps)
                            return [start_map] + steps
                        # Remove the starting map from the visited list since we are backtracking
                        visited.remove(start_map)

        # If no path is found from the starting map to the destination map, return None
        return None

    def get_station_position(self, map_name, station_name) -> List:
        '''
        Get the position of specific station on a map

        Return [x, y] as a list
        Return [-1, -1] if station is not found
        '''
        result = [-1, -1]
        for map in self.map_data:
            if map['map_name'] == map_name:
                for station in map['stations']:
                    if station['station_name'] == station_name:
                        result = station['position_on_map']
        return result

    def is_station_on_map(self, map_name, station_name) -> bool:
        '''
        Return if the provided station is located on the provided map
        '''
        result = False
        for map in self.map_data:
            if map['map_name'] == map_name:
                for station in map['stations']:
                    if station['station_name'] == station_name:
                        result = True
        return result


    def get_map_from_station(self, station_name) -> Union[str, None]:
        '''

        *KNOWN ISSUE*: since station name is the same as the name of the map they connect to,
        multiple map migtt have stations with the same name.
        ---------------------------------------------------------------------------

        Get the map name of the provided station

        return None if target station_name is not on the DB
        '''
        # result = []
        result = None
        for map in self.map_data:
            for station in map['stations']:
                if station['station_name'] == station_name:
                    # result.append(map['map_name'])
                    result = map['map_name']

        return result


    def get_goal_station_on_current_map(self, current_map, target_map):
        '''
        Get goal station name for travelling to target_map from current_map, 
        
        Return tuple of (name of goal station(str), position of the station on current_map(x, y))
        Return '' and position [-1, -1] if there is no goal station available
        '''
        goal_station = ''
        # position = [-1, -1]
        for map_data in self.map_data:
            if map_data['map_name'] == current_map: # find the current map
                
                for connect_to in map_data['connect_to']:
                    if connect_to['map_name'] == target_map:
                        
                        goal_station = connect_to['map_name'] # name of station should be the same as the name of the map it connects to

                        for station in map_data['stations']:
                            if station['station_name'] == goal_station:
                                position = station['position_on_map']

        return goal_station
        
    


if __name__ == '__main__':
    # print(path.map_connection_data)
    plan = Plan()

    # steps = plan.find_shortest_map_steps('T001', 'T005' )
    # print(f' steps : { steps} ')

    # station = 'S303'
    # resp = plan.get_map_from_station(station)
    # print(f' map from {station} : {resp}')

    # start = 'T002'
    # end = 'T001'
    # resp = plan.get_goal_station_on_current_map( start, end)
    # print(f'Goal station from {start} to {end}: {resp}')

    start_map, end_map, end_station = 'Elements04', 'Elements05', 'S501'
    big_plan = plan.get_map_station_steps(start_map, end_map, end_station )
    print(f'Big_plan from {start_map} to {end_map}: { big_plan} ')

    # resp = plan.get_station_position('T004', 'S403')
    # print(resp)

    # resp = plan.is_station_on_map('Elements04', 'S501')
    # print(resp)



        

