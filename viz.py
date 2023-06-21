
from agent import *
from model import *
import mesa
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter


NUMBER_OF_CELLS = 100

SIZE_OF_CANVAS_IN_PIXELS_X = 800
SIZE_OF_CANVAS_IN_PIXELS_Y = 800


simulation_params = {
    "number_of_agents": UserSettableParameter(
        "slider",
        "Number of Players",
        50,     # default
        10,     # min
        200,    # max
        1,      # step
        description = " Choose how many players to include in the simulation",
    ),

    "width" : NUMBER_OF_CELLS,
    "height": NUMBER_OF_CELLS,
}

def agent_portrayal(agent):
    portrayal = {"Shape": "circle", "Filled": "true", "r": 0.5}

    if agent.wealth > 0:
        portrayal["Color"] = "green"
        portrayal["Layer"] = 0
    else:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    return portrayal


grid = CanvasGrid(agent_portrayal, NUMBER_OF_CELLS, NUMBER_OF_CELLS, SIZE_OF_CANVAS_IN_PIXELS_X, SIZE_OF_CANVAS_IN_PIXELS_Y)
server = ModularServer( MoneyModel, [grid], "Money Model", simulation_params)

# chart = ChartModule([{"Label": "Gini",
#                       "Color": "Black"}],
#                     data_collector_name='datacollector')

chart_current = ChartModule([{"Label" : "Wealthy agents", "Color" : "green"},
                             {"Label" : "Non wealthy agents", "Color" : "red"}],
                             canvas_height = 300,
                             data_collector_name = "datacollector")

server = ModularServer(MoneyModel,
                       [grid, chart_current],
                       "Money Model",
                       simulation_params)

server.port = 8521  # The default
server.launch()
