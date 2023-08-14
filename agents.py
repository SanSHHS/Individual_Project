from mesa import Agent
import random

# Minimum number of players a club must have
MIN_SQUAD_SIZE = 11

 # Updates club's attributes according to its type when not calibrated:
def set_club_type(club, type):
    
    # 1 = Big, 2 = Medium, 3 = Small
    if type == 1:
        club.fans = random.randint(600, 1000)
        club.allowed_debt = random.randint(140, 200)

    if type == 2:
        club.fans = random.randint(200, 600)
        club.allowed_debt = random.randint(60, 140)

    if type == 3:
        club.fans = random.randint(1, 200)
        club.allowed_debt = random.randint(0, 60)

# Class for football clubs
class Club(Agent):
    def __init__(self, unique_id, model, type):
        super().__init__(unique_id, model)

        # Economic attributes
        self.revenue = 0
        self.spending = 0
        self.fans = 0
        self.budget = 0
        self.revenue_from_sales = 0
        self.allowed_debt = 0
        self.deficit = 0
        self.tv_rights = 0

        # Club identity
        self.type = type
        self.team = []
        self.interested_players = []
        self.name = ""
        self.league = ""

        # FFP attributes
        self.ffp_assessment = 0
        self.warning = 0

        set_club_type(self, type)

    # Add player to the team
    def add_player(self, player):
        self.team.append(player)

    # Calculate revenue
    def set_revenue(self):
        self.revenue = 0.5 * self.fans + self.tv_rights

    # Calculate spending
    def set_spending(self):
        self.spending = 0
        salary = sum(player.salary for player in self.team)
        other = 0.26 * self.revenue
        self.spending = round(salary + other,2)

    # Calculate deficit
    def set_deficit(self):
        x = round(self.revenue - self.spending, 2)
        if x < 0:
            self.deficit = -x
        else:
            self.deficit = 0

    # Calculate budget
    def set_budget(self):
        if not self.model.FFP:
            # print("No FFP!")
            self.set_deficit()
            diff = self.allowed_debt - self.deficit
            self.budget = round(self.revenue - self.spending + self.revenue_from_sales + diff, 2)
            self.revenue_from_sales = 0
        
        else:
            # print("FFP Budget!")
            self.budget = round(self.revenue - self.spending + self.revenue_from_sales, 2)
            self.revenue_from_sales = 0

    # Calculate the average level of the team
    def team_level(self):
        if len(self.team) > 0:
            optimal_squad_size = 25
            team_size_penalty = abs(len(self.team) - optimal_squad_size) 
            depth_factor = 1 - (team_size_penalty/ optimal_squad_size)

            total = sum(player.skill for player in self.team)
            average = round(total / len(self.team), 2)
            if self.warning >= 2:
                return average * depth_factor - 2
            else:
                return average * depth_factor
        # else:
            # print("No players in the team yet")

    # Boost fans number when winning
    def wins(self):
        self.fans = round(self.fans * 1.2)

    # Sell players
    def sell_player(self):
        while (len(self.team) > MIN_SQUAD_SIZE and self.budget < 0) or (len(self.team) > 25):
            if self.team:
                # Find the worst skilled player in the team
                min_player = min(self.team, key=lambda player: player.skill)
                # print("Min", min_player.unique_id)

                # Try to find a potential buyer club
                buyer = self.model.sell_incentives(min_player)
                if buyer:
                    buyer_club, target_player = buyer
                    # print("Club", self.unique_id, "sold player ", min_player.unique_id)
                    self.model.transfer(target_player, buyer_club)

                else:
                    # print("Club", self.unique_id, "could not find a buyer for the worst skilled player.")
                    self.release_player(min_player)
            # else:
            #     print("Club", self.unique_id, "has no players in the team.")

        # print("Club", self.unique_id, "does not need to sell a player.")

    # Release player if no buyers found
    def release_player(self, min_player):
        if min_player in self.team:
            # Remove the player from the team
            self.team.remove(min_player)

            self.spending -= min_player.salary
            self.set_budget

            # Print a message indicating the player has been released
            # print("Club", self.unique_id, "released player", min_player.unique_id)
        # else:
            # print("Release gone wrong Club", self.unique_id, "does not have player", min_player.unique_id)
        min_player.join_club(None)

    # Check balance over FFP assessment period
    def check_ffp(self):
        return self.ffp_assessment

    def step(self):

        # Reset spending after each transfer window
        if self.model.schedule.steps == 0 or self.model.schedule.steps % 2 == 1:
            self.set_spending()

        if self.model.FFP and self.model.schedule.steps != 1 and self.model.schedule.steps % 2 == 1:
            self.ffp_assessment += self.budget

        # Reset budget before each transfer window
        if self.model.schedule.steps % 2 == 0:
            self.set_budget()

        if self.model.schedule.steps != 0 and self.model.schedule.steps % 2 == 0:
            self.sell_player()

        # Test FFP sanctions
        # if self.model.schedule.steps % 12 == 0:
        #     if self.warning == 1:
        #         print(self.name + "has received a FFP warning!")
        #     elif self.warning == 2:
        #         print(self.name + "has got point deductions!")
        #     elif self.warning >= 3:
        #         print(self.name + "has got transfer bans!")

        # Test club attributes
        # squad_id = [str(player.unique_id) for player in self.team]
        # squad_list = ', '.join(squad_id)
        # print("Club " + self.name + ". My type is: " + str(self.type) + ". My team has player number: " + squad_list + ". The average level is: " + 
        #       str(self.team_level()) + ". The revenue is " + str(self.revenue) + ". The number of fan is " + str(self.fans) + ". Spending is " + 
        #       str(self.spending) + ". The allowed debt is " + str(self.allowed_debt) + ". The budget is " + str(self.budget) + ". My tv right is: " + str(self.tv_rights)
        #       + ". My league is: " + self.league)

# Class for football agents
class F_Agents(Agent):
    def __init__(self, unique_id, model, cut, n_skills):
        super().__init__(unique_id, model)
        self.cut = cut
        self.n_skills = n_skills
        self.clients = []
        self.money = 0
        self.replacement_done = False  # Flag to track replacement

    # Link players with agents
    def add_client(self, player):
        self.clients.append(player)

    # Source of income for football agents
    def earn(self, contract):
        self.money += self.cut /100 * contract
        self.money = round(self.money, 2)

    # Improve football agents' skill
    def qualifications(self):
        # Calculate the price to increase skills based on the current n_skills
        price = round(0.1 * self.n_skills ** 4, 2)

        if self.money >= price:
            self.money -= price
            self.n_skills += 1
            # print("Agent", self.unique_id, "increased n_skills by 1 for a price of", price)
        # else:
            # print("Agent", self.unique_id, "doesn't have enough money to increase n_skills.")


    def step(self):

        # Test football agents' attributes
        # client_id = [str(player.unique_id) for player in self.clients]
        # client_list = ', '.join(client_id)
        # print("Agent " + str(self.unique_id) + " My clients are: " + client_list + ". My skill is " + str(self.n_skills) + ". ")
        # print("Agent " + str(self.unique_id) + " money is " + str(self.money) + ".")

        # Check at every step if conditions met
        self.qualifications()


# Class for footballers
class Players(Agent):
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
        age_factor = max(0.1, 1 - abs(26 - self.age) / 8)

        self.salary = round(self.reputation / 2 * self.skill * age_factor * self.F_agent.n_skills * 0.15, 2)
        self.F_agent.earn(self.salary)

    # Set the players' value
    def set_value(self):
        age_factor = max(0.1, 1 - abs(26 - self.age) / 8)

        self.value = round(self.reputation / 2 * self.skill * self.potential * age_factor * self.F_agent.n_skills * 0.022, 3)

    # Link players with agents
    def link_agent(self, F_agents):
        self.F_agent = F_agents
        F_agents.add_client(self)

    # Player joins a club
    def join_club(self, club):
        if club is not None:
            self.club = club
            self.contract = "Signed"
            club.add_player(self)
        else:
            self.club = None
            self.contract = "Free agent"

    # Higher reputation when winning
    def higher_rep(self):
        self.reputation += 1

    # Set the players' potential
    def set_potential(self):
        self.potential = self.skill + random.randint(0, 10)

    # Player ages and get closer to their potential
    def ageing(self):
        self.age += 1
        if self.skill < self.potential:
            self.skill += 1

    def step(self):

        # Test players' attributes
        # print("Hi, I am player " + str(self.unique_id) + ". My age is " + str(self.age) + ". My contract is " + self.contract + ". My rep is " + 
        #       str(self.reputation) + ". My skill is " + str(self.skill) + ". My value is " + str(self.value) + " millions. My salary is " + str(self.salary) + ".")
        
        # if self.F_agent is not None and self.club is not None:
        #     print("My agent is agent " + str(self.F_agent.unique_id) + ". My club is club " + str(self.club.unique_id))
        
        # Player is one year older every 4 steps and gets new salary and value as skills may have increased
        if self.model.schedule.steps != 0 and self.model.schedule.steps % 4 == 0:
            self.ageing()
            self.set_salary()
            self.set_value()
    
