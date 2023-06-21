import mesa
from agent import *
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import random

# class MoneyModel(mesa.Model):
#     """A model with some number of agents."""

#     def __init__(self, number_of_agents, width, height):
#         self.num_agents = number_of_agents
#         self.grid = MultiGrid(width, height, True)
#         self.schedule = RandomActivation(self)
#         self.running = True
        
#         # Create agents
#         for i in range(self.num_agents):
#             a = Players(unique_id = i, model = self, reputation = "Good", skill = "Good", value = 75000)
#             self.schedule.add(a)
#             # Add the agent to a random grid cell
#             x = self.random.randrange(self.grid.width)
#             y = self.random.randrange(self.grid.height)
#             self.grid.place_agent(a, (x, y))

#         # self.datacollector = mesa.DataCollector(
#         #     {
#         #     "Wealthy agents" : MoneyModel.count_wealthy,
#         #     "Non wealthy agents" : MoneyModel.count_non_wealthy,}
#             # model_reporters={"Gini": compute_gini}, agent_reporters={"Wealth": "wealth"}
#         # )

#     def step(self):
#         # self.datacollector.collect(self)
#         # self.datacollector_currents.collect(self)
#         self.schedule.step()

#         # if MoneyModel.count_non_wealthy(self) > 20:
#         #     self.running = False


#     # @staticmethod
#     # def count_wealthy(model) -> int:
#     #     return sum([ 1 for agent in model.schedule.agents if agent.wealth > 0])

#     # @staticmethod
#     # def count_non_wealthy(model) -> int:
#     #     return sum([ 1 for agent in model.schedule.agents if agent.wealth == 0])

class MoneyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N):
        self.num_agents = N
        self.schedule = mesa.time.RandomActivation(self)
        # Create agents
        for i in range(self.num_agents):
            a = Players(i, self)
            self.schedule.add(a)


class MyModel(Model):
    def __init__(self, N):
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(10, 10, torus=False)

        for i in range(N):
            club = Club(i, self, revenue = 1000, spending = 500, objectives = 2, fans = 100)
            self.schedule.add(club)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(club, (x, y))

        for i in range(N):
            player = Players(i + N, self, contract = "Signed", reputation = 1, skill = random.randint(1, 10), value = 0)
            self.schedule.add(player)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(player, (x, y))

        for i in range(N):
            agent = F_Agents(i + N + N, self, cut = 0.1, network = random.randint(1, 10), n_skills=random.randint(1, 10), clients = [])
            self.schedule.add(agent)

            # Assign random players as clients to the agent
            random_players = random.sample(self.schedule.agents[N:N+N], 2)
            for player in random_players:
                agent.add_client(player)

    def step(self):
        self.schedule.step()

empty_model = MyModel(10)
empty_model.step()