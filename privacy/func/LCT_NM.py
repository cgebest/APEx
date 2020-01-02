import numpy as np


def lct_nm(m):

    q = m.query
    lap_b = m.lap_b
    q.lap_noise = np.random.laplace(0, lap_b, len(q.cond_list))
    print("q.lap_noise=", q.lap_noise)

    q.true_answer = np.matmul(q.query_matrix, q.domain_hist)
    # print("true_answers= ", q.true_answer)

    q.noisy_answer = [sum(x) for x in zip(q.lap_noise, q.true_answer)]

    arr = np.array(q.noisy_answer)
    q.selected_arg_list = arr.argsort()[-q.tcq_k:][::-1]

    arr = np.array(q.true_answer)
    true_arg_list = arr.argsort()[-q.tcq_k:][::-1]
    print("true_arg_list= ", true_arg_list)
    print("selected_arg_list=", q.selected_arg_list)
    # print("top k*2=", sorted(q.true_answer, reverse = True)[:2*q.tcq_k])

    # real cost is same to the estimated one
    m.set_real_cost(m.est_cost)

    # for i in range(0, len(q.cond_list)):
    #     print("PRINT", q.cond_list[i], q.true_answer[i], q.true_answer[i] / q.cardinality, sep=',')


def lct_nm_est_cost(m):
    q = m.query
    k = q.tcq_k
    est_cost = 2.0 * k * (np.log(len(q.cond_list)) + np.log(1.0 / (2.0 * m.beta))) / m.alpha

    return est_cost
