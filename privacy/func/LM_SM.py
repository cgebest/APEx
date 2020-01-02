import numpy as np
from numpy import linalg as LA
import scipy.stats as st


def lm_sm(m):
    """laplace mechanism using strategy"""
    q = m.query

    # print("DEBUG: before multiple true answer")
    # print("DEBUG: len(q.query_matrix)=", len(q.query_matrix))
    # print("DEBUG: len(q.domain_hist)=", len(q.domain_hist))

    q.true_answer = np.matmul(q.query_matrix, q.domain_hist)

    # print("DEBUG: q.query_matrix= ", q.query_matrix)
    # print("DEBUG: q.domain_hist= ", q.domain_hist)
    # print("DEBUG: true answer= ", q.true_answer)

    # print("i, cond_list, true_answer")
    # for i in range(0, len(q.cond_list)):
    #     print(i, "\t", q.cond_list[i], "\t", q.true_answer[i])

    # compute the inverse of strategy
    strategy_pinv = LA.pinv(m.strategy)
    # print("DEBUG: len(strategy_pinv)= ", len(strategy_pinv), len(strategy_pinv[0]))

    wap = np.matmul(q.query_matrix, strategy_pinv)

    Ax = np.matmul(m.strategy, q.domain_hist)
    q.lap_noise = np.random.laplace(0, m.lap_b, len(Ax))

    # print("DEBUG: q.lap_nosie=", q.lap_noise)

    Ax_noise = [sum(x) for x in zip(Ax, q.lap_noise)]

    q.noisy_answer = np.matmul(wap, Ax_noise)

    assert len(q.noisy_answer) == len(q.true_answer)
    for i in range(0, len(q.noisy_answer)):
        crnt_answer_diff = q.noisy_answer[i] - q.true_answer[i]
        q.answer_diff.append(crnt_answer_diff)

    m.set_real_cost(m.est_cost)


eps_diff = 0.0000001
sample_size = 10000


def lm_sm_est_cost(m):

    # sm_key like qw2_0.02_100000_0.000001_1
    sm_key = m.query.index.__name__ + "_" + str(len(m.query.cond_list)) + "_" + str(int(m.alpha)) + "_" + \
             str(sample_size) + "_" + str(eps_diff) + str(m.query.data_size)

    if sm_key in m.query.eps_cache:
        eps_max = m.query.eps_cache.get(sm_key)
        print("DEBUG: reuse cache sm_key=", sm_key)
        return eps_max

    wap = np.matmul(m.query.query_matrix, m.strategy_pinv)
    eps_max = m.strategy_sens * LA.norm(wap) / (m.alpha * np.sqrt(m.beta / 2.0))
    eps_min = 0

    # print("DEBUG: begin eps_max=", eps_max, "\teps_min=", eps_min)

    count = 0
    while (eps_max - eps_min) > eps_diff:
        count += 1
        eps = (eps_max + eps_min) / 2.0
        beta_e_adjust = estimate_beta_mc(eps, m)

        # print("DEBUG: beta_e_adjust=", beta_e_adjust)

        if beta_e_adjust < m.beta:
            eps_max = eps
        else:
            eps_min = eps

    print("DEBUG: alpha=", m.alpha, "\tcount=", count, "\teps_max=", eps_max)

    # store cache
    m.query.eps_cache[sm_key] = eps_max

    return eps_max


def estimate_beta_mc(eps, m):
    counter_fail = 0
    alpha = m.alpha
    beta = m.beta

    for i in range(int(sample_size)):
        lap_noise = np.random.laplace(0, m.strategy_sens / eps, len(m.strategy))
        max_err = LA.norm(np.matmul(m.strategy_pinv, lap_noise), np.inf)
        if max_err > alpha:
            counter_fail = counter_fail + 1

    # print("DEBUG: counter_fail=", counter_fail)

    beta_e = 1.0 * counter_fail / sample_size
    conf_p = beta / 100.0
    zscore = st.norm.ppf(1.0 - conf_p / 2.0)
    delta_beta = zscore * np.sqrt(beta_e * (1.0 - beta_e) / sample_size)
    beta_e_adjust = beta_e + delta_beta + conf_p

    return beta_e_adjust
