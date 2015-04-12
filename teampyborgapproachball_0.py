import basebehavior.behaviorimplementation
import time

class TeamPyborgApproachball_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    def implementation_init(self):
        self.__nao = self.body.nao(0)
        self.lookatball = self.ab.teampyborglookatball({})
        self.walktoball = self.ab.teampyborgwalktoball({})
        self.analysevision = self.ab.teampyborganalysevision({})
        self.selected_behaviors = [ \
#            ("analysevision", "True"), \
            ("lookatball", "True"), \
            ("walktoball", "True"), \
        ]
        print "start approach"
        
    # update loop        
    def implementation_update(self):
        # stop criteria failure
        if self.lookatball.is_finished():
            print "Finished approach: Failure"
            # stop all approach ball actions
            self.__nao.stopwalk()
            # set error flag in memory
            self.m.add_item('lost_ball', time.time(), {'restarted': False})
            # set finished
            self.set_finished()
            return 
        
        # stop on touch 
        if self.m.n_occurs('stop_behaviors') > 0 and not self.m.get_last_observation('stop_behaviors')[1]['restarted']:
            print "Finished approach-ball: stopped on touch"
            self.__nao.stopwalk()
            self.set_finished()
            return
        
        #stop criteria success
        if self.walktoball.is_finished():
            print "Finished approach: Success"
            self.set_finished()
            return
