import gym
from gym import spaces
import numpy as np
import pandas as pd
import subprocess
from abc import ABC
gym.logger.set_level(40)

class PPOEnv(gym.Env, ABC):
    def __init__(self):
        self.action_space = spaces.Box(low=np.asarray([-1 for _ in range(2)]),
                                       high=np.asarray([1 for _ in range(2)]),
                                       shape=(2,),
                                       dtype=np.float32)

        high = np.asarray([1 for _ in range(136)], dtype=np.float32)
        low = np.asarray([-1 for _ in range(136)], dtype=np.float32)
        self.observation_space = spaces.Box(low=low,
                                            high=high,
                                            dtype=np.float32)
        # Perfect l1 = 25.31, l2 = 30.91
        self.config = {
            'reward': 0,
            'parameter': {
                'l1': {
                    'default': 22.31,
                    'range': [20, 30],
                    'delta': 0
                },
                'l2': {
                    'default': 27.91,
                    'range': [25, 35],
                    'delta': 0
                }
            },
            'max_step': 100,
            'goal_reward': 18,
        }

        self.assembly_path = r'C:\Users\Lenovo Legion\PycharmProjects\pythonProject3\AnsysEM21.1\Win64'
        self.application = "Ansoft.ElectronicsDesktop.2021.1"
        self.project = "4thOrderChebyshev"
        self.golden_sparam_path = r'C:/Users/Lenovo Legion/PycharmProjects/pythonProject3/S Parameter IdealPlot.csv'
        self.actual_sparam_path = r'C:/Users/Lenovo Legion/PycharmProjects/pythonProject3/S Parameter Plot 1.csv'
        self.ironpython_path = "C:/Program Files/IronPython 2.7/ipy.exe"
        self.integration_path = "C:/Users/Lenovo Legion/PycharmProjects/pythonProject/AnsysEM/AnsysEM21.1/Win64/PythonFiles/DesktopPlugin/integration.py"
        self.rewardfile_path = "C:/Users/Lenovo Legion/PycharmProjects/pythonProject3/rewardfile.txt"
        self.golden_sparam_df = pd.read_csv(self.golden_sparam_path)
        self.actual_sparam_df = None
        self.golden_sparam_df.columns = ['freq', 's11', 's21']
        self.rewardlist = []
        self.totalreward_per_episode = 0
        self.current_step = 0
        self.reset_counter = 0
        self.is_achieved = False
        self.states = []

    def write_integration(self):
        statement = 'import sys\n'
        statement += 'import ScriptEnv\n'
        statement += 'import clr\n'
        statement += 'import warnings\n\n'
        statement += 'warnings.filterwarnings(action="ignore")\n'

        statement += 'sys.path.append("' + self.assembly_path + '")\n'
        statement += 'ScriptEnv.Initialize("' + self.application + '")\n'
        statement += 'oProject = oDesktop.SetActiveProject("' + self.project + '")\n'
        statement += 'oDesign = oProject.SetActiveDesign("HFSSDesign1")\n'

        for param_name in self.config['parameter']:
            param_value = str(self.config['parameter'][param_name]['default']) + ' + ' + str(
                self.config['parameter'][param_name]['delta'])
            statement += PPOEnv.edit_parameter_integration(parameter_name=param_name, parameter_value=param_value)

        statement += 'oProject.Save()\n'
        statement += 'oDesign.AnalyzeAll()\n'
        statement += 'oModule = oDesign.GetModule("ReportSetup")\n'
        statement += 'oModule.ExportToFile("S Parameter Plot 1", "' + self.actual_sparam_path + '", False)'
        with open(self.integration_path, 'w') as fp:
            fp.writelines(statement)

    @staticmethod
    def edit_parameter_integration(parameter_name, parameter_value):
        statement = 'oDesign.ChangeProperty(\n'
        statement += '    [\n'
        statement += '        "NAME:AllTabs",\n'
        statement += '        [\n'
        statement += '            "NAME:LocalVariableTab",\n'
        statement += '            [\n'
        statement += '                "NAME:PropServers",\n'
        statement += '                "LocalVariables"\n'
        statement += '            ],\n'
        statement += '            [\n'
        statement += '                "NAME:ChangedProps",\n'
        statement += '                [\n'
        statement += '                    "NAME:' + parameter_name + '",\n'
        statement += '					"Value:="		, "(' + parameter_value + ') mm"\n'
        statement += '                ]\n'
        statement += '            ]\n'
        statement += '        ]\n'
        statement += '    ])\n'

        return statement

    def run_integration(self):
        subprocess.run([self.ironpython_path, self.integration_path])

    def construct_states(self):
        """
            Choose 134 datapoints for evaluation
            Compute distances for predicted and ideal result comparison
            Return states
        """
        divider = int(len(self.golden_sparam_df)/101)
        golden_df = self.golden_sparam_df.iloc[::divider, :]
        golden_list = golden_df['s11'].values
        self.actual_sparam_df = pd.read_csv(self.actual_sparam_path)
        self.actual_sparam_df.columns = ['freq', 's11', 's21']
        actual_df = self.actual_sparam_df.iloc[::divider, :]
        actual_list = actual_df['s11'].values
        states = []

        for i, marker in enumerate(actual_list):
            if marker:
                upper = 1.2
                lower = 0.8
                marker = abs(marker)
                golden_list[i] = abs(golden_list[i])

                if golden_list[i] * lower <= marker <= golden_list[i] * upper:
                    states.append(0)
                elif marker < golden_list[i] * lower:
                    if marker <= golden_list[i] * 0.1:
                        states.append(-1)
                    else:
                        states.append(-(1 - ((marker - (golden_list[i] * 0.1)) / ((golden_list[i] * lower) - (
                                golden_list[i] * 0.1)))))
                else:
                    if marker >= golden_list[i] * 2:
                        states.append(1)
                    else:
                        states.append(1 - (((golden_list[i] * 2) - marker) / (
                                (golden_list[i] * 2) - (golden_list[i] * upper))))

        for para_name in self.config['parameter']:
            min_val = self.config['parameter'][para_name]['range'][0]
            max_val = self.config['parameter'][para_name]['range'][1]
            cur_val = self.config['parameter'][para_name]['default']+self.config['parameter'][para_name]['delta']

            if min_val < cur_val < max_val:
                states.append(0)
            elif cur_val <= min_val:
                states.append(-1)
            else:
                states.append(1)

        return states

    def _is_terminal(self, reward) -> bool:
        """The episode is over if the oversteps or the goal is reached."""
        is_max_steps = self.current_step >= self.config["max_step"]
        success = reward > -self.config['goal_reward']
        return is_max_steps or success

    def step(self, action):
        """
            Perform step in environment, agent give action, then tune the parameter, then run the hfss file
            Get a series of states / observation after the evaluation of s-parameters
            Reward based on the constructed states
            Return states/observation, reward, done, info
        """

        # Update Delta
        for i, param_name in enumerate(self.config['parameter']):
            default = self.config['parameter'][param_name]['default']
            delta = self.config['parameter'][param_name]['delta']
            minimum = self.config['parameter'][param_name]['range'][0]
            maximum = self.config['parameter'][param_name]['range'][1]
            #update = float(action[i]) * ((minimum + maximum) / 2)
            update = float(action[i])
            new_value = default + delta + update
            clip_value = max(min(new_value, maximum), minimum)
            new_delta = clip_value - default
            self.config['parameter'][param_name]['delta'] = new_delta

        # Update integration script
        self.write_integration()

        # Run integration script
        self.run_integration()
        # Increase current step
        self.current_step +=1

        # Construct states
        states = np.asarray(self.construct_states(), dtype=np.float32)
        self.states = states

        # Compute Reward
        reward = -sum(np.absolute(states))

        # Write reward to a file after each step
        with open(self.rewardfile_path, 'a') as fp:
            fp.writelines(str(reward) + "\n")
            fp.close()
        self.totalreward_per_episode += reward

        # Set terminating conditions
        done = bool(self._is_terminal(reward))
        info = {}

        # Inspect achieve status in current episode (in Boolean)
        self.is_achieved = reward > -self.config['goal_reward'] and self.current_step <= self.config['max_step']

        # Inspect reward
        print("Step:", self.current_step, ", Reward:", reward)
        return states, reward, done, info

    def reset(self):
        """
            Reset environment by assigning initial states
            Return states / observation
        """
        if self.reset_counter != 0:
            self.rewardlist.append(self.totalreward_per_episode)

        with open(self.rewardfile_path, 'a+') as fp:
            fp.writelines("Episode "+str(self.reset_counter) + "\n")

        end_value = [(self.config['parameter'][param_name]['default'] + self.config['parameter'][param_name]['delta']) for param_name in self.config['parameter']]
        print('Reset:', self.reset_counter, ', Achieved: {} | End: {} | State: {} | GoalRew: {} | Steps : {}'.format(
            self.is_achieved, end_value, self.states, -self.config['goal_reward'], self.current_step))

        for param_name in self.config['parameter']:
            self.config['parameter'][param_name]['delta'] = 0

        self.current_step = 0
        self.totalreward_per_episode = 0
        self.write_integration()
        self.run_integration()
        states = np.asarray(self.construct_states(), dtype=np.float32)
        self.reset_counter += 1
        return states


if __name__ == '__main__':
    hfss = PPOEnv()
    hfss.step([1, 1])
