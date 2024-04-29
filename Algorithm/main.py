from fastapi import FastAPI, HTTPException
from pydantic import BaseModel





app = FastAPI()



class AgentConfig(BaseModel):
    learning_rate: float
    discount_factor: float
    exploration_rate: float
    min_exploration_rate: float
    max_exploration_rate: float
    exploration_decay_rate: float
    mutation_methods: list

@app.post("/initialize-agent")
async def initialize_agent(config: AgentConfig):
    agent_id = str(uuid.uuid4())
    agent = QLearningAgent(
        mutation_methods=config.mutation_methods,
        learning_rate=config.learning_rate,
        discount_factor=config.discount_factor,
        exploration_rate=config.exploration_rate,
        min_exploration_rate=config.min_exploration_rate,
        max_exploration_rate=config.max_exploration_rate,
        exploration_decay_rate=config.exploration_decay_rate
    )

    return { "message": "Agent initialized successfully"}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
