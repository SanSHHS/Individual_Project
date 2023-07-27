import mesa
from agents import *
from mesa.space import MultiGrid
import random
import numpy as np
import matplotlib.pyplot as plt
# from data import datacollector
from mesa.datacollection import DataCollector




class MyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, C, F, P, width, height, league_range, FFP = False):
        self.num_clubs = C
        self.num_agents = F
        self.num_players = P
        self.grid = MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivationByType(self)
        self.is_initial_step = True
        self.clubs = []
        self.pool = []
        self.highest_unique_id = C + F
        self.team_skill_levels = {}
        self.second_team_skill_levels = {}
        self.final_results = {}
        self.market = []
        self.FFP = FFP
        self.winner_id = None
        self.league_range = league_range
        self.running = True
        
        # Calibration
        self.league_data = {
            # 0 - 19 : Premier League 21/22 adjusted to euro
            "0": {"name": "Manchester City", "type": 1, "fan": 840, "debt": 199,  "tv": 179,},
            "1": {"name": "Liverpool", "type": 1, "fan": 850,"debt": 169, "tv": 178,},
            "2": {"name": "Manchester United", "type": 1, "fan": 1000,"debt": 94, "tv": 167,},
            "3": {"name": "Chelsea", "type": 1, "fan": 860,"debt": 51, "tv": 171,},
            "4": {"name": "Tottenham", "type": 1, "fan": 600,"debt": 143, "tv": 171,},
            "5": {"name": "Arsenal", "type": 1, "fan": 666,"debt": 35, "tv": 171,},
            "6": {"name": "West Ham", "type": 2, "fan": 236,"debt": 100, "tv": 160,},
            "7": {"name": "Leicester", "type": 2, "fan": 172,"debt": 60, "tv": 151,},
            "8": {"name": "Leeds", "type": 2, "fan": 148,"debt": 60, "tv": 134,},
            "9": {"name": "Everton", "type": 2, "fan": 128,"debt": 60, "tv": 137,},
            "10": {"name": "Newcastle", "type": 2, "fan": 106,"debt": 80, "tv": 148,},
            "11": {"name": "Brighton", "type": 2, "fan": 96,"debt": 60, "tv": 147,},
            "12": {"name": "Aston Villa", "type": 2, "fan": 98,"debt": 40, "tv": 140,},
            "13": {"name": "Wolves", "type": 3, "fan": 82,"debt": 0, "tv": 146,},
            "14": {"name": "Crystal Palace", "type": 3, "fan": 80,"debt": 0, "tv": 140,},
            "15": {"name": "Southampton", "type": 3, "fan": 80,"debt": 0, "tv": 130,},
            "16": {"name": "Brentford", "type": 3, "fan": 46,"debt": 0, "tv": 138,},
            "17": {"name": "Norwich", "type": 3, "fan": 66,"debt": 0, "tv": 118,},
            "18": {"name": "Watford", "type": 3, "fan": 50,"debt": 0, "tv": 120,},
            "19": {"name": "Burnley", "type": 3, "fan": 40,"debt": 0, "tv": 123,},

            # 20 - 39: La Liga 21/22 tv rights, 
            "20": {"name": "Real Madrid", "type": 1, "fan": 100,"debt": 120, "tv": 161,},
            "21": {"name": "Barcelona", "type": 1, "fan": 100,"debt": 120, "tv": 160,},
            "22": {"name": "Atletico de Madrid", "type": 1, "fan": 100,"debt": 120, "tv": 130,},
            "23": {"name": "Sevilla", "type": 1, "fan": 100,"debt": 120, "tv": 88,},
            "24": {"name": "Villarreal", "type": 1, "fan": 100,"debt": 120, "tv": 68,},
            "25": {"name": "Real Sociedad", "type": 1, "fan": 100,"debt": 120, "tv": 69,},
            "26": {"name": "Athletic Bilbao", "type": 1, "fan": 100,"debt": 120, "tv": 66,},
            "27": {"name": "Real Betis", "type": 1, "fan": 100,"debt": 120, "tv": 66,},
            "28": {"name": "Valencia", "type": 1, "fan": 100,"debt": 120, "tv": 70,},
            "29": {"name": "Espanyol", "type": 1, "fan": 100,"debt": 120, "tv": 55,},
            "30": {"name": "Getafe", "type": 1, "fan": 100,"debt": 120, "tv": 55,},
            "31": {"name": "Celta Vigo", "type": 1, "fan": 100,"debt": 120, "tv": 53,},
            "32": {"name": "Osasuna", "type": 1, "fan": 100,"debt": 120, "tv": 51,},
            "33": {"name": "Almeria", "type": 1, "fan": 100,"debt": 120, "tv": 51,},
            "34": {"name": "Rayo Vallecano", "type": 1, "fan": 100,"debt": 120, "tv": 46,},
            "35": {"name": "Mallorca", "type": 1, "fan": 100,"debt": 120, "tv": 46,},
            "36": {"name": "Valladolid", "type": 1, "fan": 100,"debt": 120, "tv": 50,},
            "37": {"name": "Cadiz", "type": 1, "fan": 100,"debt": 120, "tv": 48,},
            "38": {"name": "Girona", "type": 1, "fan": 100,"debt": 120, "tv": 49,},
            "39": {"name": "Elche", "type": 1, "fan": 100,"debt": 120, "tv": 46,},

            # 40 - 59: Serie A 22/23
            "40": {"name": "Inter Milan", "type": 1, "fan": 100,"debt": 120, "tv": 87,},
            "41": {"name": "Napoli", "type": 1, "fan": 100,"debt": 120, "tv": 80,},
            "42": {"name": "AC Milan", "type": 1, "fan": 100,"debt": 120, "tv": 80,},
            "43": {"name": "Juventus", "type": 1, "fan": 100,"debt": 120, "tv": 79,},
            "44": {"name": "Lazio", "type": 1, "fan": 100,"debt": 120, "tv": 71,},
            "45": {"name": "Roma", "type": 1, "fan": 100,"debt": 120, "tv": 68,},
            "46": {"name": "Fiorentina", "type": 1, "fan": 100,"debt": 120, "tv": 55,},
            "47": {"name": "Atalanta", "type": 1, "fan": 100,"debt": 120, "tv": 55,},
            "48": {"name": "Torino", "type": 1, "fan": 100,"debt": 120, "tv": 49,},
            "49": {"name": "Bologna", "type": 1, "fan": 100,"debt": 120, "tv": 44,},
            "50": {"name": "Udinese", "type": 1, "fan": 100,"debt": 120, "tv": 41,},
            "51": {"name": "Sampdoria", "type": 1, "fan": 100,"debt": 120, "tv": 39,},
            "52": {"name": "Sassuolo", "type": 1, "fan": 100,"debt": 120, "tv": 39,},
            "53": {"name": "Lecce", "type": 1, "fan": 100,"debt": 120, "tv": 39,},
            "54": {"name": "Monza", "type": 1, "fan": 100,"debt": 120, "tv": 34,},
            "55": {"name": "Hellas Verona", "type": 1, "fan": 100,"debt": 120, "tv": 34,},
            "56": {"name": "Salernitana", "type": 1, "fan": 100,"debt": 120, "tv": 33,},
            "57": {"name": "Empoli", "type": 1, "fan": 100,"debt": 120, "tv": 33,},
            "58": {"name": "Spezia", "type": 1, "fan": 100,"debt": 120, "tv": 30,},
            "59": {"name": "Cremonese", "type": 1, "fan": 100,"debt": 120, "tv": 29,},

            # 60 - 77: Bundesliga 22/23
            "60": {"name": "Bayern Munich", "type": 1, "fan": 100,"debt": 120, "tv": 95,},
            "61": {"name": "Dortmund", "type": 1, "fan": 100,"debt": 120, "tv": 82,},
            "62": {"name": "RB Leipzig", "type": 1, "fan": 100,"debt": 120, "tv": 80,},
            "63": {"name": "Bayer Leverkusen", "type": 1, "fan": 100,"debt": 120, "tv": 79,},
            "64": {"name": "Frankfurt", "type": 1, "fan": 100,"debt": 120, "tv": 77,},
            "65": {"name": "Monchengladbach", "type": 1, "fan": 100,"debt": 120, "tv": 67,},
            "66": {"name": "Wolfsburg", "type": 1, "fan": 100,"debt": 120, "tv": 65,},
            "67": {"name": "Hoffenheim", "type": 1, "fan": 100,"debt": 120, "tv": 63,},
            "68": {"name": "Freiburg", "type": 1, "fan": 100,"debt": 120, "tv": 55,},
            "69": {"name": "Union Berlin", "type": 1, "fan": 100,"debt": 120, "tv": 55,},
            "70": {"name": "Mainz 05", "type": 1, "fan": 100,"debt": 120, "tv": 51,},
            "71": {"name": "FC Koln", "type": 1, "fan": 100,"debt": 120, "tv": 50,},
            "72": {"name": "Hertha", "type": 1, "fan": 100,"debt": 120, "tv": 48,},
            "73": {"name": "Schalke 04", "type": 1, "fan": 100,"debt": 120, "tv": 44,},
            "74": {"name": "Augsburg", "type": 1, "fan": 100,"debt": 120, "tv": 44,},
            "75": {"name": "Stuttgart", "type": 1, "fan": 100,"debt": 120, "tv": 41,},
            "76": {"name": "Werder Bremen", "type": 1, "fan": 100,"debt": 120, "tv": 36,},
            "77": {"name": "Bochum", "type": 1, "fan": 100,"debt": 120, "tv": 33,},

            # 78 - 97: Ligue 1 21/22
            "78": {"name": "PSG", "type": 1, "fan": 100,"debt": 120, "tv": 140,},
            "79": {"name": "Marseilles", "type": 1, "fan": 100,"debt": 120, "tv": 57,},
            "80": {"name": "Lyon", "type": 1, "fan": 100,"debt": 120, "tv": 60,},
            "81": {"name": "LOSC", "type": 1, "fan": 100,"debt": 120, "tv": 90,},
            "82": {"name": "Monaco", "type": 1, "fan": 100,"debt": 120, "tv": 59,},
            "83": {"name": "Rennes", "type": 1, "fan": 100,"debt": 120, "tv": 37,},
            "84": {"name": "Angers", "type": 1, "fan": 100,"debt": 120, "tv": 19,},
            "85": {"name": "Bordeaux", "type": 1, "fan": 100,"debt": 120, "tv": 21,},
            "86": {"name": "Brest", "type": 1, "fan": 100,"debt": 120, "tv": 17,},
            "87": {"name": "Clermont", "type": 1, "fan": 100,"debt": 120, "tv": 16,},
            "88": {"name": "Lens", "type": 1, "fan": 100,"debt": 120, "tv": 21,},
            "89": {"name": "Lorient", "type": 1, "fan": 100,"debt": 120, "tv": 16,},
            "90": {"name": "Metz", "type": 1, "fan": 100,"debt": 120, "tv": 17,},
            "91": {"name": "Montpellier", "type": 1, "fan": 100,"debt": 120, "tv": 21,},
            "92": {"name": "Nantes", "type": 1, "fan": 100,"debt": 120, "tv": 25,},
            "93": {"name": "Nice", "type": 1, "fan": 100,"debt": 120, "tv": 29,},
            "94": {"name": "Reims", "type": 1, "fan": 100,"debt": 120, "tv": 19,},
            "95": {"name": "Saint-Etienne", "type": 1, "fan": 100,"debt": 120, "tv": 32,},
            "96": {"name": "Strasbourg", "type": 1, "fan": 100,"debt": 120, "tv": 24,},
            "97": {"name": "Troyes", "type": 1, "fan": 100,"debt": 120, "tv": 16,},
        
        }
        
        self.datacollector = DataCollector(
            model_reporters={
                "Winner Club": self.get_winner,
            }
        )

        # Creating agents
        self.create_clubs(C)
        self.create_agents(F)
        self.create_players(P)

    def step(self):
        # Collect data at each step
        # datacollector.collect(self)

        """Advance the model by one step."""
        # print("Step:", self.schedule.steps)
        # First step 
        if self.is_initial_step:
            print("Step: 0")
            self.is_initial_step = False
        self.schedule.step()
        # self.retire_players()

        # First step 
        # if self.is_initial_step:
        #     print("First Step")
        #     self.is_initial_step = False
        print("\nStep:", self.schedule.steps)

        if self.schedule.steps != 0:
            self.agent_incentives()

        if self.schedule.steps != 0 and self.schedule.steps % 4 == 0:
            print("Season over")
            self.final_skill_levels()
            self.print_final_skill_levels()
            self.winner()
            self.retire_players()

            # self.datacollector.collect(self)


        if self.schedule.steps != 0 and self.schedule.steps % 2 == 0:
            self.average_skill_levels()
            self.print_average_skill_levels()
            print("Transfer market opens")
            self.open_market()
            self.club_incentives()

            
        # self.schedule.step()
        # self.retire_players()

        player_count = self.count_players()
        # print("Number of players: ", player_count)

        # If a player retires, a new player will be created
        if player_count < self.num_players:
            self.create_players(self.num_players - player_count)

        if self.schedule.steps != 1 and self.schedule.steps % 2 == 1:

            print("Close")
            # self.average_skill_levels()
            # self.print_average_skill_levels()
            # self.print_club_spending()

        # player_count = self.count_players()
        # print("Number of players: ", player_count)

        print("\n")
        # Collect data at each step
        self.datacollector.collect(self)



    # Functions
    def create_clubs(self, C):
        start, end = self.league_range
        if C == end - start + 1:
            for i, keys in enumerate(range(start, end+1)):
                club_data = self.league_data[str(keys)]
                club = Club(i, self, type = random.randint(1, 3))
                club.name = club_data["name"]
                club.type = club_data["type"]
                club.fans = club_data["fan"]
                club.allowed_debt = club_data["debt"]
                club.tv_rights = club_data["tv"]
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
        players_to_retire = [player for player in self.schedule.agents if isinstance(player, Players) and player.age == 37]
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
            for club in self.clubs:
                if club_id == club.unique_id:
                    print("Club " + str(club.name) + " season average level is: " + str(team_skill))

    # Determine the winners
    def winner(self):
        max_key = max(self.final_results, key = lambda x: self.final_results[x])
        winning_club = None
        season = round(self.schedule.steps / 4)
        
        for club in self.clubs:
            if club.unique_id == max_key:
                winning_club = club
                break

        if winning_club is not None:
            print("The winner of season " + str(season) + " is " + str(winning_club.name) + ". \n")
            self.winner_id = max_key

            for player in winning_club.team:
                player.higher_rep()
                player.set_salary()

            winning_club.wins()
            winning_club.set_revenue()
            winning_club.set_spending()
            winning_club.set_budget()
        else:
            print("No winning team.")

    def get_winner(self):
        return self.winner_id

    # Print club spending
    def print_club_spending(self):
        for club in self.clubs:
            print("Club " + str(club.unique_id) + " spends " + str(round(club.spending,2)) + ".") 

    # Open the market and list all the players
    def open_market(self):
        self.market = [agent for agent in self.schedule.agents if isinstance(agent, Players)]

    # Player transfer
    def transfer(self, player, club):
        print("Club", club.unique_id, "bought player", player.unique_id)
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

    # Player transfer
    def bid(self, player, club, offer):
        print("Club", club.unique_id, "bought player", player.unique_id)
        if player.club is not None:
            # Change attributes following the transfer
            player.club.revenue_from_sales += offer
            player.club.spending -= player.salary
            player.club.team.remove(player)

        player.F_agent.earn(player.value)
        player.join_club(club)
        club.budget -= offer
        club.set_spending()

    # Add a method to initiate a bidding war
    def initiate_bidding_war(self, player, interested_clubs):
        best_offer = None
        best_offer_value = 0

        for club in interested_clubs:
            # Create a bidding logic to determine the value of the offer
            budget_factor = club.budget / (player.value * 2)
            # normalized_budget_factor = max(0.1, min(1.0, budget_factor))  # Normalize to a value between 0.1 and 1.0
            # offer_value = player.value * normalized_budget_factor
            offer_value = player.value * budget_factor

            if offer_value > best_offer_value:
                best_offer = club
                best_offer_value = offer_value

        if best_offer is not None:
            # The player accepts the best offer and joins the club
            print("Player", player.unique_id, "accepts the offer from Club", best_offer.unique_id)
            if player.club is not None:
                    if len(player.club.team) > MIN_SQUAD_SIZE:
                        self.bid(player, best_offer, best_offer_value)
                    else:
                        print("Seller club does not have enough player.")

            # Remove the player from the interested list of other clubs
            for club in interested_clubs:
                club.interested_player.remove(player)
            return True
        else:
            print("Player", player.unique_id, "rejects all offers.")
            return False


    # Club buys players
    def club_incentives(self):
        # Randomize order of clubs for fairness
        clubs = self.clubs.copy()
        random.shuffle(clubs)

        for club in clubs:
            if club != self:  # Skip current club
                target_list = []
                min_player = None  # Initialize min_player to None

                 # Find the worst player of the team
                if club.team:
                    min_player = min(club.team, key=lambda player: player.skill)
                else:
                    print("Club", club.unique_id, "has no players in the team.")

                if club.type == 1:

                    for player in self.market:
                        if player.club != club and player.value <= club.budget - player.salary and player.skill > min_player.skill:
                            target_list.append(player)

                    target_list.sort(key=lambda player: (player.skill, player.contract == "Free agent"), reverse=True)


                if club.type == 2:
                    
                    for player in self.market:
                        if player.club != club and player.value <= club.budget - player.salary and player.skill > min_player.skill and player.potential > min_player.potential:
                            target_list.append(player)

                    target_list.sort(key=lambda player: (player.skill, player.potential, player.contract == "Free agent"), reverse=True)


                if club.type == 3:
                    for player in self.market:
                        if player.club != club and player.value <= club.budget - player.salary and player.potential > min_player.potential:
                            target_list.append(player)

                    target_list.sort(key=lambda player: (player.potential, player.contract == "Free agent"), reverse=True)

                club.interested_player = target_list 

        # Check for players targeted by multiple clubs
        targeted_players = set()
        for club in clubs:
            for player in club.interested_player:
                if player in targeted_players:
                    # Bidding war is initiated
                    interested_clubs = [c for c in clubs if player in c.interested_player]
                    self.initiate_bidding_war(player, interested_clubs)
                else:
                    targeted_players.add(player)

        # If a player has only one interested club, transfer directly without bidding war
        for player in targeted_players:
            interested_clubs = [c for c in clubs if player in c.interested_player]
            if len(interested_clubs) == 1:
                if player.club is not None:
                    if len(player.club.team) > MIN_SQUAD_SIZE:
                        self.transfer(player, interested_clubs[0])
                    else:
                        print("Seller club does not have enough player.")

        
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
                                # print("Agent " + str(agent.unique_id) + " signs player " + str(player.unique_id))
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
                                # print("Agent " + str(agent.unique_id) + " signs player " + str(player.unique_id))
                                signing_done = True  # Set flag to True
                                available_players.remove(player)
                                # if len(new_clients) > max_a:
                                #     new_clients.remove(min_value_client)
