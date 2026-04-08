# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
Smart Irrigation Environment Implementation.
"""

import random
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import IrrigationAction, IrrigationObservation
except ImportError:
    from models import IrrigationAction, IrrigationObservation


class IrrigationEnvironment(Environment):
    """
    Smart Irrigation Environment simulating 100 days of crop growth.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.day = 0
        self.soil_moisture = 0.5
        self.temperature = 25.0
        self.has_rained = False
        self.crop_health = 0.5  # Starting health

    def reset(self) -> IrrigationObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.day = 0
        self.soil_moisture = 0.5
        self.temperature = random.uniform(20.0, 35.0)
        self.has_rained = False
        self.crop_health = 0.5

        return IrrigationObservation(
            day=self.day,
            soil_moisture=self.soil_moisture,
            temperature=self.temperature,
            has_rained=self.has_rained,
            crop_health=self.crop_health,
            done=False,
            reward=0.0
        )

    def step(self, action: IrrigationAction) -> IrrigationObservation:  # type: ignore[override]
        self._state.step_count += 1
        self.day += 1

        # Apply action
        # 0: None, 1: Low, 2: Medium, 3: High
        # Let's say action gives: 1 -> +0.1, 2 -> +0.2, 3 -> +0.3
        water_amount = action.action * 0.1
        self.soil_moisture += water_amount

        # Simulate environmental evaporation based on temperature
        evaporation = (self.temperature - 20) * 0.01  # ranges roughly from 0 to 0.15 daily
        self.soil_moisture -= evaporation

        # Simulate rain (random 15% chance to rain)
        self.has_rained = random.random() < 0.15
        if self.has_rained:
            self.soil_moisture += 0.3

        # Clamp moisture between 0.0 and 1.0
        self.soil_moisture = max(0.0, min(1.0, self.soil_moisture))

        # Calculate reward
        reward = 0.0
        if 0.4 <= self.soil_moisture <= 0.7:
            reward += 0.5
        else:
            reward -= 0.5
            
        # Penalty for water waste: (water used * 0.5)
        # We define water_used as the raw action multiplier or water_amount.
        # Following exact instruction (water used * 0.5), we'll do water_amount * 0.5
        penalty = water_amount * 0.5
        reward -= penalty

        # Update crop health cumulatively over the 100 days
        # Perfect reward roughly +0.5 per day minus occasional water penalty
        # We need health to stay between 0 and 1.
        # Health drift: max perfect reward per day is 0.5, worst is -0.5
        health_delta = reward * 0.01  # Over 100 days, max change is ~ 0.5
        self.crop_health = max(0.0, min(1.0, self.crop_health + health_delta))

        # Check terminal state
        done = self.day >= 100

        return IrrigationObservation(
            day=self.day,
            soil_moisture=self.soil_moisture,
            temperature=self.temperature,
            has_rained=self.has_rained,
            crop_health=self.crop_health,
            done=done,
            reward=reward
        )

    @property
    def state(self) -> State:
        return self._state
