import mesa


class MoneyAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1

class MoneyAgent1(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1

class MoneyAgent2(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1


class MoneyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)

        # Create agents
        for i in range(self.num_agents):
            a = MoneyAgent(i, self)
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents):
            a = MoneyAgent1(i + N, self)
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents):
            a = MoneyAgent2(i + N + N, self)
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

def agent_portrayal(agent):
    if isinstance(agent, MoneyAgent):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 0,
            "Color": "blue",
            "r": 0.5
        }
    elif isinstance(agent, MoneyAgent1):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 0,
            "Color": "green",
            "r": 0.5

        }
    elif isinstance(agent, MoneyAgent2):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 0,
            "Color": "red",
            "r": 0.5

        }
    else:
        # Default portrayal for other agent types
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 0,
            "Color": "gray",
            "r": 0.5

        }
    
    return portrayal

# In addition to the portrayal method, we instantiate a canvas grid with its width and height in cells, and in pixels. In this case, 
# let’s create a 10x10 grid, drawn in 500 x 500 pixels.
grid = mesa.visualization.CanvasGrid(agent_portrayal, 10, 10, 500, 500)

# Any inputs or arguments for the model itself. In this case, 100 agents, and height and width of 10.
server = mesa.visualization.ModularServer(
    MoneyModel, [grid], "Money Model", {"N": 10, "width": 10, "height": 10}
)

server.port = 8521 # The default
server.launch()