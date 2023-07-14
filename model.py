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

        if self.schedule.steps != 0 and self.schedule.steps % 4 == 0:
            print("Season over")
            self.final_skill_levels()
            self.print_final_skill_levels()
            self.winner()

        if self.schedule.steps != 0 and self.schedule.steps % 2 == 0:
            self.average_skill_levels()
            self.print_average_skill_levels()
            print("Transfer market opens")
            self.open_market()
            self.club_incentives()

            
        self.schedule.step()
        self.retire_players()

        player_count = self.count_players()
        # print("Number of players: ", player_count)

        # If a player retires, a new player will be created
        if player_count < self.num_players:
            self.create_players(self.num_players - player_count)

        if self.schedule.steps != 1 and self.schedule.steps % 2 == 1:

            print("Close")
            # self.average_skill_levels()
            # self.print_average_skill_levels()
            self.print_club()

        # player_count = self.count_players()
        # print("Number of players: ", player_count)



    # Functions
    def create_clubs(self, C):
        for i in range(C):
            club = Club(i, self, type = random.randint(1, 3))
            club.set_revenue()
            club.set_spending()
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
                             skill = random.randint(1, 10))
            player.set_potential()
            player.set_value()
            self.schedule.add(player)

            # Link players to agents evenly
            available_agents = []
            max_a = self.num_players / self.num_agents
            available_agents = [a for a in self.pool if len(a.clients) < max_a]
            choice = random.choice(available_agents)
            player.link_agent(choice)

            # Link players to clubs evenly
            available_clubs = []
            max_c = self.num_players / self.num_clubs
            available_clubs = [c for c in self.clubs if len(c.team) < max_c]
            choice = random.choice(available_clubs)
            player.join_club(choice)

            player.set_salary()

            # Add players to a random grid cell
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
            if key in self.second_team_skill_levels and self.team_skill_levels[key] is not None and self.second_team_skill_levels[key] is not None:
                self.final_results[key] = (self.team_skill_levels[key] + self.second_team_skill_levels[key]) / 2

        if len(self.final_results) == 0:
            print("Not a valid team to compete.")

    def print_average_skill_levels(self):
        for club_id, team_skill in self.team_skill_levels.items():
            print("Club " + str(club_id) + " has average level of: " + str(team_skill) + " before transfers")

    def print_final_skill_levels(self):
        for club_id, team_skill in self.final_results.items():
            print("Club " + str(club_id) + " season average level is: " + str(team_skill))

    def winner(self):
        max_key = max(self.final_results, key = lambda x: self.final_results[x])
        season = round(self.schedule.steps / 4)
        print("The winner of season " + str(season) + " is club " + str(max_key) + ". \n")
        for club in self.clubs:
            if club.unique_id == max_key:
                for player in club.team:
                    player.higher_rep()
                    player.set_salary()
                club.wins()
                club.set_revenue()
                club.set_spending()
                club.set_budget()

    def print_club(self):
        for club in self.clubs:
            print("Club " + str(club.unique_id) + " spends " + str(club.spending) + ".") 

    # Open the market and list all the players
    def open_market(self):
        self.market = []
        for club in self.clubs:
            club.set_budget()
            for player in club.team:
                self.market.append(player)

    # Player transfer
    def transfer(self, player, club):
        if player in self.market:
            self.market.remove(player)
        player.club.revenue_from_sales += player.value
        player.club.spending -= player.salary
        player.club.team.remove(player)
        player.join_club(club)
        club.budget -= player.value
        club.set_spending()


    def club_incentives(self):
        clubs = self.clubs.copy()
        random.shuffle(clubs)

        for club in clubs:
            target = None
            skill_level = 0

            if club.type == 1:
                pass
            elif club.type == 2:
                pass
            elif club.type == 3:
                pass

            for player in self.market:
                if player.club != club and player.value <= club.budget - player.salary and player.skill > skill_level:
                    target = player
                    skill_level = player.skill

            # Find the worst player of the team
            if club.team:
                min_player = min(club.team, key=lambda player: player.skill)

                # Execute the transfer
                if target is not None and target.skill > min_player.skill:
                    self.transfer(target, club)
                    print("Club", club.unique_id, "bought player", target.unique_id)
            else:
                print("Club", club.unique_id, "has no players in the team.")
        
    def sell_players(self):
        pass