import numpy as np
import random
import matplotlib.pyplot as plt
import ArkanoidEnv
import pygame
import pprint, pickle

env = ArkanoidEnv.ArkanoidEnv() 

# Параметры обучения
learning_rate = 0.1        
discount_factor = 0.96     
exploration_rate = 1.0
max_exploration_rate = 1.0
min_exploration_rate = 0.001
exploration_decay_rate = 0.995
total_episodes = 2000
model_name='q_table_2000.pkl'
use_generated_models = False


# Для отслеживания прогресса обучения
rewards_all_episodes = []
steps_per_episode = []
exploration_rates = []

state_bins = [
            # Позиция мяча по X (5 интервалов)
            np.linspace(0, 1, 6),
            # Позиция мяча по Y (5 интервалов)
            np.linspace(0, 1, 6),
            # Направление мяча по X (3 интервала)
            np.linspace(-1, 1, 4),
            # Направление мяча по Y (3 интервала)
            np.linspace(-1, 1, 4),
            # Позиция платформы (5 интервалов)
            np.linspace(0, 1, 6)
        ]
        
# Размерность Q-таблицы
state_dims = [len(bins)-1 for bins in state_bins]
state_dims.append(env.action_space)  # Добавляем размерность действий

# Инициализация Q-таблицы нулями
q_table = np.zeros(state_dims)

# Дискретизируем
def discretize_state(state):
    discretized = []
    for i in range(len(state_bins)):
        discretized.append(np.digitize(state[i], state_bins[i]) - 1)
        discretized[-1] = max(0, min(discretized[-1], state_dims[i]-1))
    return tuple(discretized)

# Обновление q-таблицы
def update_q_table(state, action, reward, next_state, done):
    discretized_state = discretize_state(state)
    discretized_next_state = discretize_state(next_state)
    
    # Текущее Q-значение
    current_q = q_table[discretized_state + (action,)]
    
    # Q-значение для следующего состояния
    if done:
        max_next_q = 0
    else:
        max_next_q = np.max(q_table[discretized_next_state])
    
    # Новое Q-значение
    new_q = current_q + learning_rate * (
        reward + discount_factor * max_next_q - current_q
    )
    
    # Обновляю
    q_table[discretized_state + (action,)] = new_q

# Выбор действия
def get_action(state):
    if random.uniform(0, 1) <exploration_rate:
        # случайное действие
        return random.randint(0,env.action_space - 1)
    else:
        # действие с максимальным Q-значением
        discretized_state =discretize_state(state)
        return np.argmax(q_table[discretized_state])
    
def get_action_model(state):
    discretized_state =discretize_state(state)
    return np.argmax(q_table[discretized_state])

# Уменьшает скорость обучения
def decay_exploration():
    ee = max(
        min_exploration_rate, 
        exploration_rate * exploration_decay_rate
    )
    return ee

# Сохранение q-таблицы
def save(data):
    output = open('models/' + model_name, 'wb')
    pickle.dump(data, output)
    output.close()

# Загрузка q-таблицы
def load():
    pkl_file = open('models/' + model_name, 'rb')
    data = pickle.load(pkl_file)
    pkl_file.close()
    return data

if use_generated_models == False:
# Процесс обучения
    for episode in range(total_episodes):
        state = env.reset()
        done = False
        rewards_current_episode = 0
        steps = 0

        while not done:
            # Выбор действия (с учетом исследования и использования)
            action = get_action(state)  # Случайное действие
            new_state, reward, done, info = env.step(action)

            # Обновление Q-значений
            update_q_table(state, action, reward, new_state, done)

            rewards_current_episode += reward
            state = new_state
            steps += 1

            # Рендерим иногда для визуализации
            if episode % 1500 == 0:
                env.render()
                
                # Обработка событий для выхода
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        env.close()
                        break

        exploration_rate = decay_exploration()
        # Сохранение результатов
        rewards_all_episodes.append(rewards_current_episode)
        steps_per_episode.append(steps)
        exploration_rates.append(exploration_rate)

        # Вывод прогресса каждые 1000 эпизодов
        if (episode + 1) % 100 == 0:
            avg_reward = np.mean(rewards_all_episodes[-100:])
            print(f"Эпизод: {episode + 1}, Средняя награда: {avg_reward:.4f}, Exploration rate: {exploration_rate:.4f}")


    # Визуализация прогресса обучения
    plt.figure(figsize=(12, 5))

    # График средних наград
    plt.subplot(1, 2, 1)
    plt.plot(range(total_episodes), rewards_all_episodes, color='blue', alpha=0.6, label='Награды')
    plt.xlabel('Эпизод')
    plt.ylabel('Награда')
    plt.title('Награды за эпизод')
    plt.legend()

    # График шагов за эпизод
    plt.subplot(1, 2, 2)
    plt.plot(range(total_episodes), steps_per_episode, color='green', alpha=0.6, label='Шаги')
    plt.xlabel('Эпизод')
    plt.ylabel('Количество шагов')
    plt.title('Шаги за эпизод')
    plt.legend()

    plt.tight_layout()
    plt.savefig("models/" + model_name +'.statistic.png')
    plt.show()

    save(q_table)

else:
    q_table = load()

# Вывод обученной Q-таблицы
print("\nОбученная Q-таблица:")
print(q_table)

# Тестирование обученного агента
num_test_episodes = 10
print("\nТестирование обученного агента:\n")
for episode in range(num_test_episodes):
    state = env.reset()
    done = False
    print(f"Эпизод {episode + 1}:")
    env.render()
    steps = 0

    while not done:
        action = get_action_model(state)
        new_state, reward, done, info = env.step(action)
        env.render()
        state = new_state
        steps += 1


# Закрытие среды
env.close()