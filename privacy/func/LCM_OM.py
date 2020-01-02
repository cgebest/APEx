import numpy as np
import math
from query import Type


def lcm_om(m):
    """laplace comparision mechanism with ordering, for prefix queries
    shortcut for hist queries"""

    q = m.query
    q.true_answer = np.matmul(q.query_matrix, q.domain_hist)

    # print("true_counts= ", q.true_answer)

    # for i in range(0, q.count_query):
    #     if q.true_answer[i] > q.count_threshold:
    #         q.big_cond_index.append(i)
    #     elif q.true_answer[i] < q.count_threshold:
    #         q.small_cond_index.append(i)

    # total privacy cost
    eps = 0

    if m.query.index.__name__ not in ['qi_1', 'qi_4']:
        # q is hist query
        # rewrite the laplace b
        lap_b = m.alpha / np.log(0.5 * len(q.cond_list) / m.beta)
        eps = len(q.cond_list) * 1.0 / lap_b

        for i in range(0, len(q.cond_list)):
            x_hat = q.true_answer[i] - q.icq_c + np.random.laplace(0, lap_b, 1)
            if x_hat > 0:
                q.selected_cond_index.append(i)

    else:
        # q is prefix query
        l_idx = 0
        r_idx = len(q.cond_list) - 1

        while l_idx <= r_idx:
            m_idx = int((l_idx + r_idx) / 2)

            # print("DEBUG: m_idx= ", m_idx)

            x_hat = q.true_answer[m_idx] - q.icq_c + np.random.laplace(0, m.lap_b, 1)
            eps += 1.0 / m.lap_b

            if x_hat > 0:
                m.query.selected_cond_index.extend(range(m_idx, r_idx + 1))
                r_idx = m_idx - 1
            else:
                l_idx = m_idx + 1

    # real cost is same to the estimated one
    m.set_real_cost(eps)


def lcm_om_est_cost(m):

    if m.query.index.__name__ in ['qi_1', 'qi_4']:
        k = math.ceil(1.0 + np.log2(len(m.query.cond_list)))
    else:
        k = len(m.query.cond_list)

    # print("DEBUG: k= ", k)
    return k * np.log(0.5 * len(m.query.cond_list) / m.beta) / m.alpha
