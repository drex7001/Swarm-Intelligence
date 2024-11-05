import mesa
import random

class PersonAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = random.choice(['square', 'circle'])
        self.state = 'neutral'
        
    def step(self):
        # Ensure movement happens
        self.move()
        self.interact()
        
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        if possible_steps:  # Make sure there are available steps
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)
    
    def interact(self):
        # Get all neighbors in the current cell and adjacent cells
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False
        )
        
        # Interact with neighbors if there are any
        if neighbors:
            for neighbor in neighbors:
                if neighbor.type != self.type:  # Different types interact
                    # Increased probability of interaction
                    if random.random() < 0.5:  # 50% chance of interaction
                        self.state = 'angry'
                        neighbor.state = 'scared'
                        return
        
        # Cool down process - gradual return to neutral
        if self.state != 'neutral':
            if random.random() < 0.2:  # 20% chance to return to neutral
                self.state = 'neutral'

class MediaModel(mesa.Model):
    def __init__(self, N=50, width=20, height=20):
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True  # Ensure the model keeps running
        
        # Create and place agents
        for i in range(self.num_agents):
            agent = PersonAgent(i, self)
            # Place agents randomly on the grid
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
        
        # Data collector for the charts
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Angry": lambda m: sum(1 for a in m.schedule.agents if a.state == "angry"),
                "Scared": lambda m: sum(1 for a in m.schedule.agents if a.state == "scared"),
                "Neutral": lambda m: sum(1 for a in m.schedule.agents if a.state == "neutral")
            }
        )
    
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle" if agent.type == "circle" else "rect",
        "Filled": "true",
        "Layer": 0,
        "w": 0.9,  # Made agents slightly larger
        "h": 0.9,
        "r": 0.9,  # For circles
    }
    
    # More visible colors
    if agent.state == "neutral":
        portrayal["Color"] = "#808080"  # Medium grey
    elif agent.state == "angry":
        portrayal["Color"] = "#FF0000"  # Bright red
    else:  # scared
        portrayal["Color"] = "#0000FF"  # Bright blue
        
    return portrayal

# Create visualization elements
grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 
    20, 20,  # Grid size
    500, 500  # Pixel size
)

chart = mesa.visualization.ChartModule(
    [
        {"Label": "Angry", "Color": "Red"},
        {"Label": "Scared", "Color": "Blue"},
        {"Label": "Neutral", "Color": "Grey"}
    ],
    data_collector_name='datacollector'
)

# Create and launch the server
model_params = {
    "N": mesa.visualization.Slider(
        "Number of agents",
        50,  # default
        10,  # min
        100,  # max
        1    # step
    ),
    "width": 20,
    "height": 20
}

server = mesa.visualization.ModularServer(
    MediaModel,
    [grid, chart],
    "Media Influence Model",
    model_params
)

server.port = 8521
if __name__ == "__main__":
    server.launch()