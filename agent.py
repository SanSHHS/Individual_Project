from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation


class Players(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, contract, reputation, skill, value):
        super().__init__(unique_id, model)
        self.contract = contract
        self.reputation = reputation
        self.skill = skill
        self.value = value

    def step(self):
        print("Player made!")


class Club(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, revenue, spending, objectives, fans):
        super().__init__(unique_id, model)
        self.revenue = revenue
        self.spending = spending
        self.objectives = objectives
        self.fans = fans
    
    def step(self):
        print("Club made!")

class F_Agents(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, cut, network, n_skills, clients):
        super().__init__(unique_id, model)
        self.cut = cut
        self.network = network
        self.n_skills = n_skills
        self.clients = []

    def add_client(self, player):
        self.clients.append(player)

    def step(self):
        print("Agent made!" + str(self.unique_id) + ".")