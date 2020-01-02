import numpy as np


def lcm(m):
    """laplace comparison mechanism for icq"""

    q = m.query
    lap_b = m.lap_b
    q.lap_noise = np.random.laplace(0, lap_b, len(q.cond_list))

    # real cost is same to the estimated one
    m.set_real_cost(m.est_cost)

    q.true_answer = np.matmul(q.query_matrix, q.domain_hist)

    # print("true answer=", q.true_answer)

    q.noisy_answer = [sum(x) for x in zip(q.lap_noise, q.true_answer)]

    # for i in range(0, q.count_query):
    #     if q.true_answer[i] > q.count_threshold + m.alpha:
    #         q.big_cond_index.append(i)
    #     elif q.true_answer[i] < q.count_threshold - m.alpha:
    #         q.small_cond_index.append(i)

    cmp_result_noisy = [x - q.icq_c for x in q.noisy_answer]
    print("cmp_result_noisy= ", cmp_result_noisy)

    for i in range(0, len(q.cond_list)):
        if cmp_result_noisy[i] > 0:
            q.selected_cond_index.append(i)

    # for i in range(0, len(q.cond_list)):
    #     print("PRINT", q.cond_list[i], q.true_answer[i], q.true_answer[i] / q.cardinality, sep=',')

    print(len(q.selected_cond_index))


def lcm_est_cost(m):
    q = m.query
    est_cost = q.get_sensitivity() * (np.log(1.0 / (1.0 - (1.0 - m.beta) ** (1.0 / len(q.cond_list)))) - np.log(2)) / m.alpha

    return est_cost
