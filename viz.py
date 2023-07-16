from mesa.visualization.modules import CanvasGrid, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from model import MyModel
from agents import Players

class PlayerInfoElement(TextElement):
    def __init__(self):
        super().__init__()

    def render(self, model):
        players = [agent for agent in model.schedule.agents if isinstance(agent, Players)]
        # labels = [f"Player {player.unique_id}: Skill={player.skill}, Potential={player.potential}" for player in players]
        labels = [f"<span style='font-size: 12px;'>Player {player.unique_id}: Skill={player.skill}, Potential={player.potential}</span>" for player in players]
        return "<br>".join(labels)

def player_portrayal(agent):
    if isinstance(agent, Players):
        portrayal = {
            "Shape": "circle",
            "Color": "green",
            "Filled": "true",
            "Layer": 0,
            "r": 0.5
        }
        return portrayal

grid = CanvasGrid(player_portrayal, 10, 10, 500, 500)
info = PlayerInfoElement()

server = ModularServer(MyModel,
                       [grid, info],
                       "Player Visualization",
                       {"C": 3, "F": 5, "P": 20, "width": 10, "height": 10})

server.port = 8521  # Set the port for the server
server.launch()  # Launch the server
