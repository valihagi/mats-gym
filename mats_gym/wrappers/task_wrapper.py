from __future__ import annotations

from typing import Any

from mats_gym.envs.scenario_env_wrapper import BaseScenarioEnvWrapper
from mats_gym.tasks import Task


class TaskWrapper(BaseScenarioEnvWrapper):
    """
    A wrapper that adds tasks to the environment.
    """

    def __init__(
        self,
        env: BaseScenarioEnvWrapper,
        tasks: dict[str, Task],
        terminate_on_any: bool = False,
        ignore_wrapped_env_reward: bool = False,
        ignore_wrapped_env_termination: bool = False,
    ):
        """
        @param env: The environment to wrap.
        @param tasks: A dictionary mapping agent names to tasks.
        @param terminate_on_any: Whether to terminate the episode if any of the tasks is terminated.
        @param ignore_wrapped_env_reward: Whether to ignore the reward of the wrapped environment.
        @param ignore_wrapped_env_termination: Whether to ignore the termination signal of the wrapped environment.
        """
        super().__init__(env)
        self._tasks = tasks
        self._terminate_on_any = terminate_on_any
        self._ignore_wrapped_env_reward = ignore_wrapped_env_reward
        self._ignore_wrapped_env_termination = ignore_wrapped_env_termination

    def step(
        self, actions: dict
    ) -> tuple[
        dict, dict[Any, float], dict[Any, bool], dict[Any, bool], dict[Any, dict]
    ]:
        obs, reward, terminated, truncated, info = self.env.step(actions)
        for agent in actions:
            if agent not in self._tasks:
                continue
            task = self._tasks[agent]
            task_reward = task.reward(obs, actions, info)
            task_termination = task.terminated(obs, actions, info)
            if self._ignore_wrapped_env_reward:
                reward[agent] = task_reward
            else:
                reward[agent] += task_reward

            if self._ignore_wrapped_env_termination:
                terminated[agent] = task_termination
            else:
                terminated[agent] = task_termination or terminated[agent]

        return obs, reward, terminated, truncated, info

    def reset(
        self, seed: int | None = None, options: dict | None = None
    ) -> tuple[dict, dict[Any, dict]]:
        result = super().reset(seed, options)
        for task in self._tasks.values():
            task.reset()
        return result