from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation


class Players(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, age, contract, reputation, skill, value):
        super().__init__(unique_id, model)
        self.age = age
        self.contract = contract
        self.reputation = reputation
        self.skill = skill
        self.value = value
        self.agent = []

    # Set the players' value
    def set_value(self):
        self.value = self.reputation * self.skill / self.age

    # Link players with agents
    def add_agent(self, F_agents):
        self.agent.append(F_agents)


    def step(self):
        print("Player made!")
        print("Hi, I am player " + str(self.unique_id) + ". My age is " + str(self.age) + ". My contract is " + self.contract + ". My rep is " + str(self.reputation) + ". My skill is " + str(self.skill) 
              + ". My value is " + str(self.value) + ".")

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
        print("Club made!")

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