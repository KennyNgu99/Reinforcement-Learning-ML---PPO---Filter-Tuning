import gym
from previous import PPOEnv
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback

env = PPOEnv()

def PPO_train():
    checkpoint_callback = CheckpointCallback(save_freq=500, save_path='./trained/logs2/', name_prefix='ppo_model_2v')
    model = PPO("MlpPolicy", env, learning_rate=0.001, verbose=1)
    model.learn(total_timesteps=10000, callback=checkpoint_callback)
    model.save("HFSS_trained_file_2v")



def PPO_load(p1, p2):
    model = PPO.load("ppo_model_2v_5000_steps")
    episode = 5
    for x in range(episode):
        i, currentstep, done = 0, 0, False

        obs = env.reset(p1, p2)
        print("Episode {} ...".format(x+1))
        while not done:
            currentstep += 1
            action, _states = model.predict(obs)
            obs, rewards, done, info = env.step(action, p1, p2)
            i += rewards

        if done:
            if currentstep < 100:
                status = "Converge in step " + str(currentstep)
            else:
                status = "Fail to converge"
            print("Episode: {} = {}".format(x + 1, status))
            print("\tTotal Reward = {} (The lower the better)".format(i))
            print("\tTuned Parameters:", info)


if __name__ == '__main__':
    #PPO_train()
    PPO_load(20.0, 18.0)





























