import mesa
from agents import *
from mesa.space import MultiGrid
import random
import numpy as np
import matplotlib.pyplot as plt
# from data import datacollector



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
        self.market = []
        self.minimum = 11


        # Creating agents
        self.create_clubs(C)
        self.create_agents(F)
        self.create_players(P)

    def step(self):
        # Collect data at each step
        # datacollector.collect(self)

        """Advance the model by one step."""
        print("\nStep:", self.schedule.steps)

        # First step 
        # if self.is_initial_step:
        #     print("First Step")
        #     self.is_initial_step = False
        if self.schedule.steps != 0:
            self.agent_incentives()

        if self.schedule.steps != 0 and self.schedule.steps % 4 == 0:
            print("Season over")
            self.final_skill_levels()
            self.print_final_skill_levels()
            self.winner()
            # self.retire_players()

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
            self.print_club_spending()

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

            # Add players to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(club, (x, y))

    def create_agents(self, F):
        for i in range(F):
            f_agent = F_Agents(self.num_clubs + i, self, cut = random.randint(3, 10), network = "Signed", n_skills = random.randint(1, 10))
            self.schedule.add(f_agent)
            self.pool.append(f_agent)

            # Add players to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(f_agent, (x, y))

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
            max_a = self.num_players / self.num_agents
            # available_agents = [a for a in self.pool if len(a.clients) < max_a]
            available_agents = [a for a in self.pool]

            if available_agents:
                choice = random.choice(available_agents)
                player.link_agent(choice)
            else:
                print("No available agents to link player", player_id)

            # Link players to clubs evenly
            max_c = self.num_players / self.num_clubs
            available_clubs = [c for c in self.clubs if len(c.team) < max_c]
            if available_clubs:
                choice = random.choice(available_clubs)
                player.join_club(choice)
            else:
                print("No available clubs to join for player", player_id)

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

    # Compare team levels before the half season transfer martket opens
    def average_skill_levels(self):
        self.team_skill_levels = {}
        for club in self.clubs:
            team_skill = club.team_level()
            self.team_skill_levels[club.unique_id] = team_skill
        
    # Compare team levels through the whole season
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

    # Print team levels
    def print_average_skill_levels(self):
        for club_id, team_skill in self.team_skill_levels.items():
            print("Club " + str(club_id) + " has average level of " + str(team_skill) + " before transfers")

    def print_final_skill_levels(self):
        for club_id, team_skill in self.final_results.items():
            print("Club " + str(club_id) + " season average level is: " + str(team_skill))

    # Determine the winners
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

    # Print club spending
    def print_club_spending(self):
        for club in self.clubs:
            print("Club " + str(club.unique_id) + " spends " + str(round(club.spending,2)) + ".") 

    # Open the market and list all the players
    def open_market(self):
        self.market = [agent for agent in self.schedule.agents if isinstance(agent, Players)]
        # for player in self.schedule.agents:
        #     if isinstance(player, Players):
        #         self.market.append(player)
        #         print("Market:", player.unique_id)

        # print("Before transfer - market:", self.market)

    # Player transfer
    def transfer(self, player, club):
        print("Before transfer - player:", player.unique_id)
        if player.club is not None:
            # Change attributes following the transfer
            player.club.revenue_from_sales += player.value
            player.club.spending -= player.salary
            player.club.team.remove(player)

        player.F_agent.earn(player.value)
        player.join_club(club)
        club.budget -= player.value
        club.set_spending()

        # Avoid same player transfers multiple times in the same window
        # self.market.remove(player)

    # Club buys players
    def club_incentives(self):
        # Randomize order of clubs for fairness
        clubs = self.clubs.copy()
        random.shuffle(clubs)

        for club in clubs:
            if club != self:  # Skip current club
                target = None
                skill_level = 0
                potential_level = 0
                free_agents = []
                free_agents = [player for player in self.market if player.club is None]

                if club.type == 1:
                    for player in self.market:
                        if player.club != club and player.value <= club.budget - player.salary and player.skill > skill_level:
                            target = player
                            skill_level = player.skill

                    if free_agents:
                        suitable_free_agents = [agent for agent in free_agents if agent.skill == skill_level]
                        if suitable_free_agents:
                            # Prioritize free agents if available
                            target = suitable_free_agents[0]
                            # free_agents.remove(target)

                    # Find the worst player of the team
                    if club.team:
                        min_player = min(club.team, key=lambda player: player.skill)

                        # Execute the transfer if target is better than worst player of the team
                        if target is not None and target.skill > min_player.skill:
                            self.transfer(target, club)
                            print("Club", club.unique_id, "bought player", target.unique_id)
                            self.market.remove(target)
                            # if player:
                            #     return True
                    else:
                        print("Club", club.unique_id, "has no players in the team.")
                        self.transfer(target, club)
                        print("So Club", club.unique_id, "has bought player", target.unique_id)
                        self.market.remove(target)

                if club.type == 2:
                    for player in self.market:
                        if player.club != club and player.value <= club.budget - player.salary and player.skill > skill_level and player.potential > potential_level:
                            target = player
                            skill_level = player.skill
                            potential_level = player.potential

                    if free_agents:
                        suitable_free_agents = [agent for agent in free_agents if agent.skill == skill_level and agent.potential == potential_level]
                        if suitable_free_agents:
                            # Prioritize free agents if available
                            target = suitable_free_agents[0]
                            # free_agents.remove(target)

                    # Find the worst player of the team
                    if club.team:
                        min_player = min(club.team, key=lambda player: player.skill)

                        # Execute the transfer if target is better than worst player of the team
                        if target is not None and target.skill > min_player.skill and target.potential > min_player.potential:
                            self.transfer(target, club)
                            print("Club", club.unique_id, "bought player", target.unique_id)
                            self.market.remove(target)
                            # if player:
                            #     return True
                    else:
                        print("Club", club.unique_id, "has no players in the team.")
                        self.transfer(target, club)
                        print("So Club", club.unique_id, "has bought player", target.unique_id)
                        self.market.remove(target)

                if club.type == 3:
                    for player in self.market:
                        if player.club != club and player.value <= club.budget - player.salary and player.potential > potential_level:
                            target = player
                            potential_level = player.potential

                    if free_agents:
                        suitable_free_agents = [agent for agent in free_agents if agent.potential == potential_level]
                        if suitable_free_agents:
                            # Prioritize free agents if available
                            target = suitable_free_agents[0]
                            # free_agents.remove(target)

                    # Find the worst player of the team
                    if club.team:
                        min_player = min(club.team, key=lambda player: player.skill)

                        # Execute the transfer if target is better than worst player of the team
                        if target is not None and target.potential > min_player.skill:
                            self.transfer(target, club)
                            print("Club", club.unique_id, "bought player", target.unique_id)
                            self.market.remove(target)
                            # if player:
                            #     return True
                    else:
                        print("Club", club.unique_id, "has no players in the team.")
                        self.transfer(target, club)
                        print("So Club", club.unique_id, "has bought player", target.unique_id)
                        self.market.remove(target)
        
    # Use to find buyers for a specific player on sell
    def sell_incentives(self, selled_player):
        # Randomize order of clubs for fairness
        clubs = self.clubs.copy()
        random.shuffle(clubs)

        for club in clubs:
            if club != self:  # Skip current club
                target = None
                skill_level = 0
                min_potential = 0

                # Behavior for Big clubs _ search for high skill player
                if club.type == 1:
                    if selled_player.club != club and selled_player.value <= club.budget - selled_player.salary:
                        target = selled_player
                        skill_level = selled_player.skill

                    # Find the worst player of the team
                    if club.team:
                        min_player = min(club.team, key=lambda player: player.skill)

                        # Execute the transfer if target is better than worst player of the team
                        if target is not None and target.skill > min_player.skill:
                            print("Club", club.unique_id, "bought player", target.unique_id)
                            return club, target

                    else:
                        print("Club", club.unique_id, "has no players in the team.")
                        self.transfer(target, club)
                        print("So Club", club.unique_id, "has bought player", target.unique_id)
                        return club, target

                # Behavior for Medium clubs - search for players both good skill level and potential
                elif club.type == 2:
                    if (selled_player.club != club and selled_player.value <= club.budget - selled_player.salary 
                        and selled_player.potential > min_potential):
                        target = selled_player
                        skill_level = selled_player.skill
                        min_potential = selled_player.potential

                    # Find the worst player of the team based on skill level
                    if club.team:
                        min_player = min(club.team, key=lambda player: player.skill)

                        # Execute the transfer if target has higher skill and potential than the worst player of the team
                        if target is not None and target.skill > min_player.skill and target.potential > min_player.skill:
                            self.transfer(target, club)
                            print("Club", club.unique_id, "bought player", target.unique_id)
                            return club, target
                    else:
                        print("Club", club.unique_id, "has no players in the team.")
                        self.transfer(target, club)
                        print("So Club", club.unique_id, "has bought", target.unique_id)
                        return club, target

                # Behavior for Small clubs - search for players with high potential
                elif club.type == 3:
                    if (selled_player.club != club and selled_player.value <= club.budget - selled_player.salary):
                        target = selled_player
                        min_potential = selled_player.potential

                    # Find the worst player of the team based on skill level
                    if club.team:
                        min_player = min(club.team, key=lambda player: player.skill)

                        # Execute the transfer if target has higher potential than the worst player of the team
                        if target is not None and target.potential > min_player.skill:
                            self.transfer(target, club)
                            print("Club", club.unique_id, "bought player", target.unique_id)
                            return club, target
                    else:
                        print("Club", club.unique_id, "has no players in the team.")
                        self.transfer(target, club)
                        print("So Club", club.unique_id, "has bought", target.unique_id)
                        return club, target
        return False

    def signing(self, player, agent):
        # print("Before signing - player:", player)
        player.F_agent.clients.remove(player)
        player.link_agent(agent)
        
    # Search for players with higher salary or value than current clients
    def agent_incentives(self):
        # new_clients = self.pool.copy()  # Create a copy of current clients
        # num_players = len([player for player in self.model.schedule.agents if isinstance(player, Players)])
        # num_agents = len([F_agent for F_agent in self.model.schedule.agents if isinstance(F_agent, F_Agents)])
        available_players = [player for player in self.schedule.agents if isinstance(player, Players)]

        max_a = self.num_players / self.num_agents  # Maximum number of clients per agent

        for agent in self.pool:
            if agent != self:
                min_salary_client = min(agent.clients, key=lambda client: client.salary)
                min_value_client = min(agent.clients, key=lambda client: client.value)
                signing_done = False

                for player in available_players:
                    if player.F_agent != agent:
                        if not signing_done:
                            if player.salary > min_salary_client.salary:
                                # Replace the client with the higher salary player
                                # player.F_agent.clients.remove(player)
                                # agent.clients.append(player)
                                self.signing(player, agent)
                                print("Agent " + str(agent.unique_id) + " signs player " + str(player.unique_id))
                                signing_done = True  # Set flag to True
                                available_players.remove(player)
                                # if len(new_clients) > max_a:
                                #     new_clients.remove(min_salary_client)
                            elif player.value > min_value_client.value:
                                # Replace the client with the higher value player
                                print(player.unique_id)
                                # player.F_agent.clients.remove(player)
                                # agent.clients.append(player)
                                self.signing(player, agent)
                                print("Agent " + str(agent.unique_id) + " signs player " + str(player.unique_id))
                                signing_done = True  # Set flag to True
                                available_players.remove(player)
                                # if len(new_clients) > max_a:
                                #     new_clients.remove(min_value_client)
