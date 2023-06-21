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

    # def move(self):
    #     possible_steps = self.model.grid.get_neighborhood(
    #         self.pos, moore=True, include_center=False
    #     )
    #     new_position = self.random.choice(possible_steps)
    #     self.model.grid.move_agent(self, new_position)

    # def give_money(self):
    #     cellmates = self.model.grid.get_cell_list_contents([self.pos])
    #     if len(cellmates) > 1:
    #         other_agent = self.random.choice(cellmates)
    #         other_agent.wealth += 1
    #         self.wealth -= 1

    def step(self):
        print("Player made!")
        # self.move()
        # if self.wealth > 0:
        #     self.give_money()

class Players(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, contract, reputation, skill, value):
        super().__init__(unique_id, model)
        self.contract = contract
        self.reputation = reputation
        self.skill = skill
        self.value = value

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