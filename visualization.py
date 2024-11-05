from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer

def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle" if agent.shape == "circle" else "rect",
        "w": 0.8,
        "h": 0.8,
        "Filled": "true",
        "Layer": 0
    }
    
    if agent.mood == 'neutral':
        portrayal["Color"] = "grey"
    elif agent.mood == 'angry':
        portrayal["Color"] = "red"
    else:  # scared
        portrayal["Color"] = "blue"
        
    return portrayal