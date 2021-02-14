from random import random
from gym import Env
import gym
from gym.envs.classic_control import *

class SarsaLambdaAgent(object):
    def __init__(self, env: Env):
        self.env = env
        self.Q = {}  # {s0:[,,,,,,],s1:[]} 数组内元素个数为行为空间大小
        self.E = {}  # Eligibility Trace 
        self.state = None
        self._init_agent()
        return

    def _init_agent(self):
        self.state = self.env.reset()  # agent回到起点位置
        s_name = self._name_state(self.state)
        self._assert_state_in_QE(s_name, randomized = False)

    # using simple decaying epsilon greedy exploration
    def _curPolicy(self, s, num_episode, use_epsilon):
        epsilon = 1.00 / (num_episode + 1) # 衰减的epsilon-greedy
        Q_s = self.Q[s]
        rand_value = random()
        if use_epsilon and rand_value < epsilon:  
            return self.env.action_space.sample()
        else:
            return int(max(Q_s, key=Q_s.get))

    # Agent依据当前策略和状态生成下一步与环境交互所要执行的动作
    # 该方法并不执行生成的行为
    def performPolicy(self, s, num_episode, use_epsilon=True):
        return self._curPolicy(s, num_episode, use_epsilon)

    def act(self, a): # Agent执行动作a
        return self.env.step(a)

    def learning(self, lambda_, gamma, alpha, max_episode_num):
        total_time = 0
        time_in_episode = 0
        num_episode = 1
        while num_episode <= max_episode_num:
            self._resetEValue()  # 将所有E(s, a)重新置0
            s0 = self._name_state(self.env.reset())
            a0 = self.performPolicy(s0, num_episode)
            #self.env.render()

            time_in_episode = 0
            is_done = False
            while not is_done:
                s1, r1, is_done, info = self.act(a0)
                #self.env.render()
                s1 = self._name_state(s1)
                self._assert_state_in_QE(s1, randomized = True)

                a1= self.performPolicy(s1, num_episode)

                q = self._get_(self.Q, s0, a0)
                q_prime = self._get_(self.Q, s1, a1)
                delta = r1 + gamma * q_prime - q

                e = self._get_(self.E, s0,a0)
                e = e + 1
                self._set_(self.E, s0, a0, e) # set E before update E

                # 更新所有(state, action)对
                state_action_list = list(zip(self.E.keys(),self.E.values()))
                for s, a_es in state_action_list:  # s是状态名，a_es是当前状态下 行为名：行为价值  组成的list
                    for a in range(self.env.action_space.n):
                        e_value = a_es[a]
                        old_q = self._get_(self.Q, s, a)
                        new_q = old_q + alpha * delta * e_value
                        new_e = gamma * lambda_ * e_value
                        self._set_(self.Q, s, a, new_q)
                        self._set_(self.E, s, a, new_e)

                if num_episode == max_episode_num:
                    print("t:{0:>2}: s:{1}, a:{2:10}, s1:{3}".
                          format(time_in_episode, s0, a0, s1))

                s0, a0 = s1, a1
                time_in_episode += 1

            print("Episode {0} takes {1} steps.".format(
                num_episode, time_in_episode))
            total_time += time_in_episode
            num_episode += 1
        return

    def _is_state_in_Q(self, s):
        return self.Q.get(s) is not None

    def _init_state_value(self, s_name, randomized = True):
        if not self._is_state_in_Q(s_name):
            self.Q[s_name], self.E[s_name] = {},{}
            for action in range(self.env.action_space.n):
                default_v = random() / 10 if randomized is True else 0.0
                self.Q[s_name][action] = default_v
                self.E[s_name][action] = 0.0

    def _assert_state_in_QE(self, s, randomized=True):
        if not self._is_state_in_Q(s):
            self._init_state_value(s, randomized)

    def _name_state(self, state): 
        '''给个体的一个观测(状态）生成一个不重复的字符串作为Q、E字典里的键
        '''
        return str(state)               

    def _get_(self, QorE, s, a):
        self._assert_state_in_QE(s, randomized=True)
        return QorE[s][a]

    def _set_(self, QorE, s, a, value):
        self._assert_state_in_QE(s, randomized=True)
        QorE[s][a] = value

    def _resetEValue(self):
        for value_dic in self.E.values():
            for action in range(self.env.action_space.n):
                value_dic[action] = 0.00

def main():
    # id = "Reacher-v2" # 设置环境id
    # env = gym.make(id) # 构建环境对象
    env = WindyGridWorld()
    
    # directory = ""
    # env = gym.wrappers.Monitor(env, directory, force=True)
    agent = SarsaLambdaAgent(env)
    env.reset()
    print("Learning...")  
    agent.learning(lambda_ = 0.01,
                   gamma = 0.9, 
                   alpha = 0.1, 
                   max_episode_num = 1000)

if __name__ == "__main__":
    main() 
