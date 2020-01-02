import numpy as np


def lcm_mp(m):
    """icp with multi poking. assume q has one single count"""
    q = m.query
    q.true_answer = np.matmul(q.query_matrix, q.domain_hist)

    # print(q.true_answer)

    # need to split the beta
    eps_max = m.est_cost

    eps0 = eps_max / q.count_poking
    lap_b = q.get_sensitivity() / eps0
    lap_noises = np.random.laplace(0, lap_b, len(q.cond_list))

    y = q.true_answer - q.icq_c + lap_noises

    print("DEBUG: alpha=", m.alpha, "\teps_max=", eps_max)
    poking_complete = False
    q.real_count_poking = 0

    epsi = eps0
    for i in range(0, q.count_poking-1):
        q.real_count_poking += 1

        ai = q.get_sensitivity() * np.log(q.count_poking * len(q.cond_list) * 0.5 / m.beta) / epsi
        pred_positive = []
        pred_negative = []
        for j in range(0, len(q.cond_list)):
            if (y[j] - ai) / m.alpha >= -1:
                pred_positive.append(j)
            elif (y[j] + ai) / m.alpha <= 1:
                pred_negative.append(j)

        if len(pred_negative) + len(pred_positive) == len(q.cond_list):
            m.set_real_cost(epsi)
            q.selected_cond_index = pred_positive
            poking_complete = True
            break
        else:
            epsi += eps0
            for j in range(0, len(q.cond_list)):
                # noise down here
                lap_noises[j] = noise_down(lap_noises[j], epsi - eps0, epsi)
            # update the noise answer
            y = q.true_answer - q.icq_c + lap_noises

    if not poking_complete:
        m.set_real_cost(eps_max)

        for j in range(0, len(q.cond_list)):
            if y[j] > 0:
                q.selected_cond_index.append(j)

    # for k in range(0, len(q.cond_list)):
    #     eps0 = eps_max / q.count_poking
    #     true_answer = q.true_answer[k]
    #     lap_noise = lap_noises[k]
    #     epsi = eps0
    #     from_flag = False
    #
    #     print("icq_c=", q.icq_c, "\ttrue_answer=", true_answer, "\tlap_noise=", lap_noise)
    #     x_hat = true_answer - q.icq_c + lap_noise
    #
    #     for i in range(0, q.count_poking - 2):
    #         ai = np.log(0.5 * q.count_poking / m.beta) / epsi
    #
    #         q.real_count_poking[k] = i + 1
    #
    #         if (x_hat - ai) / m.alpha >= -1.0:
    #             eps_total += epsi
    #             q.selected_cond_index.append(k)  # True
    #             from_flag = True
    #             break
    #
    #         elif (x_hat + ai) / m.alpha <= 1.0:
    #             eps_total += epsi  # Flase
    #             from_flag = True
    #             break
    #
    #         else:
    #             epsi += eps0
    #             # update noise
    #             old_lap_noise = lap_noise
    #
    #             lap_noise = noise_down(lap_noise, epsi-eps0, epsi)
    #
    #             # print("DEBUG: idx= ", k, "\told_lap_noise=", old_lap_noise, "\t new_lap_noise=", lap_noise)
    #             # assert abs(lap_noise) <= abs(old_lap_noise)
    #
    #             x_hat = true_answer - q.icq_c + lap_noise
    #
    #     if not from_flag:
    #         eps_total += eps_max
    #         if x_hat > 0:
    #             q.selected_cond_index.append(k)  # True
    #
    # # set the real cost
    # m.set_real_cost(eps_total)

    print("DEBUG: print count_poking for all queries")
    print(q.real_count_poking)
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


def noise_down(lap_noise, eps_old, eps_new):
    assert eps_new > eps_old

    pdf = [eps_old / eps_new * np.exp((eps_old - eps_new) * abs(lap_noise)),
           (eps_new - eps_old) / (2.0 * eps_new),
           (eps_old + eps_new) / (2.0 * eps_new) * (1.0 - np.exp((eps_old - eps_new) * abs(lap_noise)))]

    p = np.random.random_sample()

    if p <= pdf[0]:
        z = lap_noise

    elif p <= pdf[0] + pdf[1]:
        z = np.log(p) / (eps_old + eps_new)

    elif p <= pdf[0] + pdf[1] + pdf[2]:
        z = np.log(p * (np.exp(abs(lap_noise) * (eps_old - eps_new)) - 1.0) + 1.0) / (eps_old - eps_new)

    else:
        z = abs(lap_noise) - np.log(1.0 - p) / (eps_new + eps_old)

    return z


# estimate the cost of poking
def lcm_mp_est_cost(m):

    # est_cost = np.log(0.5 * m.query.count_poking / m.beta) / m.alpha
    est_cost = m.query.get_sensitivity() * \
               np.log(m.query.count_poking * len(m.query.cond_list) * 0.5 / m.beta) / m.alpha
    return est_cost


def test_mpm():
    all_noise = []
    repeats = 10000
    for repeat in range(0, repeats):
        m = 2
        eps_max = 2.0
        eps0 = eps_max / m
        noises = []
        noise = np.random.laplace(0, 1.0/eps0)
        noises.append(noise**2)
        eps_i = eps0
        for i in range(0, m-1):
            eps_i += eps0
            noise = noise_down(noise, eps_i - eps0, eps_i)
            # exit(0)
            noises.append(noise**2)

        all_noise.append(noises)


    for col in range(0, m):
        col_sum = 0
        for row in range(0, repeats):
            col_sum += abs(all_noise[row][col])

        print("col=", col, "\t", np.sqrt(col_sum / repeats))


