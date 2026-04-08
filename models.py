# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Smart Irrigation Environment.
"""

from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class IrrigationAction(Action):
    """
    Action for the Smart Irrigation environment.
    0: None, 1: Low, 2: Medium, 3: High
    """
    action: int = Field(default=0, description="Amount of water to apply: 0=None, 1=Low, 2=Medium, 3=High")


class IrrigationObservation(Observation):
    """Observation from the Smart Irrigation environment."""
    
    day: int = Field(default=0, description="Current day in the simulation (0-100)")
    soil_moisture: float = Field(default=0.5, description="Soil moisture level (0.0 to 1.0)")
    temperature: float = Field(default=25.0, description="Ambient temperature in Celsius (20-35)")
    has_rained: bool = Field(default=False, description="Whether it rained on the current day")
    crop_health: float = Field(default=0.5, description="Current health of the crop (0.0 to 1.0)")
