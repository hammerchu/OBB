from bot.tools import path

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
        '''
        pass


if __name__ == '__main__':
    print(path.map_connection_data)
        

