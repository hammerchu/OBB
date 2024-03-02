

class Plan():
    '''
    Create plans and connecting mini maps


    '''
    def __init__(self):
        self.goal_list = []
        self.start_station = None 
        self.dest_station = None 
        self.goal_list = []

    def prepare_goal_list(self, start_station, dest_station):
        self.start_station = start_station 
        self.dest_station = dest_station 
        '''
        Given the global start and dest, find out a list of goals and maps as use them as input
        for the navigation stack.

        e.g. 
        [
            {
            "index" : 0
            "map_name" : "KW182",
            "goal_lng" : 23.4553546
            "goal_lat" : 234.123244
            },
            {
            "index" : 1
            "map_name" : "KW123",
            "goal_lng" : 23.3445352
            "goal_lat" : 234.123236
            },
        ]
        '''
        pass

        

