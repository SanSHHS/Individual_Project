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
        club.fans = random.randint(70, 100)
    if type == 2:
        club.objectives = random.randint(10, 1000)
        club.fans = random.randint(30, 70)
    if type == 3:
        club.objectives = random.randint(10, 1000)
        club.fans = random.randint(1, 30)


class Club(Agent):
    def __init__(self, unique_id, model, type):
        super().__init__(unique_id, model)
        self.revenue = 0
        self.spending = 0
        self.type = type
        self.objectives = 0
        self.fans = 0
        self.team = []
        self.budget = 0
        self.revenue_from_sales = 0
        set_club_type(self, type)

    def add_player(self, player):
        self.team.append(player)

    def set_revenue(self):
        """For small clubs its 7000 - 210 000, medium clubs 210 000 - 490 000, big club 490 000 - 700 000"""
        self.revenue = 2 * self.fans

    def set_spending(self):
        self.spending = 0
        # for player in self.team:
        #     self.spending += player.salary
        # self.spending = round(self.spending, 2)
        self.spending = round(sum(player.salary for player in self.team), 2)

    def set_budget(self):
        self.budget = round(self.revenue - self.spending + self.revenue_from_sales, 2)
        self.revenue_from_sales = 0

    def team_level(self):
        if len(self.team) > 0:
            total = sum(player.skill for player in self.team)
            average = round(total / len(self.team), 2)
            return average
        else:
            print("No players in the team yet")

    def wins(self):
        self.fans = round(self.fans * 1.3)

    def sell_player(self):
        if self.budget < 0:
            if self.team:
                # Find the worst skilled player in the team
                min_player = min(self.team, key=lambda player: player.skill)

                # Try to find a potential buyer club
                if self.model.club_incentives(min_player):
                    print("Club", self.unique_id, "sold player ", min_player.unique_id)

                else:
                    print("Club", self.unique_id, "could not find a buyer for the worst skilled player.")
                    self.release_player(min_player)
            else:
                print("Club", self.unique_id, "has no players in the team.")
        else:
            print("Club", self.unique_id, "does not need to sell a player.")


    def release_player(self, min_player):
        if min_player in self.team:
            # Remove the player from the team
            self.team.remove(min_player)

            # Update the budget by adding the player's value
            self.spending -= min_player.salary

            # Print a message indicating the player has been released
            print("Club", self.unique_id, "released player", min_player.unique_id)
        else:
            print("Release gone wrong Club", self.unique_id, "does not have player", min_player.unique_id)
        min_player.join_club(None)

    
    def step(self):
        if self.model.schedule.steps == 0 or self.model.schedule.steps % 2 == 1:
            self.set_spending()

        if self.model.schedule.steps % 2 == 0:
            self.set_budget()

        if self.model.schedule.steps != 0 and self.model.schedule.steps % 2 == 0:
            self.sell_player()


        squad_id = [str(player.unique_id) for player in self.team]
        squad_list = ', '.join(squad_id)
        print("Club " + str(self.unique_id) + ". My type is: " + str(self.type) + ". My team has player number: " + squad_list + ". The average level is: " + 
              str(self.team_level()) + ". The revenue is " + str(self.revenue) + ". The number of fan is " + str(self.fans) + ". Spending is " + 
              str(self.spending) + ". The budget is " + str(self.budget) + ".")

class F_Agents(Agent):
    def __init__(self, unique_id, model, cut, network, n_skills):
        super().__init__(unique_id, model)
        self.cut = cut
        self.network = network
        self.n_skills = n_skills
        self.clients = []
        self.money = 0

    def add_client(self, player):
        self.clients.append(player)

    def earn(self, contract):
        self.money += self.cut /100 * contract
        self.money = round(self.money, 2)

    def step(self):
        client_id = [str(player.unique_id) for player in self.clients]
        client_list = ', '.join(client_id)
        # print("Agent " + str(self.unique_id) + " My clients are: " + client_list + ". My skill is " + str(self.n_skills) + ". ")
        print("Agent " + str(self.unique_id) + " money is " + str(self.money) + ".")

class Players(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, age, contract, reputation, skill):
        super().__init__(unique_id, model)
        self.age = age
        self.contract = contract
        self.reputation = reputation
        self.skill = skill
        self.value = 0
        self.salary = 0
        self.potential = 0
        self.F_agent = None
        self.club = None

    # Set the players' salary
    def set_salary(self):
        self.salary = round(self.reputation * self.skill / self.age * self.F_agent.n_skills, 2)
        self.F_agent.earn(self.salary)

    # Set the players' value
    def set_value(self):
        self.value = round(self.reputation * self.skill * self.potential / self.age, 2)

    # Link players with agents
    def link_agent(self, F_agents):
        self.F_agent = F_agents
        F_agents.add_client(self)

    def join_club(self, club):
        if club is not None:
            self.club = club
            self.contract = "Signed"
            club.add_player(self)
        else:
            self.club = None
            self.contract = "Free agent"

    def higher_rep(self):
        self.reputation += 1

    def set_potential(self):
        self.potential = self.skill + random.randint(0, 10)

    # Player ages and get closer to their potential
    def ageing(self):
        self.age += 1
        if self.skill < self.potential:
            self.skill += 1

    def step(self):
        print("Hi, I am player " + str(self.unique_id) + ". My age is " + str(self.age) + ". My contract is " + self.contract + ". My rep is " + 
              str(self.reputation) + ". My skill is " + str(self.skill) + ". My value is " + str(self.value) + " millions. My salary is " + str(self.salary) + ".")
        
        if self.F_agent is not None and self.club is not None:
            print("My agent is agent " + str(self.F_agent.unique_id) + ". My club is club " + str(self.club.unique_id))
        
        # Player is one year older each 10 steps
        if self.model.schedule.steps != 0 and self.model.schedule.steps % 4 == 0:
            self.ageing()
            self.set_salary()
            self.set_value()
    
