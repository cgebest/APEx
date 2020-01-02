from query import Type
from privacy.func import Strategy
from numpy import linalg as LA


class Mechanism:
    """privacy mechanism"""

    def __init__(self):
        self.query = ""
        self.method = ""
        self.alpha = 0
        self.beta = 0
        self.real_cost = 0
        self.est_cost = 0
        self.lap_b = 0
        self.return_msg = Type.ReturnMsgType.SUCCESS
        self.strategy = 0
        self.strategy_sens = 0
        self.strategy_pinv = 0
        self.m_type = ""

    def set_q(self, q):
        self.query = q
        self.m_type = q.m_type

    def set_method(self, t):
        self.method = t

    def set_alpha(self, a):
        self.alpha = a

    def set_beta(self, b):
        self.beta = b

    def set_real_cost(self, c):
        self.real_cost = c

    def set_est_cost(self, c):
        self.est_cost = c

    def set_lap_b(self, b):
        self.lap_b = b

    def set_return_qd(self):
        self.return_msg = Type.ReturnMsgType.QD

    # for SM only
    def set_strategy_h2(self):
        self.strategy = Strategy.gen_strategy_h2(len(self.query.domain_hist)).toarray()
        self.strategy_sens = LA.norm(self.strategy, 1)
        self.strategy_pinv = LA.pinv(self.strategy)

        # print("DEBUG: h2= ", self.strategy)
        # print("DEBUG: h2= ", len(self.strategy), len(self.strategy[0]))
        # print("DEBUG: h2_sens= ", self.strategy_sens)

    def set_strategy_w(self):
        # copy the workload matrix as the strategy
        self.strategy = list(self.query.query_matrix)
        self.strategy_sens = LA.norm(self.strategy, 1)
        self.strategy_pinv = LA.pinv(self.strategy)

        assert self.strategy_sens == self.query.get_sensitivity()

        # print("DEBUG: w_strategy= ", len(self.strategy), len(self.strategy[0]))
        # print("DEBUG: w_strategy_sens= ", self.strategy_sens)

    def run(self):
        print("DEBUG: alpha=", self.alpha, "\tbeta=", self.beta)
        # return self.method(self.query, self.alpha, self.beta)
        self.method(self)
