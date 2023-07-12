from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import random


def set_club_type(club, type):
    """Updates club's attributes according to its type:
    1 = Big, 2 = Medium, 3 = Small

    Args:
        Club: The agent instance.
        type (int): The type of club.
    """
    if type == 1:
        club.objectives = random.randint(10, 1000)
        club.fans = random.randint(700, 1000)
    if type == 2:
        club.objectives = random.randint(10, 1000)
        club.fans = random.randint(300, 700)
    if type == 3:
        club.objectives = random.randint(10, 1000)
        club.fans = random.randint(10, 300)


class Club(Agent):
    def __init__(self, unique_id, model, revenue, spending, type):
        super().__init__(unique_id, model)
        self.revenue = revenue
        self.spending = spending
        self.type = type
        self.objectives = 0
        self.fans = 0
        self.team = []
        set_club_type(self, type)

    def add_player(self, player):
        self.team.append(player)

    def set_revenue(self):
        self.revenue = 700 * self.fans

    def team_level(self):
        if len(self.team) > 0:
            total = sum(player.skill for player in self.team)
            average = round(total / len(self.team), 2)
            return average
        else:
            print("No players in the team yet")

    def wins(self):
        self.fans *= 1.3
    
    def step(self):
        squad_id = [str(player.unique_id) for player in self.team]
        squad_list = ', '.join(squad_id)
        print("Club made!" + str(self.unique_id) + ". My type is: " + str(self.type) + ". My team has player number: " + squad_list + ". The average level is: " + 
              str(self.team_level()) + ". The revenue is " + str(self.revenue) + ".")

class F_Agents(Agent):
    def __init__(self, unique_id, model, cut, network, n_skills):
        super().__init__(unique_id, model)
        self.cut = cut
        self.network = network
        self.n_skills = n_skills
        self.clients = []

    def add_client(self, player):
        self.clients.append(player)

    def step(self):
        client_id = [str(player.unique_id) for player in self.clients]
        client_list = ', '.join(client_id)
        print("Agent made!" + str(self.unique_id) + " My clients are: " + client_list + ".")

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

    def higher_rep(self):
        self.reputation += 5

    # Player ages
    def ageing(self):
        self.age += 1

    def step(self):
        print("Player made!")
        print("Hi, I am player " + str(self.unique_id) + ". My age is " + str(self.age) + ". My contract is " + self.contract + ". My rep is " + 
              str(self.reputation) + ". My skill is " + str(self.skill) + ". My value is " + str(self.value) + " millions.")
        
        if self.F_agent is not None:
            print("My agent is agent " + str(self.F_agent.unique_id) + ". My club is club " + str(self.club.unique_id))
        
        # Player is one year older each 10 steps
        if self.model.schedule.steps != 0 and self.model.schedule.steps % 10 == 0:
            self.ageing()
    
