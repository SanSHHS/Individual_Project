import mesa
from agents import *
from mesa.space import MultiGrid
import random
import numpy as np
import matplotlib.pyplot as plt


class MyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, C, F, P, width, height):
        self.num_clubs = C
        self.num_agents = F
        self.num_players = P
        self.grid = MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivationByType(self)
        # self.is_initial_step = True
        self.clubs = []
        self.pool = []
        self.highest_unique_id = C + F
        self.team_skill_levels = {}
        self.second_team_skill_levels = {}
        self.final_results = {}


        # Creating agents
        self.create_clubs(C)
        self.create_agents(F)
        self.create_players(P)

    def step(self):
        """Advance the model by one step."""
        print("\nStep:", self.schedule.steps)

        # First step 
        # if self.is_initial_step:
        #     print("First Step")
        #     self.is_initial_step = False

        if self.schedule.steps != 0 and self.schedule.steps %10 == 0:
            print("Season over")
            self.final_skill_levels()
            self.print_final_skill_levels()
            self.winner()

        if self.schedule.steps != 0 and self.schedule.steps % 5 == 0:
            print("Transfer market opens")

        self.schedule.step()
        self.retire_players()
        player_count = self.count_players()
        # print("Number of players: ", player_count)

        # If a player retires, a new player will be created
        if player_count < self.num_players:
            self.create_players(self.num_players - player_count)

        if self.schedule.steps != 1 and self.schedule.steps % 5 == 1:

            print("Close")
            self.average_skill_levels()
            self.print_average_skill_levels()

        # player_count = self.count_players()
        # print("Number of players: ", player_count)



    # Functions
    def create_clubs(self, C):
        for i in range(C):
            club = Club(i, self, revenue = 0, spending = 0, type = random.randint(1, 3))
            club.set_revenue()
            self.schedule.add(club)
            self.clubs.append(club)

    def create_agents(self, F):
        for i in range(F):
            f_agent = F_Agents(self.num_clubs + i, self, cut = random.randint(3, 10), network = "Signed", n_skills = random.randint(1, 10))
            self.schedule.add(f_agent)
            self.pool.append(f_agent)

    def create_players(self, P):
        for i in range(P):
            self.highest_unique_id += 1
            player_id = self.highest_unique_id
            player = Players(player_id, self, age = random.randint(18, 39), contract = "Signed", reputation = random.randint(1, 10), 
                             skill = random.randint(1, 10), value = 0)
            player.set_value()
            self.schedule.add(player)

            # Link players to agents
            choice = random.choice(self.pool)
            player.link_agent(choice)
            choice = random.choice(self.clubs)
            player.join_club(choice)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(player, (x, y))

    # Players go to retirement when age >= 40
    def retire_players(self):
        players_to_retire = [player for player in self.schedule.agents if isinstance(player, Players) and player.age == 40]
        if players_to_retire:
            for agent in players_to_retire:
                print("Player " + str(agent.unique_id) + " retires!")

                if agent.F_agent is not None:
                    agent.F_agent.clients.remove(agent)

                if agent.club is not None:
                    agent.club.team.remove(agent)

                self.schedule.remove(agent)
                self.grid.remove_agent(agent)
        else:
            print("No players retire!")

    # Count current players in the model
    def count_players(self):
        count = 0
        for agent in self.schedule.agents:
            if isinstance(agent, Players):
                count += 1
        return count

    def average_skill_levels(self):
        self.team_skill_levels = {}
        for club in self.clubs:
            team_skill = club.team_level()
            self.team_skill_levels[club.unique_id] = team_skill
        
    def final_skill_levels(self):
        self.second_team_skill_levels = {}
        self.final_results = {}
        for club in self.clubs:
            team_skill = club.team_level()
            self.second_team_skill_levels[club.unique_id] = team_skill

        for key in self.team_skill_levels:
            if key in self.second_team_skill_levels:
                self.final_results[key] = (self.team_skill_levels[key] + self.second_team_skill_levels[key]) / 2

    def print_average_skill_levels(self):
        for club_id, team_skill in self.team_skill_levels.items():
            print("Club " + str(club_id) + " - Average Team Skill Level: " + str(team_skill))

    def print_final_skill_levels(self):
        for club_id, team_skill in self.final_results.items():
            print("Club " + str(club_id) + " - Average Team Skill Level: " + str(team_skill))

    def winner(self):
        max_key = max(self.final_results, key=lambda x: self.final_results[x])
        print("The winner is club: ", max_key)
