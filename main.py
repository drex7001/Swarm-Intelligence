from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

class PersonAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state = "neutral"
        self.shape = "circle"
        self.color = "grey"

    def step(self):
        self.move()
        self.interact()

    def move(self):
        # Move to a random neighboring cell
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def interact(self):
        # Interact with neighbors
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            for other in cellmates:
                if other != self:
                    if other.state == "angry" and self.state != "angry":
                        self.state = "angry"
                        self.shape = "triangle"
                        self.color = "red"
                    elif other.state == "happy" and self.state != "happy":
                        self.state = "happy"
                        self.shape = "square"
                        self.color = "green"

class WBWWBModel(Model):
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.running = True

        # Create agents
        for i in range(self.num_agents):
            a = PersonAgent(i, self)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.media_counter = 0

    def step(self):
        self.schedule.step()
        self.media_influence()

    def media_influence(self):
        # Media highlights an angry interaction every 5 steps
        if self.media_counter % 5 == 0:
            agent = self.random.choice(self.schedule.agents)
            agent.state = "angry"
            agent.shape = "triangle"
            agent.color = "red"
        self.media_counter += 1

def agent_portrayal(agent):
    portrayal = {
        "Shape": agent.shape,
        "Color": agent.color,
        "Filled": "true",
        "Layer": 0,
        "r": 0.5
    }
    return portrayal

grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

server = ModularServer(WBWWBModel,
                       [grid],
                       "We Become What We Behold Model",
                       {"N": 100, "width": 20, "height": 20})

if __name__ == "__main__":
    server.launch()
