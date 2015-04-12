import basebehavior.behaviorimplementation
import time

# the walktoball behavior
class TeamPyborgWalktoball_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    def implementation_init(self):

        self.__nao = self.body.nao(0)
        self.firstWalk = True
        self.center_yaw = 0
        self.min_pitch = 0.5
        self.acc_look = 0.08
        self.lastwalktime = time.time()
        self.state = 0
        
        #self.state = "START"
        print "start walk to ball"
        
    def within_accuracy(self, var, val, acc):
        return (var < val+acc and var > val-acc)    
        
    def implementation_update(self):
        yaw, pitch = self.__nao.get_angles(['HeadYaw', 'HeadPitch'], True) 
        
        # stop criteria success head = center down, ball = lower half of view
        if self.within_accuracy(pitch, self.min_pitch, self.acc_look) and self.within_accuracy(yaw, self.center_yaw, self.acc_look):
            self.__nao.stopwalk()
            self.set_finished()
            print "Finished walk to ball: Succes"
            return

		# first rotate towards the ball
        if self.firstWalk:
                print "first-turn"
                self.__nao.walk(0,0,yaw)
                self.__nao.set_angles(['HeadYaw', 'HeadPitch'],[0,0], 0.01)
                self.firstWalk = False

		# walk left or right when the NAO is not front of the ball
        if not self.within_accuracy(yaw, self.center_yaw, self.acc_look):
            if yaw < self.center_yaw:
                if not self.state == 1:
                    self.__nao.setWalkTargetVelocity(0,0,0,0)
                    time.sleep(0.2)
                self.__nao.setWalkTargetVelocity(0,-1, 0, 0.5)
                #self.__nao.walk(0,-0.05,0)
                self.state = 1
            elif yaw > self.center_yaw:
                if not self.state == 2:
                    self.__nao.setWalkTargetVelocity(0,0,0,0)
                    time.sleep(0.2)
                self.__nao.setWalkTargetVelocity(0, 1, 0, 0.5)
                #self.__nao.walk(0,0.05,0)
                self.state = 2
		# walk forward if the NAO is in front of the NAO
        else:
            if not self.state == 0:
                self.__nao.setWalkTargetVelocity(0,0,0,0)
                time.sleep(0.2)
            self.__nao.setWalkTargetVelocity(1, 0, 0, 0.5)
            self.state = 0
    


