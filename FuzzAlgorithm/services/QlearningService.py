import utils
from FuzzAlgorithm.Algorithm import QLearningAgent, write_agent_report
from FuzzAlgorithm.environment import APIFuzzyTestingEnvironment
from FuzzAlgorithm.services.IfuzzAlgorithmService import IFuzzingService


class QlearningService(IFuzzingService):
    async def fuzz(self, data):

        metrics = []
        env = None
        for scenario_functions in data.scenarios:
            for function in scenario_functions:
                requests_log = []
                print("Function: ", function)
                if env is None:
                    env = APIFuzzyTestingEnvironment(data.base_url, data.function[function], utils.mutation_methods,
                                                     data.ids)
                else:
                    env._change_environment_function(data.function[function])
                agent = QLearningAgent(env, utils.mutation_methods, data.max_steps_per_episode, data.exploration_rate)
                agent.train(data.num_episodes, requests_log)
                metricTrain = write_agent_report(agent, requests_log, data.ids)
                metrics.append(metricTrain)
                requests_log = []
                agent.test(requests_log)
                metricTest = write_agent_report(agent, requests_log, data.ids)
                metrics.append(metricTest)

        return metrics
