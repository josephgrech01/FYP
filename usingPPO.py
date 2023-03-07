from stable_baselines3 import PPO

from env import SumoEnv

e = SumoEnv(gui=True, noWarnings=True)

# model = PPO.load("eplen250/reward_0_2/ppo_Speed60_Nobusvectorinstate_NoWaitTimeCONTINUED")
model = PPO.load("eplen250/reward_paper_normalized5320_NoExp/ppo_Speed60_Nobusvectorinstate_NoWaitTime.zip")

obs = e.reset()
# print("obs: ", obs)

while True:
# for _ in range(250):
    action, states = model.predict(obs)
    print("action: ", action)
    obs, reward, done, info = e.step(action)
    if done:
        # obs = e.reset()
        break


e.close()
