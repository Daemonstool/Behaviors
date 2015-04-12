import basebehavior.behaviorimplementation
import time

class TeamPyborgLookatball_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    def implementation_init(self):

        self.__nao = self.body.nao(0)
        self.new_detection = True
        self.last_recogtime = time.time()
        self.position = [0.5,0.5]
        self.lastlooktime = 0
        self.lookinterval = 1
        self.lostballtime = 3
        print "start look at ball"
        
    # get ball vision information
    def update_obs(self):
        if (self.m.n_occurs('ball_info') > 0):
            (recogtime, observation) = self.m.get_last_observation('ball_info')
            if (recogtime > self.last_recogtime):
                self.last_recogtime = recogtime
                self.position = observation['view_position']
                self.new_detection = True
    
    def implementation_update(self):
    
        self.update_obs()
		# every second re-adjust the head to where the ball is
        if (time.time() - self.lastlooktime) > self.lookinterval:
            self.__nao.look_at(self.position[0], self.position[1])
            self.lastlooktime = time.time()
        
        # lost ball
        if time.time() - self.last_recogtime > self.lostballtime:
            print "Finished look at ball: failure"
            self.set_finished()
            return



