import random
import itertools
import bisect
import math
import datetime

from banditfunctions import betadist_payoff, randomshock, softmax_strategy, simplebelief



class Bandit:
    """
    With default parameters, this object should set up a single run
    of the multi-armed bandit simulation described by Posen & Levinthal
    in their 2012 Management Science paper.  The simulate() method
    will cause it to run all time periods (500 by default), and return
    the run time.  The other methods may be used to capture outcome
    data like the ending asset stock.
    """
    def __init__(self,
                 arms=10,
                 turns=500,
                 payoff_fxn=betadist_payoff,
                 turbulence_fxn=randomshock,
                 strategy_fxn=softmax_strategy,
                 turbulence=0,
                 belief_fxn=simplebelief,
                 strategy=0.5
                 ):
        self._arms = arms
        self._turns = turns
        self._assetstock = 0
        self._complete = False
        
        self._payoff_fxn = payoff_fxn 
        # User can pass in any random number generating function; 
        # by default the payoffs for each arm are drawn from a Beta 
        # distribution with alpha=2 and beta=2. This is a normal-like
        # distribution bounded between 0 and 1, with mean = 0.50 and 
        # std. dev. = 0.22.
        self._payoffs = [self._payoff_fxn() for i in range(arms)] 

        self._turbulence_fxn = turbulence_fxn
        self._turbulence = turbulence
        # In Posen&Levinthal, there is a set probability of turbulence 
        # occurring in any given turn (determined here by the turbulence
        # parameter, with a default of 0, no turbulence).  When it occurs,
        # it is manifested as a re-draw of some payoffs from the initial
        # beta distribution.  Each "arm" has an independent probability
        # of 0.5 of having its payoff re-drawn.  Each turn this program
        # will call self._turbulence_fxn( self._payoffs, self._payoff_fxn,
        # self._turbulence ), so if you provide a custom turbulence function,
        # the self._turbulence variable should be used to hold any variable 
        # parameters or configuration.
        
        self._strategy_fxn = strategy_fxn
        self._strategy = strategy
        # The _strategy_fxn returns probabilities, one for each "arm", that
        # the gambler will choose that arm.  This could be all 0s with one 1,
        # or some other distribution that adds up to 1.  By default we use
        # the SOFTMAX algorithm described by Posen & Levinthal. The function
        # is called with self._strategy_fxn( self._beliefs, self._strategy )
        # so the self._strategy variable should be used to hold any variable
        # parameters or configuration. By default, it is the "tau" of the 
        # SOFTMAX calculation.
        
        self._belief_fxn = belief_fxn
        self._tries = [0 for i in range(arms)]
        self._wins = [0 for i in range(arms)]
        self._beliefs = [0.5 for i in range(arms)]
        # By default, the gambler's belief about the payoff of each "arm"
        # is the number of wins divided by the number of tries.         
        # According to Hart Posen (personal communication), the initial
        # belief for all arms is 0.5, simulated as 2 trials with 1 win;
        # this way the first true trial is averaged in as if it were
        # the third trial, so the belief will not jump to 0.0 or 1.0.
        # We simply keep track of the # tries and # wins for each arm.
        # The belief-updating function is called with self._beliefs = 
        # self._belief_fxn( self._beliefs, self._tries, self._wins )
        # after self_tries and self_wins have been updated.
        
        # data structures to hold score data over time
        self._score = []
        self._knowledge = []
        self._opinion = []
        self._probexplore = []
        
    def simulate(self):
        
        starttime = datetime.datetime.now()

        for t in range(self._turns):
        
            # implement turbulence
            self._payoffs = self._turbulence_fxn( self._payoffs, self._payoff_fxn, self._turbulence)
            
            # determine gambler's choice
            choice_probabilities = self._strategy_fxn( self._beliefs, self._strategy )
            cumdist = list(itertools.accumulate(choice_probabilities))
            x = random.random()
            choice = bisect.bisect(cumdist,x)
            
            # The gambler's choice results in a win or a loss (a gain or loss of 1 "asset stock")
            self._tries[choice] += 1
            if random.random() < self._payoffs[choice]:
                self._wins[choice] += 1
                self._assetstock += 1
            else:
                self._assetstock -= 1
                
            # Update beliefs
            self._beliefs = self._belief_fxn( self._beliefs, self._tries, self._wins )
            # Beliefs are simply the proportion of trials of each arm that have resulted in wins.
            
            # Score time series of asset stock, "Knowledge", "Opinion", and "Prob_Explore"
            self._score.append(self._assetstock)
            self._knowledge.append( 1 - sum([ (self._beliefs[i]-self._payoffs[i])**2 for i in range(self._arms) ]) )
            self._opinion.append( sum([(self._beliefs[i] - (sum(self._beliefs)/self._arms))**2 for i in range(self._arms)]) )
            self._probexplore.append( 1 - max(choice_probabilities) )

        self._complete = True

        endtime = datetime.datetime.now()
        self._simtime = endtime-starttime # how long the simulation took
        

    def score(self):
        if self._complete:
            return self._score[-1]
        else:
            return None
            # todo: decide: if they request the score without first running the simulation, should we run self.simulate() for them? or raise an exception, or what?
            
    def knowledge(self):
        if self._complete:
            return self._knowledge[-1]
        else:
            return None

    def opinion(self):
        if self._complete:
            return self._opinion[-1]
        else:
            return None

    def probexplore(self):
        if self._complete:
            return self._probexplore[-1]
        else:
            return None



if __name__ == "__main__":
    b = Bandit()
    assert b.score() == None
    b.simulate()
    print( "final asset stock:", b.score() )
    #print( "scores", b._score )
    #print( "knowledge:", b._knowledge )
    #print( "opinion", b._opinion )
    #print( "probability of exploration", b._probexplore )
    print( "simulation time",b._simtime )





    

