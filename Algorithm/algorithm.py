import os
import random
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import pyplot as plt

from Environment.environment import APIFuzzyTestingEnvironment


class QLearningAgent:
    def __init__(self, env: APIFuzzyTestingEnvironment, mutation_methods, max_steps_per_episode, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1, min_exploration_rate=0.1, max_exploration_rate=1, exploration_decay_rate=0.01):
        self.env = env
        self.int_q_table = np.zeros([env.observation_space.n, len(mutation_methods[0])])
        self.float_q_table = np.zeros([env.observation_space.n, len(mutation_methods[1])])
        self.bool_q_table = np.zeros([env.observation_space.n, len(mutation_methods[2])])
        self.byte_q_table = np.zeros([env.observation_space.n, len(mutation_methods[3])])
        self.string_q_table = np.zeros([env.observation_space.n, len(mutation_methods[4])])
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.min_exploration_rate = min_exploration_rate
        self.max_exploration_rate = max_exploration_rate
        self.exploration_decay_rate = exploration_decay_rate
        self.max_steps_per_episode = max_steps_per_episode
        self.episode_rewards = []  # To store the rewards obtained in each episode
        self.rewards_all_episodes=[]
        self.mutation_methods = mutation_methods
        self.mutation_counts = {i: {method: 0 for method in mutation_methods[i]} for i in range(env.observation_space.n)}
        self.mutation_rewards = {i: {method: [] for method in mutation_methods[i]} for i in range(env.observation_space.n)}
        self.state_visits = np.zeros(env.observation_space.n)
        self.q_value_convergence = {}
        self.num_episodes = 30

    def choose_action(self, state, int_q_table, float_q_table, bool_q_table, byte_q_table, string_q_table):
        # Epsilon-greedy exploration policy
        if random.uniform(0, 1) < self.exploration_rate:
            action = self.env.action_space.sample()
        else:
            action = []
            action.append(np.argmax(int_q_table[state,:]))
            action.append(np.argmax(float_q_table[state,:]))
            action.append(np.argmax(bool_q_table[state,:]))
            action.append(np.argmax(byte_q_table[state,:]))
            action.append(np.argmax(string_q_table[state,:]))
        return action

    def update_q_table(self, state, action, reward, new_state, q_table):
        q_table[state, action] = q_table[state, action] * (1 - self.learning_rate) + \
            self.learning_rate * (reward + self.discount_factor * np.max(q_table[new_state, :]))

    def train(self, num_episodes):
        self.q_value_convergence = {
            'int': [],
            'float': [],
            'bool': [],
            'byte': [],
            'string': []
        }

        self.num_episodes = num_episodes

        for episode in range(num_episodes):
            done = False
            state = self.env.reset()
            rewards_current_episode = 0

            print(episode)

            for step in range(self.max_steps_per_episode):
                action = self.choose_action(state, self.int_q_table, self.float_q_table, self.bool_q_table, self.byte_q_table, self.string_q_table)
                new_state, reward, done = self.env.step(action)
                self.update_q_table(state, action[0], reward, new_state, self.int_q_table)
                self.update_q_table(state, action[1], reward, new_state, self.float_q_table)
                self.update_q_table(state, action[2], reward, new_state, self.bool_q_table)
                self.update_q_table(state, action[3], reward, new_state, self.byte_q_table)
                self.update_q_table(state, action[4], reward, new_state, self.string_q_table)

                for i in range(len(self.mutation_counts)):
                    chosen_method = self.mutation_methods[i][action[i]]  # Get the chosen mutation method dynamically
                    self.mutation_counts[i][chosen_method] += 1
                    self.mutation_rewards[i][chosen_method].append(reward)

                state = new_state
                rewards_current_episode += reward
                self.episode_rewards.append(reward)
                self.state_visits[state] += 1

                if done is True:
                    break

            # Exploration rate decay
            self.exploration_rate = self.min_exploration_rate + \
                (self.max_exploration_rate - self.min_exploration_rate) * np.exp(-self.exploration_decay_rate*episode)

            self.rewards_all_episodes.append(rewards_current_episode)

            self.q_value_convergence['int'].append(np.copy(self.int_q_table))
            self.q_value_convergence['float'].append(np.copy(self.float_q_table))
            self.q_value_convergence['bool'].append(np.copy(self.bool_q_table))
            self.q_value_convergence['byte'].append(np.copy(self.byte_q_table))
            self.q_value_convergence['string'].append(np.copy(self.string_q_table))

        # Calculate and print the average reward per hundred episodes
        rewards_per_number_episodes = np.split(np.array(self.rewards_all_episodes),num_episodes/num_episodes)
        count = num_episodes
        print("********Average reward per number of episodes********\n")
        for r in rewards_per_number_episodes:
            print(count, ": ", str(sum(r/num_episodes)))
            count += num_episodes

    def plot_q_value_convergence(self, base_path):
        x = np.arange(0, self.num_episodes)
        data_types = ['int', 'float', 'bool', 'byte', 'string']
        for data_type in data_types:
            q_values = np.array(self.q_value_convergence[data_type])
            avg_q_values = np.mean(q_values, axis=(1, 2))  # Average over states and actions
            plt.plot(x, avg_q_values, label=data_type)

        plt.xlabel('Episodes')
        plt.ylabel('Average Q-value')
        plt.legend()
        plt.title('Q-value Convergence')
        plt.savefig(base_path + "q_value_convergence.png")
        plt.close()

    def plot_learning_curve(self, num_episodes):
        # Calculate the average reward over a fixed number of episodes (e.g., last 100 episodes) and plot the learning curve
        window_size = 10
        average_rewards = [np.mean(self.episode_rewards[i:i + window_size]) for i in range(len(self.episode_rewards) - window_size + 1)]
        plt.plot(range(window_size, num_episodes + 1), average_rewards)
        plt.xlabel('Episodes')
        plt.ylabel('Average Reward')
        plt.title('Learning Curve')
        plt.show()

    def plot_action_distribution(self, base_path):
        data_types = ['int', 'float', 'bool', 'byte', 'string']
        for i in range(len(self.mutation_counts)):
            mutation_methods = list(self.mutation_counts[i].keys())
            method_counts = list(self.mutation_counts[i].values())

            indices = np.arange(len(mutation_methods))

            # Define a list of colors for the columns
            colors = plt.cm.viridis(np.linspace(0, 1, len(mutation_methods)))

            # Use the 'colors' list to set different colors for each column
            bars = plt.bar(indices, method_counts, color=colors)

            plt.xticks(indices, indices)
            plt.xlabel('Mutation Method Index')
            plt.ylabel('Action Counts')
            plt.title(f'Action Distribution for {data_types[i]}')

            # Create custom legend handles for each mutation method
            legend_handles = [mpatches.Patch(color=colors[j], label=mutation_method.__name__) for j, mutation_method in enumerate(mutation_methods)]

            # Move the legend outside the plot
            plt.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1, 1))

            # Annotate each bar with the exact number on top
            for j, count in enumerate(method_counts):
                plt.text(j, count + 0.1, str(count), ha='center', va='bottom')

            plt.savefig(base_path + "q_action_distribution_" + str(i) + ".png", bbox_inches='tight')
            plt.close()

    def plot_state_visits(self, base_path):
        states = list(range(len(self.state_visits)))
        visit_counts = list(self.state_visits)

        # Define legend labels for HTTP status code ranges
        legend_labels = ['1XX', '2XX', '3XX', '4XX', '5XX']

        # Define colors for each HTTP status code range
        colors = ['lightblue', 'green', 'yellow', 'orange', 'red']

        plt.bar(states, visit_counts, color=colors)
        plt.xlabel('HTTP Status Code Ranges')
        plt.ylabel('Number of Visits')
        plt.title('Number of Visits to Each HTTP Status Code Range')

        # Set x-axis ticks and labels to the legend labels
        plt.xticks(states, legend_labels)

        # Annotate each bar with the exact number on top
        for state, count in zip(states, visit_counts):
            plt.text(state, count + 0.1, str(count), ha='center', va='bottom')

        plt.savefig(base_path + "state_visits.png", bbox_inches='tight')
        plt.close()


    def test(self,env):
        for episode in range(5):
            state = self.env.reset()
            done = False

            print("*******Episode ", episode+1, "*******\n\n")
            for step in range(self.max_steps_per_episode):
                # Choose action with highest Q-value for current state
                self.env.render()
                # Take new action
                # time.sleep(0.3)
                action = []
                action.append(np.argmax(self.int_q_table[state,:]))
                action.append(np.argmax(self.float_q_table[state,:]))
                action.append(np.argmax(self.bool_q_table[state,:]))
                action.append(np.argmax(self.byte_q_table[state,:]))
                action.append(np.argmax(self.string_q_table[state,:]))
                new_state, reward, done = self.env.step(action)

                if done:
                    env.render()
                    if reward == 1:
                        # Agent reached the goal and won episode
                        print("****You reached the goal****")
                        # time.sleep(3)
                    break
                else:
                    print("****You lost****")
                    # time.sleep(3)

                state = new_state


