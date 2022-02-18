# SGS: SEQUENTIAL GOAL SWITCHING

from abc import ABC
from xpag.goalsetters.goalsetter import GoalSetter
from xpag.tools.utils import debug, DataType, datatype_convert, hstack_func
import numpy as np


class SGS(GoalSetter, ABC):
    def __init__(self, params,
                 num_envs: int = 1,
                 datatype: DataType = DataType.TORCH,
                 device: str = 'cpu'):
        if params is None:
            params = {}
        super().__init__("SGS", params, num_envs, datatype, device)
        self.agent = self.params['agent']
        self.goal_sequence = []
        self.budget_sequence = []
        self.current_idxs = None
        self.current_budgets = None
        self.timesteps = np.zeros(self.num_envs).astype('int')

    def reset(self, obs):
        self.current_idxs = np.zeros(self.num_envs).astype('int')
        self.current_budgets = self.budget_sequence[self.current_idxs]
        self.timesteps = np.zeros(self.num_envs).astype('int')
        # obs["desired_goal"] =
        # obs['desired_goal'][:] = self.goal_sequence[0]
        obs['desired_goal'][:] = self.goal_sequence[self.current_idxs]
        return obs

    def step(self, o, action, new_o, reward, done, info):
        self.agent.value(hstack_func(o["observation"], o["desired_goal"]), action)
        # if info is not None:
        #     info["target"] = ""
        self.timesteps += 1
        # new_o["desired_goal"] =
        delta = datatype_convert(info['is_success'], DataType.NUMPY).astype('int')
        delta = np.maximum(delta, (self.timesteps > self.current_budgets).astype('int'))
        delta_max = delta.max()
        if delta_max:
            self.timesteps = self.timesteps * (1 - delta)
            self.current_idxs += delta
            self.current_idxs = self.current_idxs.clip(0, len(self.goal_sequence) - 1)
            self.current_budgets = self.budget_sequence[self.current_idxs]
            new_o['desired_goal'][:] = self.goal_sequence[self.current_idxs]
        return o, action, new_o, reward, done, info

    def write_config(self, output_file: str):
        pass

    def save(self, directory: str):
        pass

    def load(self, directory: str):
        pass

    def set_sequence(self, gseq, bseq):
        self.goal_sequence = np.array(gseq)
        self.goal_sequence = datatype_convert(self.goal_sequence,
                                              self.datatype,
                                              self.device)
        self.budget_sequence = np.array(bseq)
        self.budget_sequence = datatype_convert(self.budget_sequence,
                                                DataType.NUMPY,
                                                self.device)

        # for i in range(len(self.goal_sequence)):
        #     self.goal_sequence[i] = datatype_convert(self.goal_sequence[i],
        #                                              self.datatype,
        #                                              self.device)
        # self.budget_sequence = bseq
