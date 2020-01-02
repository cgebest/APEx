from conn import DB
import numpy as np
from query import Type
from sklearn.metrics import f1_score


class QueryBag:
    """intermediate structure when formalizing query matrix representation"""
    def __init__(self):
        self.id_set = set()
        self.query_list = []

    def add_q(self, new_q):
        if type(new_q) is list:
            self.query_list.extend(new_q)
        else:
            self.query_list.append(new_q)

    def add_ids(self, ids):
        self.id_set.update(set(ids))


class Query:
    """the query class"""

    query_type = Type.QueryType.WCQ

    def __init__(self):
        self.index = -1
        self.cond_list = []

        self.query_type = -1

        self.query_bags = []  # intermediate holder for each condition/predicate
        self.query_matrix = []  # W
        self.domain_hist = []  # x
        self.true_answer = []  # the true counting of queries using matrix mechanism
        self.noisy_answer = []  # noisy counting
        self.lap_noise = []  # a list of laplace noise

        self.cardinality = -1  # cardinality of the table, will assign when get_cond_list

        # WCQ related
        self.answer_diff = []

        # ICQ related
        self.icq_c = -1
        self.selected_cond_index = []
        self.count_poking = -1
        self.real_count_poking = []  # a list of true poking times per predicate

        # TCQ related
        self.tcq_k = -1
        self.selected_arg_list = []

        # data set related
        self.table_name = ""
        self.data_size = 1
        self.db = ""

        self.m_type = ""
        self.query_key = -1

        self.Wx_cache_W = dict()
        self.Wx_cache_x = dict()
        self.Wx_cache_N = dict()
        self.eps_cache = dict()

    # set the query index
    def set_index(self, i):
        self.index = i

    # set query predicates
    def set_cond_list(self, p):
        self.cond_list = p

    # set the table and db connection
    def set_data_and_size(self, ds, s):
        if ds == 'census':
            self.table_name = 'census.income'
        elif ds == 'location':
            self.table_name = 'location.trip'
        else:
            print("ERROR: not supported data set ", ds)
        # set the db connection and size
        self.db = DB.DB(ds)
        self.data_size = s

    def set_query_type(self, qt, icq_c=-1, mpm_p=-1, tcq_k=-1):
        self.query_type = qt
        if qt == Type.QueryType.ICQ:
            assert icq_c != -1
            self.icq_c = icq_c
            self.count_poking = mpm_p
            self.real_count_poking = 0
        elif qt == Type.QueryType.TCQ:
            assert tcq_k != -1
            self.tcq_k = tcq_k

    def set_mechanism_type(self, m):
        self.m_type = m

    def set_cache(self, w, x, n, e):
        self.Wx_cache_W = w
        self.Wx_cache_x = x
        self.Wx_cache_N = n
        self.eps_cache = e

    # collect the ids for each condition to build histogram
    def get_cond_ids(self):
        counter = 0
        table_name = self.table_name + str(self.data_size)

        for cond in self.cond_list:
            # initialize an object to hold the ids and its belonging queries
            crnt_query_bag = QueryBag()
            crnt_query_bag.add_q(counter)

            # prepare the query to query ids
            crnt_query = 'select id from ' + table_name + ' where ' + cond
            crnt_query_rs = self.db.run(crnt_query)

            # store the row ids
            crnt_query_bag.add_ids([i[0] for i in crnt_query_rs])
            self.query_bags.append(crnt_query_bag)
            # print(len(crnt_query_rs))
            counter = counter + 1

        # get the total count from the table
        crnt_query = 'select count(*) from ' + table_name
        self.cardinality = self.db.run(crnt_query)[0][0]
        self.db.close_conn()

    def get_cond_counts(self):
        table_name = self.table_name + str(self.data_size)
        counts_list = []

        for cond in self.cond_list:
            # prepare the query to query ids
            crnt_query = 'select count(*) from ' + table_name + ' where ' + cond
            counts_list.append(self.db.run(crnt_query)[0][0])

        # get the total count from the table
        crnt_query = 'select count(*) from ' + table_name
        self.cardinality = self.db.run(crnt_query)[0][0]
        self.db.close_conn()

        return counts_list

    # construct the matrix representation of the query
    def to_matrix(self):

        # check if the results was previously cached
        # key qw1_100_1
        self.query_key = self.index.__name__ + str(len(self.cond_list)) + str(self.data_size)

        if self.query_key in self.Wx_cache_W:
            self.domain_hist = self.Wx_cache_W.get(self.query_key)
            self.query_matrix = self.Wx_cache_x.get(self.query_key)
            self.cardinality = self.Wx_cache_N.get(self.query_key)
            print("DEBUG: reuse cache query_key=", self.query_key)
            return
        else:
            print("DEBUG: no cache query_key=", self.query_key)

        # if the query is qt_2 or qt_4, otherwise just count
        if self.index.__name__ in ['qt_2', 'qt_4']:  # HD
            # first of all, collect the ids for each condition
            self.get_cond_ids()

            disjoint_query_bags = list()
            print("len(self.query_bags)= ", len(self.query_bags))
            disjoint_query_bags.append(self.query_bags[0])

            for i in range(1, len(self.cond_list)):
                # use the current query bag to iterate the existing disjoint bags
                crnt_query_bag = self.query_bags[i]
                disjoint_query_bags_size = len(disjoint_query_bags)

                for j in range(0, disjoint_query_bags_size):
                    existing_query_bag = disjoint_query_bags[j]
                    # find the intersection
                    set_intersect = existing_query_bag.id_set & crnt_query_bag.id_set
                    if len(set_intersect) > 0:
                        # intersection is not empty
                        intersect_query_bag = QueryBag()

                        # add the intersected ids into new query bag
                        intersect_query_bag.add_ids(set_intersect)

                        # set the queries from both current and previous query bags
                        intersect_query_bag.add_q(existing_query_bag.query_list)
                        intersect_query_bag.add_q(crnt_query_bag.query_list)

                        # extract the intersection from previous two bags
                        existing_query_bag.id_set = existing_query_bag.id_set - set_intersect
                        crnt_query_bag.id_set = crnt_query_bag.id_set - set_intersect

                        # append the intersected query bag into disjoint bag list
                        disjoint_query_bags.append(intersect_query_bag)

                # add the remaining crnt_query_bag into disjoint bag list
                if len(crnt_query_bag.id_set) > 0:
                    disjoint_query_bags.append(crnt_query_bag)

            # clean the disjoin query bags
            caught_count = 0
            for crnt_bag in disjoint_query_bags:
                if len(crnt_bag.id_set) == 0:
                    disjoint_query_bags.remove(crnt_bag)
                caught_count += len(crnt_bag.id_set)

            # add the uncaught ids into the last position
            if caught_count < self.cardinality:
                last_query_bag = QueryBag()
                last_query_bag.add_ids(range(0, self.cardinality - caught_count))
                disjoint_query_bags.append(last_query_bag)

            disjoint_query_bags_size = len(disjoint_query_bags)

            # generate the domain histogram
            self.domain_hist = [len(crnt_bag.id_set) for crnt_bag in disjoint_query_bags]
            print("domain_hist: \n", self.domain_hist)
            print("domain_hist_len: \n", len(self.domain_hist))

            # test disjoint query bags
            # for i in range(0, len(disjoint_query_bags)):
            #     crnt_bag = disjoint_query_bags[i]
            #     print("query_list= ", crnt_bag.query_list)
            #     print("id_set= ", crnt_bag.id_set)

            # initialize a matrix
            self.query_matrix = np.zeros((len(self.cond_list), disjoint_query_bags_size))
            for i in range(0, disjoint_query_bags_size):
                crnt_query_list = disjoint_query_bags[i].query_list
                for j in range(0, len(crnt_query_list)):
                    self.query_matrix[crnt_query_list[j]][i] = 1

            print("query matrix: \n", self.query_matrix)

        else:
            # for 1D and 2D histogram, just count(*)

            # get all the counts for each predicate
            self.domain_hist = self.get_cond_counts()

            # for i in range(0, len(self.domain_hist)):
            #     print(i, "\t", self.domain_hist[i])

            if self.index.__name__ in ['qw_1', 'qi_3', 'qt_1', 'qw_4', 'qi_2', 'qt_3']:  # 1D/2D histogram
                is_hist = True
            else:
                is_hist = False
                assert self.index.__name__ in ['qw_2', 'qw_3', 'qi_1', 'qi_4']  # 1D prefix

            if is_hist:
                # for histogram query
                count_row_by_predicates = sum(self.domain_hist)
            else:
                # for prefix query
                count_list = list(self.domain_hist)
                count_row_by_predicates = self.domain_hist[-1]
                for i in range(1, len(self.domain_hist)):
                    self.domain_hist[i] = count_list[i] - count_list[i - 1]
                    # print("after minus:\t", i, "\t", self.domain_hist[i])
                    assert self.domain_hist[i] >= 0

            # now the domain_hist represents non-overlapping sets
            count_remaining = self.cardinality - count_row_by_predicates
            if count_remaining > 0:
                self.domain_hist.append(count_remaining)
            self.query_matrix = np.zeros((len(self.cond_list), len(self.domain_hist)))

            if is_hist:
                for i in range(0, len(self.cond_list)):
                    self.query_matrix[i][i] = 1
            else:
                for i in range(0, len(self.cond_list)):
                    for j in range(0, i+1):
                        self.query_matrix[i][j] = 1

        # cache the results
        self.Wx_cache_W[self.query_key] = self.domain_hist
        self.Wx_cache_x[self.query_key] = self.query_matrix
        self.Wx_cache_N[self.query_key] = self.cardinality

    # return the sensitivity of matrix
    def get_sensitivity(self):
        return max([sum(a) for a in self.query_matrix])

    # to count f1 for ICQ and TCQ, max error for WCQ
    def get_accuracy(self):

        if self.query_type == Type.QueryType.WCQ:
            # print("DEBUG: max_error", max([abs(crnt_answer_diff) for crnt_answer_diff in self.answer_diff]))
            max_errpr = 1.0 - max([abs(crnt_answer_diff) for crnt_answer_diff in self.answer_diff]) / self.cardinality
            return [max_errpr, 'N/A']

        true_list = [0] * len(self.cond_list)
        pred_list = [0] * len(self.cond_list)

        c = 0
        if self.query_type == Type.QueryType.ICQ:
            c = self.icq_c
            for i in self.selected_cond_index:
                pred_list[i] = 1
            for i in range(0, len(self.cond_list)):
                if self.true_answer[i] > self.icq_c:
                    true_list[i] = 1

        elif self.query_type == Type.QueryType.TCQ:
            for i in self.selected_arg_list:
                pred_list[i] = 1

            cp_true = list(self.true_answer)
            cp_true.sort(reverse=True)
            c = cp_true[self.tcq_k - 1]

            for i in range(0, len(self.cond_list)):
                if self.true_answer[i] >= c:
                    true_list[i] = 1

        # return sum(true_list), sum(pred_list), f1_score(true_list, pred_list)
        f1 = f1_score(true_list, pred_list)


        alpha_hat = 0
        for i in range(0, len(self.cond_list)):
            if true_list[i] != pred_list[i]:
                alpha_hat = max(alpha_hat, abs(c - self.true_answer[i]))

        error = alpha_hat / self.cardinality

        return [error, f1]
