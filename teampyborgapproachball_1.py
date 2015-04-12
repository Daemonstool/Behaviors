import basebehavior.behaviorimplementation
import time

# sequential behavior: looks where the ball is and afterwards re-adjust its head. This process is repeated
class TeamPyborgApproachball_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    def implementation_init(self):

        self.__nao = self.body.nao(0)
        self.role = (self.m.get_last_observation('player')[1])['role']
        # Observation variables
        self.last_recogtime = time.time()
        self.last_detection = None
        self.new_detection = False
        self.last_look_time = time.time()
        
        # Possible states: "LOOK", "WALK", "DONE"
        self.state = "LOOK"
        # ball position in camera view
        self.position = [0.5, 0.5]
        # first walk
        self.firstWalk = True
        
        # set position stop criteria
        if self.role == "attacker":
            self.min_pitch = 0.5
            self.acc_look = 0.05
        else:
            self.min_pitch = -0.3
            self.acc_look = 0.1
            
        # acc_view needs to be smaller than acc_walk
        self.center_yaw = 0
        self.acc_view = 0.05

        # ensure vision is loaded
        print "start approach"
        #self.__nao.say("start approach")
        
    # Get view_position_ball from memory
    def update_obs(self):
        if (self.m.n_occurs('ball_info') > 0):
            (recogtime, observation) = self.m.get_last_observation('ball_info')
            if (recogtime > self.last_recogtime): #observation['large_enough']
                self.last_recogtime = recogtime
                self.position = observation['view_position']
                self.new_detection = True
    
    # returns true when var is between val+/-acc
    def within_accuracy(self, var, val, acc):
        return (var < val+acc and var > val-acc)    
   
    # update loop        
    def implementation_update(self):
        # check colorblob detection
        self.new_detection = False
        self.update_obs()

        # get head pitch and yaw
        
        yaw, pitch = self.__nao.get_angles(['HeadYaw', 'HeadPitch'], True)  
        # allowed distance from the center of view to keep walking in percentage of pixels
        # to-do account for cyclopse view size!
        acc_walk = 0.1 #0.4 * abs(self.min_pitch - pitch) + 0.05
        
        # stop on touch on tactile button
        if self.m.n_occurs('stop_behaviors') > 0 and not self.m.get_last_observation('stop_behaviors')[1]['restarted']:
            print "Finished approach: stopped on touch"
            self.__nao.stopwalk()
            self.set_finished()
            return
         
        # Stop criteria failure: No ball in sight
        if (time.time() - self.last_recogtime) >= 2:
            print "Finished approach: Failure"
            # stop all approach ball actions
            self.__nao.stopwalk()
            # set error flag in memory
            self.m.add_item('lost_ball', time.time(), {'restarted': False})
            fails = self.m.get_last_observation('nappr_fails')[1]['cnt']
            self.m.add_item('nappr_fails', time.time(), {'cnt':fails+1})
            # set finished
            self.set_finished()
            return
                    
        # stop criteria success head = center down, ball = lower half of view
        if self.within_accuracy(pitch, self.min_pitch, self.acc_look) and self.within_accuracy(yaw, self.center_yaw, self.acc_look):
            self.__nao.stopwalk()
            self.set_finished()
            print "Finished approach: Succes"
            return

        # centers the ball in the field of view
        # starts walking in the direction of the ball
        if self.state == "LOOK" and self.new_detection:
            if time.time() - self.last_look_time >=2:
                # maybe allows for yaw movement when pitch cannot go any further
                self.__nao.look_at(self.position[0], self.position[1])
                self.last_look_time = time.time()
            # go to state WALK when ball is in center of x
            # walk takes care of the y view-position
            if self.within_accuracy(self.position[0], 0.5, self.acc_view):
                self.state = "WALK"
                
        # monitors walking
        # stops if the ball is at the edge of the view
        elif self.state == "WALK":  
	    # first rotate towards to the ball and re-adjust the yaw to the center
            if self.firstWalk:
                self.__nao.walk(0,0,yaw)
                self.__nao.set_angles(["HeadYaw"],[-yaw],0.01)
                self.state = "LOOK"
                self.firstWalk = False
            
            if not self.__nao.isWalking():
                # calculates how far the NAO is allowed to move as a function of the pitch. (how far the NAO is looking down)
                dist = (abs(pitch - self.min_pitch))*0.1
		# if the NAO is not in front of the ball, walk to the left or to the right
                if not self.within_accuracy(yaw, self.center_yaw, self.acc_look):
                    if yaw < self.center_yaw:
                        if not self.__nao.isWalking():
                            self.__nao.walk(0,-0.05,0)
                    elif yaw > self.center_yaw:
                        if not self.__nao.isWalking():
                            self.__nao.walk(0,0.05,0)
		# if the NAO is in front of the ball, walk forward using calculated distance. 
                else:
                    self.__nao.walk(dist,0,0)
            # go back to findball when the ball is lost 
            if (self.within_accuracy(self.position[0], 0.5, acc_walk)==False) or self.position[1] <( 0.5-acc_walk) or (time.time()-self.last_recogtime > 1.5):
                self.__nao.stopwalk()
                self.state = "LOOK"
