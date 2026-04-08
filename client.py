# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""Smart Irrigation Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from models import IrrigationAction, IrrigationObservation


class SmartIrrigationEnv(
    EnvClient[IrrigationAction, IrrigationObservation, State]
):
    """
    Client for the Smart Irrigation Environment.
    """

    def _step_payload(self, action: IrrigationAction) -> Dict:
        return {
            "action": action.action,
        }

    def _parse_result(self, payload: Dict) -> StepResult[IrrigationObservation]:
        obs_data = payload.get("observation", {})
        observation = IrrigationObservation(
            day=obs_data.get("day", 0),
            soil_moisture=obs_data.get("soil_moisture", 0.0),
            temperature=obs_data.get("temperature", 0.0),
            has_rained=obs_data.get("has_rained", False),
            crop_health=obs_data.get("crop_health", 0.0),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
