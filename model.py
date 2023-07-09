import mesa
from agent import *
from mesa.space import MultiGrid
import random
import numpy as np
import matplotlib.pyplot as plt


class MoneyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        # self.agents = []
        self.kill_agents = []

        # Create agents
        for i in range(self.num_agents):
            player = Players(i, self, age = random.randint(18, 40), contract = "Signed", reputation = random.randint(1, 10), 
                             skill = random.randint(1, 10), value = 0)
            player.set_value()
            self.schedule.add(player)
            # self.agents.append(player)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(player, (x, y))

    def step(self):
        """Advance the model by one step."""
        print("Step:", self.schedule.steps)
        self.schedule.step()
        self.retire_agents()
        # for agent in self.agents:
        #     agent.step()

    def retire_agents(self):
        players_to_retire = [player for player in self.schedule.agents if player.age == 40]
        if players_to_retire:
            for agent in players_to_retire:
                print("Player " + str(agent.unique_id) + " retires!")
                self.schedule.remove(agent)
                self.grid.remove_agent(agent)
                # self.kill_agents.remove(agent)
        else:
            print("No players retire!")

