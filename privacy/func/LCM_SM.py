from privacy.func import LM_SM


def lcm_sm(m):
    """SM for answering ICQ queries"""
    # run the SM using WCQ functions
    LM_SM.lm_sm(m)

    q = m.query

    # print("DEBUG: icq_c= ", q.icq_c)

    idx = 0
    for crnt_noisy_answer in q.noisy_answer:
        if crnt_noisy_answer - q.icq_c > 0:
            q.selected_cond_index.append(idx)
        idx = idx + 1

    print("selected_cond_index=", m.query.selected_cond_index)
    true_list = []
    idx = 0
    for crnt_true_answer in q.true_answer:
        if crnt_true_answer > q.icq_c:
            if len(true_list) == 0:
                print("DEBUG: first true_cond=", q.cond_list[idx], "\tcrnt_true_answer= ", crnt_true_answer)

            true_list.append(idx)

        idx = idx + 1
    print("true_cond_index=", true_list)

    for i in range(0, len(q.cond_list)):
        print("PRINT", q.cond_list[i], q.true_answer[i], q.true_answer[i] / q.cardinality, sep=',')


def lcm_sm_est_cost(m):
    return LM_SM.lm_sm_est_cost(m)

