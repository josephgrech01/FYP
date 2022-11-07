from stable_baselines3 import DQN

from env import SumoEnv

e = SumoEnv(gui=False, noWarnings=True)

model = DQN("MlpPolicy", e, verbose=1, tensorboard_log="tensorboard/", exploration_initial_eps=2)
model.learn(total_timesteps=90000, log_interval=4)
model.save("dqn_model_MaxSD")

e.close()
