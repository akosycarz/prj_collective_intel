from enum import Enum, auto

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import numpy as np


@deserialize
@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.5
    separation_weight: float = 0.5

    delta_time: float = 3

    mass: int = 20

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


class Bird(Agent):
    config: FlockingConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.neighbours = []  # initialize neighbours
        self.velocity = Vector2(0, 0)  # initialize velocity
        self.position = Vector2(0, 0)  # initialize position
        self.max_velocity = 5.0 #set maximal velocity
  

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        #YOUR CODE HERE -----------

        #update neighbours
        self.update_neighbours()

        #wander if no neighbours
        if len(self.neighbours) == 0:
            self.velocity += self.wander()
            #.move and .pos

        else:
            alignment = self.compute_alignment() * self.config.alignment_weight
            separation = self.compute_separation() * self.config.separation_weight
            cohesion = self.compute_cohesion() * self.config.cohesion_weight

            #calculating the total force
            f_total = ((alignment + separation + cohesion) / self.config.mass)*self.config.delta_time

            # Adding force to movement
            self.move += f_total

            self.velocity += f_total
            if self.velocity.length() > self.config.movement_speed:
                self.velocity = (self.velocity / self.velocity.length()) * self.config.movement_speed
        # Update position, current position plus movement position value
        self.pos = self.pos + self.move 
        # Limiting to maximum velocity
        if self.move.length() > self.max_velocity:  # Using length() to get the velocity and compare to max_velocity
            self.move.normalize_ip()  # Normalizing move vector in-place to get vector length 1
            self.move.scale_to_length(self.max_velocity) # Scales vector to max_velocity value

        # Update position, current position plus movement position value
        self.pos = self.pos + self.move 


    def update_neighbours(self):
        self.neighbours = []
        for agent in self.in_proximity_accuracy():
            #add neighbours if not itself
            if agent[0] != self:
                self.neighbours.append(agent[0])


    def wander(self):
        return Vector2(np.random.uniform(-1,1), np.random.uniform(-1,1))

    def compute_alignment(self):
        # return type: Vector2
        return sum((bird.velocity for bird in self.neighbours), Vector2((0,0))) / len(self.neighbours) - self.velocity

    def compute_separation(self):
        return sum((self.position - bird.position for bird in self.neighbours), Vector2()) / len(self.neighbours)

    def compute_cohesion(self):
        average_position = sum((bird.position for bird in self.neighbours), Vector2()) / len(self.neighbours)
        cohesion_force =  average_position - self.position
        return cohesion_force - self.velocity
    


class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()


        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")


(
    # FlockingLive(
    #     FlockingConfig(
    #         image_rotation=True,
    #         movement_speed=2,
    #         radius=50,
    #         seed=1,
    #     )
    # )
    
    
    # .batch_spawn_agents(50, Bird, images=["images/bird.png"])

    Simulation(
        FlockingConfig(image_rotation=True,
            movement_speed=2,
            radius=50,
            seed=1)

    )
    .batch_spawn_agents(50, Bird, images=["images/bird.png"])

    
    .run()
    
)
