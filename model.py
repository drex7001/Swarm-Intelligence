# model.py
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random

class PersonAgent(Agent):
    def __init__(self, unique_id, model, shape):
        super().__init__(unique_id, model)
        self.shape = shape  # 'square' or 'circle'
        self.mood = 'neutral'  # 'neutral', 'angry', 'scared'
        self.news_influenced = False
        
    def step(self):
        # Move randomly
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        
        # Interact with neighbors
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)
        
        if neighbors:
            for neighbor in neighbors:
                # Conflict probability increases if different shapes meet
                if neighbor.shape != self.shape:
                    if random.random() < self.model.conflict_probability:
                        self.mood = 'angry'
                        neighbor.mood = 'scared'
                        self.model.media_focus = (self.shape, neighbor.shape)
                        return
                
        # Reset mood gradually
        if self.mood != 'neutral' and random.random() < 0.1:
            self.mood = 'neutral'

class MediaSimulation(Model):
    def __init__(self, N, width, height, conflict_probability=0.3):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.conflict_probability = conflict_probability
        self.media_focus = None
        
        # Create agents
        shapes = ['square', 'circle']
        for i in range(self.num_agents):
            shape = random.choice(shapes)
            agent = PersonAgent(i, self, shape)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
            
        self.datacollector = DataCollector(
            model_reporters={
                "Angry": lambda m: sum(1 for agent in m.schedule.agents if agent.mood == 'angry'),
                "Scared": lambda m: sum(1 for agent in m.schedule.agents if agent.mood == 'scared')
            }
        )
        
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()