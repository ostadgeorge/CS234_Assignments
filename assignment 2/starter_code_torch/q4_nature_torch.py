import torch
import torch.nn as nn
import torch.nn.functional as F

from utils.general import get_logger
from utils.test_env import EnvTest
from q2_schedule import LinearExploration, LinearSchedule
from q3_linear_torch import Linear


from configs.q4_nature import config


class DeepQNetwork(nn.Module):

    def __init__(self, num_actions):
        super(DeepQNetwork, self).__init__()
        self.conv1 = nn.Conv2d(24, 32, 8, 4)
        self.conv2 = nn.Conv2d(32, 64, 4, 2)
        self.conv3 = nn.Conv2d(64, 64, 3, 1)
        # self.fc1 = nn.Linear()
        # Init with cuda if available
        if torch.cuda.is_available():
            self.cuda()
        self.apply(self.weights_init)

    def forward(self, x):
        x = self.conv1(x)
        print("\n\n\n\n")
        print(x.size(), flush=True)
        x = self.conv2(x)
        x = self.conv3(x)
        # print("\n\n\n\n")
        # print(x.size(), flush=True)
        x = x.view(x.size(0), -1)
        x = self.hidden(x)
        x = self.out(x)
        return x

    @staticmethod
    def weights_init(m):
        classname = m.__class__.__name__
        if classname.find('Conv') != -1:
            # pass
            m.weight.data.normal_(0.0, 0.02)
            # nn.init.xavier_uniform(m.weight)
        if classname.find('Linear') != -1:
            pass
            # m.weight.data.normal_(0.0, 0.02)
            # m.weight.data.fill_(1)
            # nn.init.xavier_uniform(m.weight)
            # m.weight.data.normal_(0.0, 0.008)



class NatureQN(Linear):
    """
    Implementing DeepMind's Nature paper. Here are the relevant urls.
    https://storage.googleapis.com/deepmind-data/assets/papers/DeepMindNature14236Paper.pdf

    Model configuration can be found in the Methods section of the above paper.
    """

    def initialize_models(self):
        """Creates the 2 separate networks (Q network and Target network). The input
        to these models will be an img_height * img_width image
        with channels = n_channels * self.config.state_history

        1. Set self.q_network to be a model with num_actions as the output size
        2. Set self.target_network to be the same configuration self.q_network but initialized from scratch
        3. What is the input size of the model?

        To simplify, we specify the paddings as:
            (stride - 1) * img_height - stride + filter_size) // 2

        Hints:
            1. Simply setting self.target_network = self.q_network is incorrect.
            2. The following functions might be useful
                - nn.Sequential
                - nn.Conv2d
                - nn.ReLU
                - nn.Flatten
                - nn.Linear
        """
        state_shape = list(self.env.observation_space.shape)
        img_height, img_width, n_channels = state_shape
        num_actions = self.env.action_space.n

        ##############################################################
        ################ YOUR CODE HERE - 25-30 lines lines ################

        self.q_network = DeepQNetwork(num_actions)
        self.target_network = DeepQNetwork(num_actions)

        ##############################################################
        ######################## END YOUR CODE #######################

    def get_q_values(self, state, network):
        """
        Returns Q values for all actions

        Args:
            state: (torch tensor)
                shape = (batch_size, img height, img width, nchannels x config.state_history)
            network: (str)
                The name of the network, either "q_network" or "target_network"

        Returns:
            out: (torch tensor) of shape = (batch_size, num_actions)

        Hint:
            1. What are the input shapes to the network as compared to the "state" argument?
            2. You can forward a tensor through a network by simply calling it (i.e. network(tensor))
        """
        out = None

        ##############################################################
        ################ YOUR CODE HERE - 4-5 lines lines ################

        state.transpose_(1, 3)
        print("\n\n")
        print(state.size())
        print("\n\n")

        if network == "q_network":
            out = self.q_network(state)
        else:
            out = self.target_network(state)

        ##############################################################
        ######################## END YOUR CODE #######################
        return out


"""
Use deep Q network for test environment.
"""
if __name__ == '__main__':
    env = EnvTest((8, 8, 6))

    # exploration strategy
    exp_schedule = LinearExploration(env, config.eps_begin,
            config.eps_end, config.eps_nsteps)

    # learning rate schedule
    lr_schedule  = LinearSchedule(config.lr_begin, config.lr_end,
            config.lr_nsteps)

    # train model
    model = NatureQN(env, config)
    model.run(exp_schedule, lr_schedule)
