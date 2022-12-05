import numpy as np
import random
import copy
import matplotlib.pyplot as plt


class Network(object):

    def __init__(self, n, q, decay):
        self.n = n
        self.assignments = random.choices(['honest', 'attack'], weights=[1-q, q], k=n)
        self.attacker_ids = [i for i in range(len(self.assignments)) if self.assignments[i] == 'attack']
        self.honest_ids = [i for i in range(len(self.assignments)) if self.assignments[i] == 'honest']
        self.decay = decay
        self.peers = np.full((n, 8), np.nan)

    def fill_peers(self, mode, counter_rate=None):
        for i in range(self.n):
            row = self.peers[i, :]
            if mode == 'init':
                pool = list(range(self.n))
                pool.remove(i)
            else:
                pool = []
                peers = row[~np.isnan(row)]
                if mode == 'step_rand':
                    for peer in peers:
                        peer_int = int(peer)
                        peer_neighbors = self.peers[peer_int, :]
                        pool += list(peer_neighbors[~np.isnan(peer_neighbors)])
                elif mode == 'step_aggro':
                    if not counter_rate:
                        for peer in peers:
                            peer_int = int(peer)
                            peer_side = self.assignments[peer_int]
                            if peer_side == 'attack':
                                attackers = copy.deepcopy(self.attacker_ids)
                                attackers.remove(peer_int)
                                pool += random.sample(attackers, 8)
                            else:
                                peer_neighbors = self.peers[peer_int, :]
                                pool += list(peer_neighbors[~np.isnan(peer_neighbors)])
                    else:
                        if np.random.binomial(1, counter_rate):
                            pool = copy.deepcopy(self.honest_ids)
                        else:
                            for peer in peers:
                                peer_int = int(peer)
                                peer_side = self.assignments[peer_int]
                                if peer_side == 'attack':
                                    attackers = copy.deepcopy(self.attacker_ids)
                                    attackers.remove(peer_int)
                                    pool += random.sample(attackers, 8)
                                else:
                                    peer_neighbors = self.peers[peer_int, :]
                                    pool += list(peer_neighbors[~np.isnan(peer_neighbors)])
                pool = list(set(pool))
                if np.float64(i) in pool:
                    pool.remove(np.float64(i))
                for peer in peers:
                    if peer in pool:
                        pool.remove(peer)
            for j in range(len(row)):
                if np.isnan(row[j]):
                    ind = random.choice(list(range(len(pool))))
                    row[j] = pool.pop(ind)

    def decay_peers(self):
        for i in range(self.n):
            for j in range(8):
                if np.random.binomial(1, self.decay):
                    self.peers[i, j] = np.nan

    def get_proportions(self):
        props = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(self.n):
            k = 0
            row = self.peers[i, :]
            for ind in row:
                if self.assignments[int(ind)] == 'attack':
                    k += 1
            props[k] += 1
        props = [prop / self.n for prop in props]
        return props


def simulate_network(n, q, decay, T, mode, counter_rate, title, fname):
    proportions = np.zeros((9, T))
    net = Network(n, q, decay)
    net.fill_peers('init')
    proportions[:, 0] = net.get_proportions()
    for t in range(T-1):
        net.decay_peers()
        net.fill_peers(mode, counter_rate)
        proportions[:, t+1] = net.get_proportions()

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    colors = ['tab:gray', 'tab:blue', 'tab:cyan', 'tab:green', 'tab:olive', 'tab:brown', 'tab:orange', 'tab:pink', 'tab:red']
    for i in range(9):
        ax.plot(range(T), proportions[i, :], colors[i], label=f'{i} Malicious Peers')
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel('Proportion')
    plt.legend()
    plt.savefig(fname)

simulate_network(1000, 0.1, 0.05, 200, 'step_aggro', 0.5, 'Sybil Attack Simulation: Counter-Aggressive Case (Counter Rate = 0.5)', 'sim_counter2.png')
