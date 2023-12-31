import mesa
from agents import *
import random
from statistics import mean
from mesa.datacollection import DataCollector

class MyModel(mesa.Model):

    def __init__(self, C, F, P, league_range = None, FFP = False):
        # Attributes to keep track of the unique ids of agents
        self.num_clubs = C
        self.num_agents = F
        self.num_players = P
        self.highest_unique_id = C + F

        # Attributes to store all concerned agents in the model
        self.clubs = []
        self.pool = []
        self.market = []

        # Attributes for winning clubs
        self.club_id = 0
        self.team_skill_levels = {}
        self.second_team_skill_levels = {}
        self.final_results = {}
        self.winner_id = None
        self.winner_name = None
        self.winner_level = None

        # Other attributes
        self.schedule = mesa.time.RandomActivationByType(self)
        self.is_initial_step = True
        self.FFP = FFP
        self.league_range = league_range
        self.season = 0
        self.running = True
        self.transfer_values_by_type = {1: [], 2: [], 3: []}
        
        # Calibration of top 5 leagues, ordered from 0 - 97, 98 clubs in total
        self.league_data = {
            # 0 - 19 : Premier League 21/22, adjusted to euros
            "0": {"name": "Manchester City", "type": 1, "fan": 840, "debt": 199,  "tv": 179,},
            "1": {"name": "Liverpool", "type": 1, "fan": 850,"debt": 149, "tv": 178,},
            "2": {"name": "Manchester United", "type": 1, "fan": 1000,"debt": 150, "tv": 167,},
            "3": {"name": "Chelsea", "type": 1, "fan": 860,"debt": 181, "tv": 171,},
            "4": {"name": "Tottenham", "type": 1, "fan": 600,"debt": 143, "tv": 171,},
            "5": {"name": "Arsenal", "type": 1, "fan": 666,"debt": 35, "tv": 171,},
            "6": {"name": "West Ham", "type": 2, "fan": 236,"debt": 100, "tv": 160,},
            "7": {"name": "Leicester", "type": 2, "fan": 172,"debt": 60, "tv": 151,},
            "8": {"name": "Leeds", "type": 2, "fan": 148,"debt": 60, "tv": 134,},
            "9": {"name": "Everton", "type": 2, "fan": 128,"debt": 60, "tv": 137,},
            "10": {"name": "Newcastle", "type": 2, "fan": 206,"debt": 80, "tv": 148,},
            "11": {"name": "Brighton", "type": 2, "fan": 126,"debt": 60, "tv": 147,},
            "12": {"name": "Aston Villa", "type": 2, "fan": 138,"debt": 40, "tv": 140,},
            "13": {"name": "Wolves", "type": 3, "fan": 82,"debt": 0, "tv": 146,},
            "14": {"name": "Crystal Palace", "type": 3, "fan": 80,"debt": 0, "tv": 140,},
            "15": {"name": "Southampton", "type": 3, "fan": 80,"debt": 0, "tv": 130,},
            "16": {"name": "Brentford", "type": 3, "fan": 46,"debt": 0, "tv": 138,},
            "17": {"name": "Norwich", "type": 3, "fan": 66,"debt": 0, "tv": 118,},
            "18": {"name": "Watford", "type": 3, "fan": 50,"debt": 0, "tv": 120,},
            "19": {"name": "Burnley", "type": 3, "fan": 40,"debt": 0, "tv": 123,},

            # 20 - 39: La Liga 21/22 
            "20": {"name": "Real Madrid", "type": 1, "fan": 1106,"debt": 150, "tv": 161,},
            "21": {"name": "Barcelona", "type": 1, "fan": 956,"debt": 0, "tv": 160,},
            "22": {"name": "Atletico de Madrid", "type": 1, "fan": 484,"debt": 80, "tv": 130,},
            "23": {"name": "Sevilla", "type": 2, "fan": 290,"debt": 70, "tv": 88,},
            "24": {"name": "Villarreal", "type": 2, "fan": 120,"debt": 60, "tv": 68,},
            "25": {"name": "Real Sociedad", "type": 2, "fan": 56,"debt": 70, "tv": 69,},
            "26": {"name": "Athletic Bilbao", "type": 2, "fan": 86,"debt": 60, "tv": 66,},
            "27": {"name": "Real Betis", "type": 2, "fan": 68,"debt": 50, "tv": 66,},
            "28": {"name": "Valencia", "type": 2, "fan": 76,"debt": 10, "tv": 70,},
            "29": {"name": "Espanyol", "type": 3, "fan": 46,"debt": 8, "tv": 55,},
            "30": {"name": "Getafe", "type": 3, "fan": 45,"debt": 8, "tv": 55,},
            "31": {"name": "Celta Vigo", "type": 3, "fan": 40,"debt": 8, "tv": 53,},
            "32": {"name": "Osasuna", "type": 3, "fan": 35,"debt": 7, "tv": 51,},
            "33": {"name": "Almeria", "type": 3, "fan": 20,"debt": 3, "tv": 51,},
            "34": {"name": "Rayo Vallecano", "type": 3, "fan": 20,"debt": 3, "tv": 46,},
            "35": {"name": "Mallorca", "type": 3, "fan": 20,"debt": 3, "tv": 46,},
            "36": {"name": "Valladolid", "type": 3, "fan": 30,"debt": 5, "tv": 50,},
            "37": {"name": "Cadiz", "type": 3, "fan": 30,"debt": 5, "tv": 48,},
            "38": {"name": "Girona", "type": 3, "fan": 20,"debt": 3, "tv": 49,},
            "39": {"name": "Elche", "type": 3, "fan": 35,"debt": 6, "tv": 46,},

            # 40 - 59: Serie A 22/23
            "40": {"name": "Inter Milan", "type": 1, "fan": 442,"debt": 60, "tv": 87,},
            "41": {"name": "Napoli", "type": 2, "fan": 240,"debt": 50, "tv": 80,},
            "42": {"name": "AC Milan", "type": 1, "fan": 400,"debt": 65, "tv": 80,},
            "43": {"name": "Juventus", "type": 1, "fan": 642,"debt": 70, "tv": 79,},
            "44": {"name": "Lazio", "type": 2, "fan": 130,"debt": 40, "tv": 71,},
            "45": {"name": "Roma", "type": 2, "fan": 276,"debt": 50, "tv": 68,},
            "46": {"name": "Fiorentina", "type": 2, "fan": 194, "debt": 45, "tv": 55,},
            "47": {"name": "Atalanta", "type": 2, "fan": 130,"debt": 40, "tv": 55,},
            "48": {"name": "Torino", "type": 3, "fan": 70,"debt": 20, "tv": 49,},
            "49": {"name": "Bologna", "type": 3, "fan": 72,"debt": 20, "tv": 44,},
            "50": {"name": "Udinese", "type": 3, "fan": 74,"debt": 21, "tv": 41,},
            "51": {"name": "Sampdoria", "type": 3, "fan": 74,"debt": 20, "tv": 39,},
            "52": {"name": "Sassuolo", "type": 2, "fan": 120,"debt": 30, "tv": 39,},
            "53": {"name": "Lecce", "type": 3, "fan": 35,"debt": 5, "tv": 39,},
            "54": {"name": "Monza", "type": 3, "fan": 30,"debt": 0, "tv": 34,},
            "55": {"name": "Hellas Verona", "type": 3, "fan": 102,"debt": 30, "tv": 34,},
            "56": {"name": "Salernitana", "type": 3, "fan": 28,"debt": 0, "tv": 33,},
            "57": {"name": "Empoli", "type": 3, "fan": 76,"debt": 18, "tv": 33,},
            "58": {"name": "Spezia", "type": 3, "fan": 22,"debt": 0, "tv": 30,},
            "59": {"name": "Cremonese", "type": 3, "fan": 33,"debt": 0, "tv": 29,},

            # 60 - 77: Bundesliga 22/23
            "60": {"name": "Bayern Munich", "type": 1, "fan": 900,"debt": 120, "tv": 95,},
            "61": {"name": "Dortmund", "type": 1, "fan": 676,"debt": 90, "tv": 82,},
            "62": {"name": "RB Leipzig", "type": 2, "fan": 380,"debt": 80, "tv": 80,},
            "63": {"name": "Bayer Leverkusen", "type": 2, "fan": 248,"debt": 45, "tv": 79,},
            "64": {"name": "Frankfurt", "type": 2, "fan": 242,"debt": 45, "tv": 77,},
            "65": {"name": "Monchengladbach", "type": 3, "fan": 124,"debt": 28, "tv": 67,},
            "66": {"name": "Wolfsburg", "type": 2, "fan": 168,"debt": 30, "tv": 65,},
            "67": {"name": "Hoffenheim", "type": 3, "fan": 116,"debt": 18, "tv": 63,},
            "68": {"name": "Freiburg", "type": 3, "fan": 120,"debt": 18, "tv": 55,},
            "69": {"name": "Union Berlin", "type": 3, "fan": 134,"debt": 20, "tv": 55,},
            "70": {"name": "Mainz 05", "type": 3, "fan": 128,"debt": 20, "tv": 51,},
            "71": {"name": "FC Koln", "type": 3, "fan": 96,"debt": 25, "tv": 50,},
            "72": {"name": "Hertha", "type": 3, "fan": 98,"debt": 25, "tv": 48,},
            "73": {"name": "Schalke 04", "type": 3, "fan": 146,"debt": 30, "tv": 44,},
            "74": {"name": "Augsburg", "type": 3, "fan": 94,"debt": 12, "tv": 44,},
            "75": {"name": "Stuttgart", "type": 3, "fan": 98,"debt": 28, "tv": 41,},
            "76": {"name": "Werder Bremen", "type": 3, "fan": 114,"debt": 20, "tv": 36,},
            "77": {"name": "Bochum", "type": 3, "fan": 66,"debt": 10, "tv": 33,},

            # 78 - 97: Ligue 1 21/22
            "78": {"name": "PSG", "type": 1, "fan": 950,"debt": 200, "tv": 140,},
            "79": {"name": "Marseilles", "type": 2, "fan": 362,"debt": 40, "tv": 57,},
            "80": {"name": "Lyon", "type": 2, "fan": 200,"debt": 10, "tv": 60,},
            "81": {"name": "LOSC", "type": 2, "fan": 116,"debt": 40, "tv": 90,},
            "82": {"name": "Monaco", "type": 2, "fan": 54,"debt": 40, "tv": 59,},
            "83": {"name": "Rennes", "type": 2, "fan": 92,"debt": 35, "tv": 37,},
            "84": {"name": "Angers", "type": 3, "fan": 32,"debt": 5, "tv": 19,},
            "85": {"name": "Bordeaux", "type": 3, "fan": 58,"debt": 10, "tv": 21,},
            "86": {"name": "Brest", "type": 3, "fan": 54,"debt": 8, "tv": 17,},
            "87": {"name": "Clermont", "type": 3, "fan": 20,"debt": 0, "tv": 16,},
            "88": {"name": "Lens", "type": 3, "fan": 52,"debt": 12, "tv": 21,},
            "89": {"name": "Lorient", "type": 3, "fan": 36,"debt": 8, "tv": 16,},
            "90": {"name": "Metz", "type": 3, "fan": 38,"debt": 8, "tv": 17,},
            "91": {"name": "Montpellier", "type": 3, "fan": 36,"debt": 10, "tv": 21,},
            "92": {"name": "Nantes", "type": 3, "fan": 54,"debt": 15, "tv": 25,},
            "93": {"name": "Nice", "type": 2, "fan": 98,"debt": 30, "tv": 29,},
            "94": {"name": "Reims", "type": 3, "fan": 34,"debt": 8, "tv": 19,},
            "95": {"name": "Saint-Etienne", "type": 2, "fan": 80,"debt": 30, "tv": 32,},
            "96": {"name": "Strasbourg", "type": 3, "fan": 66,"debt": 20, "tv": 24,},
            "97": {"name": "Troyes", "type": 3, "fan": 20,"debt": 0, "tv": 16,},
        
        }
        
        # Data collection for analysis
        self.datacollector = DataCollector(
            model_reporters={
                "Winner Club": self.get_winner,
                "Winner level": self.get_level,
                "Season": lambda model: model.season,
                "Average revenue by league": self.calculate_avg_revenue_by_league,
                "Total revenue by league": self.calculate_total_revenue_by_league,
                "Average Transferred Value (Type 1)": lambda model: model.calculate_transfers(1),
                "Average Transferred Value (Type 2)": lambda model: model.calculate_transfers(2),
                "Average Transferred Value (Type 3)": lambda model: model.calculate_transfers(3),
            },
            agent_reporters={
                "Club Revenue": lambda agent: agent.revenue if isinstance(agent, Club) else None,
                "Team size": lambda agent: len(agent.team) if isinstance(agent, Club) else None,
                "Name": lambda agent: agent.name if isinstance(agent, Club) else None,
                "TV": lambda agent: agent.tv_rights if isinstance(agent, Club) else None,
                "Type": lambda agent: agent.type if isinstance(agent, Club) else None,
            },
        )

        # Creating agents
        self.create_clubs(C)
        self.create_agents(F)
        self.create_players(P)

    def step(self):

        if self.is_initial_step:
            # print("Step: 0")
            self.is_initial_step = False
        self.schedule.step()

        # print("\nStep:", self.schedule.steps)

        if self.schedule.steps != 0:
            self.agent_incentives()

        if self.schedule.steps != 0 and self.schedule.steps % 4 == 0:
            # print("Season over")
            self.final_skill_levels()
            # self.print_final_skill_levels()
            self.winner()
            self.retire_players()
            
        if self.schedule.steps != 0 and self.schedule.steps % 2 == 0:
            self.average_skill_levels()
            # self.print_average_skill_levels()
            # print("Transfer market opens")
            self.open_market()
            self.club_incentives()

        player_count = self.count_players()
        # print("Number of players: ", player_count)

        # If a player retires, a new player will be created
        if player_count < self.num_players:
            self.create_players(self.num_players - player_count)

        # if self.schedule.steps != 1 and self.schedule.steps % 2 == 1:
            # print("Close")
            # self.average_skill_levels()
            # self.print_average_skill_levels()
            # self.print_club_spending()

        # Check FFP every 3 seasons
        if self.FFP and self.schedule.steps % 12 == 0:
            self.sanctions

        # Collect data at each step
        self.datacollector.collect(self)        


    # Functions
    def create_clubs(self, C):
        if self.league_range is not None:
            # Handle single league range
            if not isinstance(self.league_range, list):
                self.league_range = [self.league_range]

            # Calibrate attributes
            for league_range in self.league_range:
                start, end = league_range
                for keys in range(start, end+1):
                    club_data = self.league_data[str(keys)]
                    club = Club(self.club_id, self, type = random.randint(1, 3))
                    self.club_id += 1
                    club.name = club_data["name"]
                    club.type = club_data["type"]
                    club.fans = club_data["fan"]
                    club.allowed_debt = club_data["debt"]
                    club.tv_rights = club_data["tv"]
                    club.set_revenue()
                    club.set_spending()

                    # Determine the club's league based on its key in league_data
                    if 0 <= keys <= 19:
                        club.league = "Premier League"
                    elif 20 <= keys <= 39:
                        club.league = "La Liga"
                    elif 40 <= keys <= 59:
                        club.league = "Serie A"
                    elif 60 <= keys <= 77:
                        club.league = "Bundesliga"
                    elif 78 <= keys <= 97:
                        club.league = "Ligue 1"

                    self.schedule.add(club)
                    self.clubs.append(club)

        # No calibration
        else:
            for i in range(C):
                club = Club(self.club_id, self, type = random.randint(1, 3))
                club.name = str(self.club_id)
                self.club_id += 1
                club.set_revenue()
                club.set_spending()
                self.schedule.add(club)
                self.clubs.append(club)


    def create_agents(self, F):
        for i in range(F):
            f_agent = F_Agents(self.num_clubs + i, self, cut = random.randint(3, 10), n_skills = random.randint(1, 10))
            self.schedule.add(f_agent)
            self.pool.append(f_agent)


    def create_players(self, P):
        for i in range(P):
            self.highest_unique_id += 1
            player_id = self.highest_unique_id
            player = Players(player_id, self, age = random.randint(18, 36), contract = "Signed", reputation = random.randint(1, 10), 
                             skill = random.randint(1, 10))
            player.set_potential()
            self.schedule.add(player)

            # Link players to agents evenly
            max_a = self.num_players / self.num_agents
            available_agents = [a for a in self.pool if len(a.clients) < max_a]

            if available_agents:
                choice = random.choice(available_agents)
                player.link_agent(choice)
            # else:
            #     print("No available agents to link player", player_id)

            # Link players to clubs evenly
            max_c = self.num_players / self.num_clubs
            available_clubs = [c for c in self.clubs if len(c.team) < max_c]
            if available_clubs:
                choice = random.choice(available_clubs)
                player.join_club(choice)
            # else:
            #     print("No available clubs to join for player", player_id)

            player.set_salary()
            player.set_value()

    # Players go to retirement when they are 37 years old
    def retire_players(self):
        players_to_retire = [player for player in self.schedule.agents if isinstance(player, Players) and player.age == 37]
        if players_to_retire:
            for agent in players_to_retire:
                # print("Player " + str(agent.unique_id) + " retires!")

                if agent.F_agent is not None:
                    agent.F_agent.clients.remove(agent)

                if agent.club is not None:
                    agent.club.team.remove(agent)

                self.schedule.remove(agent)
                # self.grid.remove_agent(agent)
        # else:
        #     print("No players retire!")

    # Count current players in the model
    def count_players(self):
        count = 0
        for agent in self.schedule.agents:
            if isinstance(agent, Players):
                count += 1
        return count
    
    # Check FFP for clubs
    def sanctions(self):
        assess = 0
        for club in self.clubs:
            assess = club.check_ffp()
            if assess < -5:
                club.warning += 1
            else:
                club.warning = 0

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

    # Determine the winners
    def winner(self):
        max_key = max(self.final_results, key = lambda x: self.final_results[x])
        winning_club = None
        winning_level = None
        self.season = round(self.schedule.steps / 4)
        
        for club in self.clubs:
            if club.unique_id == max_key:
                winning_club = club
                winning_level = self.final_results[max_key]
                break

        if winning_club is not None:
            # print("The winner of season " + str(self.season) + " is " + str(winning_club.name) + ". \n")
            self.winner_id = max_key
            self.winner_name = winning_club.name
            self.winner_level = winning_level

            for player in winning_club.team:
                player.higher_rep()
                player.set_salary()

            winning_club.wins()
            winning_club.set_revenue()
            winning_club.set_spending()
            winning_club.set_budget()
        else:
            print("No winning team.")

    # Print club spending
    def print_club_spending(self):
        for club in self.clubs:
            print("Club " + str(club.name) + " spends " + str(round(club.spending,2)) + ".") 

    # Open the market and list all the players
    def open_market(self):
        self.market = [agent for agent in self.schedule.agents if isinstance(agent, Players)]

    # Player transfer
    def transfer(self, player, club):
        # print("Club", club.unique_id, "bought player", player.unique_id,"for", player.value)
        if player.value <= club.budget:
            transfer_value = player.value

            # If player has a contract
            if player.club is not None:
                # Change attributes following the transfer
                player.club.revenue_from_sales += transfer_value
                player.club.spending -= player.salary
                player.club.team.remove(player)
                player.club.set_budget()
                self.transfer_values_by_type[club.type].append(transfer_value)

            player.F_agent.earn(transfer_value)
            player.join_club(club)
            club.budget -= transfer_value
            club.set_spending()

    # Player transfer
    def bid(self, player, club, offer):
        # print("Club", club.unique_id, "bought player", player.unique_id,"for", offer)
        if offer <= club.budget:

            # If player has a contract
            if player.club is not None:
                # Change attributes following the transfer
                player.club.revenue_from_sales += offer
                player.club.spending -= player.salary
                player.club.team.remove(player)
                player.club.set_budget()
                self.transfer_values_by_type[club.type].append(offer)

            player.F_agent.earn(offer)
            player.join_club(club)
            club.budget -= offer
            club.set_spending()

    # Initiate a bidding war
    def initiate_bidding_war(self, player, interested_clubs):
        best_offer = None
        best_offer_value = player.value

        for club in interested_clubs:
            # Create a bidding logic to determine the value of the offer
            budget_factor = club.budget / (player.value * 2)
            offer_value = player.value * budget_factor

            if offer_value > best_offer_value:
                best_offer = club
                best_offer_value = offer_value

        if best_offer is not None:
            # The player joins the club
            # print("Player", player.unique_id, "joins the Club", best_offer.unique_id)
            if player.club is not None:
                if len(player.club.team) > MIN_SQUAD_SIZE:
                    self.bid(player, best_offer, best_offer_value)
                # else:
                #     print("Seller club does not have enough player.")
            else:
                self.bid(player, best_offer, best_offer_value)
            
            # Remove the player from the interested list of other clubs
            for club in interested_clubs:
                club.interested_player.remove(player)
            return True
        else:
            # print("Player", player.unique_id, "rejects all offers.")
            return False


    # Club buys players
    def club_incentives(self):
        # Randomize order of clubs for fairness
        clubs = self.clubs.copy()
        random.shuffle(clubs)

        for club in clubs:
            if club != self and club.warning < 3:  # Skip current club and club with transfer bans
                target_list = []
                min_player = None  # Initialize min_player to None

                 # Find the worst player of the team
                if club.team:
                    min_player = min(club.team, key=lambda player: player.skill)
                # else:
                #     print("Club", club.unique_id, "has no players in the team.")

                # Big club strategy
                if club.type == 1:
                    for player in self.market:
                        if player.club != club and player.value <= club.budget - player.salary and player.skill > min_player.skill:
                            target_list.append(player)

                    target_list.sort(key=lambda player: (player.skill, player.contract == "Free agent"), reverse=True)

                # Medium club strategy
                if club.type == 2:               
                    for player in self.market:
                        if player.club != club and player.value <= club.budget - player.salary and player.skill > min_player.skill and player.potential > min_player.potential:
                            target_list.append(player)
                    target_list.sort(key=lambda player: (player.skill, player.potential, player.contract == "Free agent"), reverse=True)

                # Small club strategy
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
                    # else:
                    #     print("Seller club does not have enough player.")
                else:
                    self.transfer(player, interested_clubs[0])

    # Use to find buyers for a specific player on sell
    def sell_incentives(self, selled_player):
        # Randomize order of clubs for fairness
        clubs = self.clubs.copy()
        random.shuffle(clubs)

        for club in clubs:
            if club != self and club.warning < 3:  # Skip current club and club with transfer bans
                target = None
                skill_level = 0
                min_potential = 0

                # Behavior for Big clubs _ search for high skill player
                if club.type == 1:
                    if selled_player.club != club and selled_player.value <= club.budget - selled_player.salary:
                        target = selled_player

                    # Find the worst player of the team
                    if club.team:
                        min_player = min(club.team, key=lambda player: player.skill)

                        # Execute the transfer if target is better than worst player of the team
                        if target is not None and target.skill > min_player.skill:
                            # print("Club", club.unique_id, "bought player", target.unique_id)
                            return club, target

                    else:
                        # print("Club", club.unique_id, "has no players in the team.")
                        self.transfer(target, club)
                        # print("So Club", club.unique_id, "has bought player", target.unique_id)
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
                            # print("Club", club.unique_id, "bought player", target.unique_id)
                            return club, target
                    else:
                        # print("Club", club.unique_id, "has no players in the team.")
                        self.transfer(target, club)
                        # print("So Club", club.unique_id, "has bought", target.unique_id)
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
                            # print("Club", club.unique_id, "bought player", target.unique_id)
                            return club, target
                    else:
                        # print("Club", club.unique_id, "has no players in the team.")
                        self.transfer(target, club)
                        # print("So Club", club.unique_id, "has bought", target.unique_id)
                        return club, target
        return False

    # Sign a player to a new agent
    def signing(self, player, agent):
        # print("Before signing - player:", player)
        player.F_agent.money += player.value/2
        player.F_agent.clients.remove(player)
        player.link_agent(agent)
        agent.money -= player.value/2
        
    # Search for players with higher salary or value than current clients, for agents
    def agent_incentives(self):
        available_players = [player for player in self.schedule.agents if isinstance(player, Players)]

        for agent in self.pool:
            if agent != self:
                min_salary_client = min(agent.clients, key=lambda client: client.salary)
                min_value_client = min(agent.clients, key=lambda client: client.value)
                signing_done = False

                for player in available_players:
                    if player.F_agent != agent and len(player.F_agent.clients) > 1 and agent.money >= player.value / 2:
                        if not signing_done:
                            if agent.n_skills > player.F_agent.n_skills:
                                if player.salary > min_salary_client.salary:
                                    self.signing(player, agent)
                                    signing_done = True  # Set flag to True
                                    available_players.remove(player)

                                elif player.value > min_value_client.value:
                                    # Replace the client with the higher value player
                                    self.signing(player, agent)
                                    signing_done = True  # Set flag to True
                                    available_players.remove(player)

    # Data Collector methods
    def get_winner(self):
        return self.winner_name
    
    def get_level(self):
        return self.winner_level
    
    def calculate_avg_revenue_by_league(self):
        league_revenue = {}
        for club in self.clubs:
            league = club.league
            revenue = club.revenue
            if league in league_revenue:
                league_revenue[league].append(revenue)
            else:
                league_revenue[league] = [revenue]
        
        avg_revenue_by_league = {}
        for league, revenues in league_revenue.items():
            avg_revenue_by_league[league] = round(sum(revenues) / len(revenues),2)
        
        return avg_revenue_by_league
    
    def calculate_total_revenue_by_league(self):
        league_revenue = {}
        for club in self.clubs:
            league = club.league
            revenue = club.revenue
            if league in league_revenue:
                league_revenue[league] += revenue
            else:
                league_revenue[league] = revenue

        return league_revenue

    def team_size(self):
        team_sizes = {club.unique_id: len(club.team) for club in self.clubs}
        return team_sizes
    
    # Calculate average transfer value by club category
    def calculate_transfers(self, club_type):
        values = self.transfer_values_by_type.get(club_type, [])
        if values:
            return mean(values)
        else: 
            return None