import mesa
from agents import *
from mesa.space import MultiGrid
import random
import numpy as np
import matplotlib.pyplot as plt


class MyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, C, F, P, width, height):
        # self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivationByType(self)
        self.is_initial_step = True
        self.kill_agents = []

        # Create clubs
        clubs = []
        for i in range(C):
            club = Club(i, self, revenue = 0, spending = 0, objectives = 0, fans = 0)
            self.schedule.add(club)
            clubs.append(club)

            # Add the agent to a random grid cell
            # x = self.random.randrange(self.grid.width)
            # y = self.random.randrange(self.grid.height)
            # self.grid.place_agent(f_agent, (x, y))

        # Create agents
        pool = []
        for i in range(F):
            f_agent = F_Agents(C + i, self, cut = random.randint(3, 10), network = "Signed", n_skills = random.randint(1, 10))
            self.schedule.add(f_agent)
            pool.append(f_agent)

            # Add the agent to a random grid cell
            # x = self.random.randrange(self.grid.width)
            # y = self.random.randrange(self.grid.height)
            # self.grid.place_agent(f_agent, (x, y))

        # Create players
        for i in range(P):
            player = Players(C + F + i, self, age = random.randint(18, 40), contract = "Signed", reputation = random.randint(1, 10), 
                             skill = random.randint(1, 10), value = 0)
            player.set_value()
            self.schedule.add(player)

            # Link players to agents
            choice = random.choice(pool)
            player.link_agent(choice)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(player, (x, y))


    def step(self):
        """Advance the model by one step."""
        print("\nStep:", self.schedule.steps)

        # First step 
        if self.is_initial_step:
            print("First")
            self.is_initial_step = False

        self.schedule.step()
        self.retire_players()


    # Players go to retirement when age >= 40
    def retire_players(self):
        players_to_retire = [player for player in self.schedule.agents if isinstance(player, Players) and player.age == 40]
        if players_to_retire:
            for agent in players_to_retire:
                print("Player " + str(agent.unique_id) + " retires!")
                self.schedule.remove(agent)
                self.grid.remove_agent(agent)
        else:
            print("No players retire!")

