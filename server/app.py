# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
FastAPI application for the Smart Irrigation Environment.
"""

from fastapi import FastAPI
try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with '\n    uv sync\n'"
    ) from e

try:
    from ..models import IrrigationAction, IrrigationObservation
    from .irrigation_env import IrrigationEnvironment
except (ModuleNotFoundError, ImportError):
    from models import IrrigationAction, IrrigationObservation
    from server.irrigation_env import IrrigationEnvironment

# Create the app with web interface and README integration
app = create_app(
    IrrigationEnvironment,
    IrrigationAction,
    IrrigationObservation,
    env_name="smart_irrigation",
    max_concurrent_envs=10, 
)

@app.get("/tasks")
async def get_tasks():
    """Return the three exact task IDs required by the evaluator."""
    return ["baseline-growth", "drought-resistance", "monsoon-management"]

@app.get("/scale_score")
async def scale_score(health: float):
    """
    Implements the 0.05-0.95 scaling math. 
    Returns linearly scaled performance_score (or security_score) based on crop_health.
    """
    health = max(0.0, min(1.0, health))
    scaled_score = 0.05 + (0.90 * health)
    return {"security_score": scaled_score, "performance_score": scaled_score}

def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(port=args.port)
