import numpy as np


def lm(m):
    """WCQ laplace mechanism, input is an object of Mechanism class"""

    q = m.query
    lap_b = m.lap_b
    q.lap_noise = np.random.laplace(0, lap_b, len(q.cond_list))

    # real cost is same to the estimated one
    m.set_real_cost(m.est_cost)

    q.true_answer = np.matmul(q.query_matrix, q.domain_hist)
    print("true_answers via matrix= ", q.true_answer)

    q.noisy_answer = [sum(x) for x in zip(q.lap_noise, q.true_answer)]

    q.answer_diff = q.lap_noise

    print("query_result_noisy= ", q.noisy_answer)
    print("laplace_noise= ", q.lap_noise)
    # print("OUTPUT:", q.index, ",", abs(max(q.lap_noise, key=abs)), ",", real_privacy_cost, ",", m.alpha)


def lm_est_cost(m):
    q = m.query
    est_cost = q.get_sensitivity() * np.log(1.0 / (1.0 - (1.0 - m.beta) ** (1.0 / len(q.cond_list)))) / m.alpha
    return est_cost
