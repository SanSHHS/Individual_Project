from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

class Club(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, revenue, spending, objectives, fans):
        super().__init__(unique_id, model)
        self.revenue = revenue
        self.spending = spending
        self.objectives = objectives
        self.fans = fans
        self.team = []

    def add_player(self, player):
        self.team.append(player)
    
    def step(self):
        print("Club made!" + str(self.unique_id))

class F_Agents(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, cut, network, n_skills):
        super().__init__(unique_id, model)
        self.cut = cut
        self.network = network
        self.n_skills = n_skills
        self.clients = []

    def add_client(self, player):
        self.clients.append(player)

    def step(self):
        print("Agent made!" + str(self.unique_id) + ".")

class Players(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, age, contract, reputation, skill, value):
        super().__init__(unique_id, model)
        self.age = age
        self.contract = contract
        self.reputation = reputation
        self.skill = skill
        self.value = value
        self.F_agent = None
        self.club = None

    # Set the players' value
    def set_value(self):
        self.value = round(self.reputation * self.skill / self.age, 2)

    # Link players with agents
    def link_agent(self, F_agents):
        self.F_agent = F_agents
        F_agents.add_client(self)

    def join_club(self, club):
        self.club = club
        club.add_player(self)

    # Player ages
    def ageing(self):
        self.age += 1

    def step(self):
        print("Player made!")
        print("Hi, I am player " + str(self.unique_id) + ". My age is " + str(self.age) + ". My contract is " + self.contract + ". My rep is " + 
              str(self.reputation) + ". My skill is " + str(self.skill) + ". My value is " + str(self.value) + " millions.")
        
        if self.F_agent is not None:
            print("My agent is agent " + str(self.F_agent.unique_id))
        
        # Player is one year older each 10 steps
        if self.model.schedule.steps != 0 and self.model.schedule.steps % 10 == 0:
            self.ageing()
    
