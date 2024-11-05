import mesa
import random
import math

class PersonAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = 'Person'  # Base type
        self.emotion = 0  # Neutral emotion on a scale from -1 to 1
        self.influence_factor = 1.0  # Base influence factor
        self.resistance_level = 0.0  # Base resistance
        self.media_susceptibility = 1.0  # Base media susceptibility
        self.memory = []  # Memory of past emotions
        self.memory_capacity = 5  # How many past emotions to remember
        self.tolerance_threshold = random.uniform(0, 1)  # Individual tolerance
        self.reactivity = 1.0  # How reactive the agent is
        self.fatigue_rate = self.model.fatigue_rate  # Fatigue rate from model

    def step(self):
        self.move()
        self.interact()
        self.update_memory()
        self.cool_down()  # Implement fatigue

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        if possible_steps:  # Make sure there are available steps
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def interact(self):
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False
        )
        if neighbors:
            # Compute average emotion of neighbors
            avg_emotion = sum([neighbor.emotion for neighbor in neighbors]) / len(neighbors)
            emotion_difference = avg_emotion - self.emotion
            if abs(emotion_difference) > self.tolerance_threshold:
                self.emotion += emotion_difference * self.influence_factor * self.reactivity
                # Apply resistance level
                self.emotion -= self.emotion * self.resistance_level
                # Keep emotion within bounds
                self.emotion = max(-1, min(1, self.emotion))

    def update_memory(self):
        self.memory.append(self.emotion)
        if len(self.memory) > self.memory_capacity:
            self.memory.pop(0)

    def cool_down(self):
        # Fatigue reduces reactivity over time
        self.reactivity *= self.fatigue_rate
        if self.reactivity < 0.1:
            self.reactivity = 0.1  # Minimum reactivity

    def receive_media_influence(self, media_emotion):
        self.emotion += media_emotion * self.media_susceptibility
        self.emotion = max(-1, min(1, self.emotion))

class PassiveObserver(PersonAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = 'PassiveObserver'
        self.influence_factor = 0.5  # Less influence on others
        self.media_susceptibility = 0.5  # Less susceptible to media

    def interact(self):
        super().interact()
        # Passive observers absorb emotions but have less influence

class Influencer(PersonAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = 'Influencer'
        self.influence_factor = 1.5  # Greater influence on others
        self.media_susceptibility = 1.5  # More susceptible to media

    def interact(self):
        super().interact()
        # Influencers have greater impact on neighbors

class Resistor(PersonAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = 'Resistor'
        self.resistance_level = 0.7  # High resistance to change
        self.media_susceptibility = 0.5  # Less susceptible to media

    def interact(self):
        super().interact()
        # Resistors resist changes in emotion

class MediaAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.memory = []  # Memory of captured high-impact emotions

    def step(self):
        self.capture_events()
        self.broadcast()

    def capture_events(self):
        # Detect high-impact events (e.g., agents with extreme emotions)
        high_impact_agents = [agent for agent in self.model.schedule.agents if isinstance(agent, PersonAgent) and abs(agent.emotion) > 0.8]
        if high_impact_agents:
            selected_agent = self.random.choice(high_impact_agents)
            # Capture and amplify the emotion
            captured_emotion = selected_agent.emotion * self.model.media_amplification_factor
            self.memory.append(captured_emotion)
            if len(self.memory) > 5:
                self.memory.pop(0)

    def broadcast(self):
        if self.memory:
            # Influence the population based on the most recent captured emotion
            media_emotion = self.memory[-1]
            for agent in self.model.schedule.agents:
                if isinstance(agent, PersonAgent):
                    agent.receive_media_influence(media_emotion)

class MediaModel(mesa.Model):
    def __init__(self, N=50, width=20, height=20, density=0.8, media_amplification_factor=1.0, fatigue_rate=0.99):
        self.num_agents = int(N * density)
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True

        self.media_amplification_factor = media_amplification_factor
        self.fatigue_rate = fatigue_rate

        # Create agents
        for i in range(self.num_agents):
            agent_type = self.random.choices(
                [PassiveObserver, Influencer, Resistor, PersonAgent],
                weights=[0.3, 0.1, 0.1, 0.5]
            )[0]
            agent = agent_type(i, self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)

        # Add Media Agent
        media_agent = MediaAgent(self.num_agents + 1, self)
        self.schedule.add(media_agent)

        # Data collector
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Emotion Diversity": self.compute_emotion_diversity,
                "Average Emotion": self.compute_average_emotion,
                "Influencer Impact": self.compute_influencer_impact,
                "Positive Emotion": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, PersonAgent) and a.emotion > 0),
                "Negative Emotion": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, PersonAgent) and a.emotion < 0),
                "Neutral Emotion": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, PersonAgent) and a.emotion == 0),
            }
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

    def compute_emotion_diversity(self):
        emotions = [agent.emotion for agent in self.schedule.agents if isinstance(agent, PersonAgent)]
        rounded_emotions = [round(e * 10) / 10 for e in emotions]  # Round to 1 decimal place
        unique_emotions = set(rounded_emotions)
        diversity = len(unique_emotions) / 20  # Assuming 20 possible emotion levels
        return diversity

    def compute_average_emotion(self):
        emotions = [agent.emotion for agent in self.schedule.agents if isinstance(agent, PersonAgent)]
        if emotions:
            avg_emotion = sum(emotions) / len(emotions)
            return avg_emotion
        else:
            return 0

    def compute_influencer_impact(self):
        influencers = [agent for agent in self.schedule.agents if isinstance(agent, Influencer)]
        if not influencers:
            return 0
        influence = sum([agent.emotion for agent in influencers]) / len(influencers)
        return influence

def agent_portrayal(agent):
    portrayal = {
        "Filled": "true",
        "Layer": 0,
    }

    # Shape based on agent type
    if isinstance(agent, Influencer):
        portrayal["Shape"] = "star"
        portrayal["Color"] = "Gold"
        portrayal["r"] = 0.8
    elif isinstance(agent, Resistor):
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "DarkGrey"
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
    elif isinstance(agent, PassiveObserver):
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "LightBlue"
        portrayal["r"] = 0.5
    elif isinstance(agent, PersonAgent):
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "Grey"
        portrayal["r"] = 0.6
    elif isinstance(agent, MediaAgent):
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "Black"
        portrayal["w"] = 1.0
        portrayal["h"] = 1.0
        portrayal["Layer"] = 1
        return portrayal  # Media agent does not need to show emotion

    # Color intensity based on emotion
    if isinstance(agent, PersonAgent):
        red = int(max(0, -agent.emotion) * 255)
        green = int(max(0, agent.emotion) * 255)
        blue = 0
        portrayal["Color"] = f"rgb({red}, {green}, {blue})"

    return portrayal

# Create visualization elements
grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 
    20, 20,  # Grid size
    500, 500  # Pixel size
)

chart = mesa.visualization.ChartModule(
    [
        {"Label": "Positive Emotion", "Color": "Green"},
        {"Label": "Negative Emotion", "Color": "Red"},
        {"Label": "Neutral Emotion", "Color": "Grey"},
        {"Label": "Emotion Diversity", "Color": "Black"},
        {"Label": "Average Emotion", "Color": "Blue"},
        {"Label": "Influencer Impact", "Color": "Gold"},
    ],
    data_collector_name='datacollector'
)

# Create and launch the server
model_params = {
    "N": mesa.visualization.Slider(
        "Number of agents",
        50,  # default
        10,  # min
        200,  # max
        10    # step
    ),
    "density": mesa.visualization.Slider(
        "Density",
        0.8,  # default
        0.1,  # min
        1.0,  # max
        0.1   # step
    ),
    "media_amplification_factor": mesa.visualization.Slider(
        "Media Amplification Factor",
        1.0,  # default
        0.5,  # min
        2.0,  # max
        0.1   # step
    ),
    "fatigue_rate": mesa.visualization.Slider(
        "Fatigue Rate",
        0.99,  # default
        0.8,  # min
        1.0,  # max
        0.005   # step
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
