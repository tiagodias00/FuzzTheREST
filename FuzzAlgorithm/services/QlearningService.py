import utils
from FuzzAlgorithm.Algorithm import QLearningAgent
from FuzzAlgorithm.environment import APIFuzzyTestingEnvironment
from FuzzAlgorithm.services.IfuzzAlgorithmService import IFuzzingService


class QlearningService(IFuzzingService):
    async def fuzz(self, data):
        env = APIFuzzyTestingEnvironment(data.base_url, data.function, utils.mutation_methods, data.ids)
        agent = QLearningAgent(env, utils.mutation_methods, data.max_steps_per_episode, data.exploration_rate)
        agent.train(data.num_episodes)
        agent.test()
        return {"message": "FuzzAlgorithm initialized"}
