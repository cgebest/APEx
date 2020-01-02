import numpy as np
import pickle
from query import Type
from privacy import Mechanism
from privacy.func.LM import lm, lm_est_cost
from privacy.func.LM_SM import lm_sm, lm_sm_est_cost
from privacy.func.LCM import lcm, lcm_est_cost
from privacy.func.LCM_SM import lcm_sm, lcm_sm_est_cost
from privacy.func.LCM_OM import lcm_om, lcm_om_est_cost
from privacy.func.LCM_MP import lcm_mp, lcm_mp_est_cost
from privacy.func.LCT import lct, lct_est_cost
from privacy.func.LCT_NM import lct_nm, lct_nm_est_cost


class PrivacyEngine:
    """define all the dp related methods"""

    def __init__(self, budget, d):
        self.B = budget
        self.total_privacy_cost = 0
        self.m_list = []

        self.Wx_cache_W = dict()
        self.Wx_cache_x = dict()
        self.Wx_cache_N = dict()
        self.eps_cache = dict()

        try:
            with open('Wx.pkl', 'rb') as input:
                self.Wx_cache_W = pickle.load(input)
                self.Wx_cache_x = pickle.load(input)
                self.Wx_cache_N = pickle.load(input)
                self.eps_cache = pickle.load(input)
        except (OSError, IOError, FileNotFoundError, EOFError) as e:
            self.Wx_cache_W = dict()
            self.Wx_cache_x = dict()
            self.Wx_cache_N = dict()
            self.eps_cache = dict()

    def __del__(self):
        with open('Wx.pkl', 'wb') as output:
            pickle.dump(self.Wx_cache_W, output, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.Wx_cache_x, output, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.Wx_cache_N, output, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.eps_cache, output, pickle.HIGHEST_PROTOCOL)

    def run_query(self, q, alpha, beta):

        # set the cache repos
        q.set_cache(self.Wx_cache_W, self.Wx_cache_x, self.Wx_cache_N, self.eps_cache)

        # matrix transform, use the mechanism to represent
        m = self.translate(q, alpha, beta)

        # estimate the cost of mechanism
        total_privacy_cost_est = self.estimate_loss(m)

        print("total_privacy_cost_est= ", total_privacy_cost_est)

        if total_privacy_cost_est <= self.B:
            # run the query through mechanism m
            m.run()

            self.m_list.append(m)

            # update the total cost
            self.total_privacy_cost = self.analyze_loss()
        else:
            m.set_return_qd()

        # return the mechanism
        return m

    # translate the query to matrix, and assign mechanism based on query type
    def translate(self, q, alpha, beta):
        # matrix representation
        q.to_matrix()

        # initialize the mechanism for this query
        m = Mechanism.Mechanism()
        m.set_q(q)
        m.set_alpha(alpha)
        m.set_beta(beta)

        # decide which function to call
        if q.query_type == Type.QueryType.WCQ:
            assert q.tcq_k == -1
            assert q.icq_c == -1

            if q.m_type == Type.MechanismType.LM:
                m.set_method(lm)

            elif q.m_type == Type.MechanismType.LM_SM:
                m.set_method(lm_sm)
                # TODO: set different strategies here
                m.set_strategy_h2()

            else:
                print("ERROR: wrong mechanism_type ", q.m_type)
        elif q.query_type == Type.QueryType.ICQ:
            assert q.tcq_k == -1
            assert q.icq_c != -1

            if q.m_type == Type.MechanismType.LCM:
                m.set_method(lcm)
            elif q.m_type == Type.MechanismType.LCM_SM:
                m.set_method(lcm_sm)
                # TODO: set different strategies here
                m.set_strategy_h2()

            elif q.m_type == Type.MechanismType.LCM_OM:
                m.set_method(lcm_om)

            elif q.m_type == Type.MechanismType.LCM_MP:
                m.set_method(lcm_mp)

            else:
                print("ERROR: wrong mechanism_type ", q.m_type)

        elif q.query_type == Type.QueryType.TCQ:
            assert q.tcq_k > 0
            assert q.icq_c == -1

            if q.m_type == Type.MechanismType.LCT:
                m.set_method(lct)
            elif q.m_type == Type.MechanismType.LCT_NM:
                m.set_method(lct_nm)
            else:
                print("ERROR: wrong mechanism_type ", q.m_type)

        # return the mechanism
        print("DEBUG: finish translating")
        return m

    # estimate cost using sequential composition
    def estimate_loss(self, m):
        # estimate the cost based on the query type
        q = m.query
        if q.query_type == Type.QueryType.WCQ:
            if q.m_type == Type.MechanismType.LM:
                # estimate cost
                est_cost = lm_est_cost(m)
                m.set_est_cost(est_cost)

                # set the laplace b
                m.set_lap_b(q.get_sensitivity() / est_cost)

            elif q.m_type == Type.MechanismType.LM_SM:
                # estimate cost
                est_cost = lm_sm_est_cost(m)
                m.set_est_cost(est_cost)

                # set the laplace b
                print("DEBUG: est_cost=", est_cost, "\tm.strategy_sens=", m.strategy_sens, "\tlaplace_b=", m.strategy_sens / est_cost)

                m.set_lap_b(m.strategy_sens / est_cost)

        elif q.query_type == Type.QueryType.ICQ:
            if q.m_type == Type.MechanismType.LCM:
                # estimate cost
                est_cost = lcm_est_cost(m)
                m.set_est_cost(est_cost)

                # set laplace b
                m.set_lap_b(q.get_sensitivity() / est_cost)

            elif q.m_type == Type.MechanismType.LCM_SM:
                # estimate cost
                est_cost = lcm_sm_est_cost(m)
                m.set_est_cost(est_cost)

                # set the laplace b
                m.set_lap_b(m.strategy_sens / est_cost)

            elif q.m_type == Type.MechanismType.LCM_OM:
                # estimate cost
                est_cost = lcm_om_est_cost(m)
                m.set_est_cost(est_cost)

                # set the laplace b
                m.set_lap_b(m.alpha / np.log(0.5 * len(m.query.cond_list) / m.beta))

            elif q.m_type == Type.MechanismType.LCM_MP:
                # estimate cost
                est_cost = lcm_mp_est_cost(m)
                m.set_est_cost(est_cost)

                # do not set laplace b since it's variable

        elif q.query_type == Type.QueryType.TCQ:
            if q.m_type == Type.MechanismType.LCT:
                # estimate the cost
                est_cost = lct_est_cost(m)
                m.set_est_cost(est_cost)

                # set laplace b
                m.set_lap_b(q.get_sensitivity() / est_cost)

            elif q.m_type == Type.MechanismType.LCT_NM:
                # estimate the cost
                est_cost = lct_nm_est_cost(m)
                m.set_est_cost(est_cost)

                # set laplace b
                m.set_lap_b(q.tcq_k / est_cost)

        return self.total_privacy_cost + m.est_cost

    # privacy analyzer
    def analyze_loss(self):
        cost_sum = 0
        for m in self.m_list:
            cost_sum += m.real_cost
        return cost_sum

