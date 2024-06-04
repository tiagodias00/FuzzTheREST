import utils
from FuzzAlgorithm.Algorithm import QLearningAgent, write_agent_report
from FuzzAlgorithm.environment import APIFuzzyTestingEnvironment
from FuzzAlgorithm.services.IfuzzAlgorithmService import IFuzzingService
import time

class QlearningService(IFuzzingService):
    async def fuzz(self, data):


        start_time = time.time()
        metrics = []
        crashes = {}
        hangs={}
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
                agent.train(data.num_episodes, requests_log, crashes,hangs)
                name = "Train" + function
                metricTrain = write_agent_report(agent, requests_log, data.ids,name)
                metrics.append(metricTrain)
                requests_log = []
                agent.test(requests_log,crashes,hangs)
                name = "Test" + function
                metricTest = write_agent_report(agent, requests_log, data.ids,name)
                metrics.append(metricTest)
        end_time = time.time()
        duration = end_time - start_time
        return {"Requests_metrics":metrics,"Duration":duration,"Crashes":crashes,"Hangs":hangs}
