import sys
sys.path.append('../')

from query import Query
from query import Type
from query.Type import mechanism_name_dict, wcq_mechanisms, icq_mechanisms, tcq_mechanisms
from privacy import PrivacyEngine
from query.query_gen import *


repeat_times = 1

census_card = 32561

default_workload_size = 100
default_icq_c_ratio = 0.1
default_census_icq_c = default_icq_c_ratio * census_card

default_topk = 10
alpha_ratio = 0.02
alpha_census = alpha_ratio * census_card

global_foo = 'N/A'


def analysis_results(re_list):

    print("data,sf,query_type,q_idx,wl,alpha/N,est_cost,real_cost,error,f1,"
          "icq_c,mpm_p,real_poking,"
          "top_k")

    for crnt_run in re_list:

        table_name = crnt_run.query.table_name
        data_size = crnt_run.query.data_size
        m_type = crnt_run.query.m_type
        q_idx = crnt_run.query.index
        query_len = len(crnt_run.query.cond_list)
        alpha = crnt_run.alpha

        data_card = crnt_run.query.cardinality

        acc_list = crnt_run.query.get_accuracy()

        print(table_name.split(".", 1)[0], data_size, mechanism_name_dict[m_type],
              str(q_idx.__name__).replace("_", "").upper(), query_len,
              "{0:.4f}".format(alpha / data_card), crnt_run.est_cost, crnt_run.real_cost,
              acc_list[0], acc_list[1], sep=',', end=',')

        crnt_q_type = crnt_run.query.query_type

        if crnt_q_type == Type.QueryType.WCQ:
            #
            print("N/A,N/A,N/A,N/A")

        elif crnt_q_type == Type.QueryType.ICQ:

            print(global_foo,
                  crnt_run.query.count_poking,
                  crnt_run.query.real_count_poking,
                  # sum(crnt_run.query.real_count_poking),
                  "N/A", sep=',')

        elif crnt_q_type == Type.QueryType.TCQ:

            print("N/A,N/A,N/A", crnt_run.query.tcq_k, sep=',')


'''       
Function to run a single query

data_set: string of data set, e.g., census
q_idx: string of the query
wl: workload
query_type: WCQ, ICQ, or TCQ
icq_threshold: threshold for ICQ
mpm_poking: poking times for mpm
tcq_k: top k for TCQ
m_type: mechanism to use
dsize: database size
alpha, beta: accuracy parameters
'''


def run_query(data_set, q_idx, wl, query_type, m_type,
              icq_c=-1, mpm_poking=10, tcq_k=-1,
              dsize=1, alpha=0.1, beta=0.0005, budget=float('inf')):

    run_list = []

    pe = PrivacyEngine.PrivacyEngine(budget, data_set)

    cond_list = q_idx(wl)

    print("DEBUG: cond_list", cond_list)
    if len(cond_list) == 0:  # file not exist
        print("ERROR: query not found ", q_idx)
        return

    for i in range(0, repeat_times):
        crnt_q = Query.Query()

        crnt_q.set_index(q_idx)
        crnt_q.set_cond_list(cond_list)
        crnt_q.set_data_and_size(data_set, dsize)
        crnt_q.set_query_type(query_type, icq_c, mpm_poking, tcq_k)
        crnt_q.set_mechanism_type(m_type)

        re_m = pe.run_query(crnt_q, alpha, beta)
        if re_m.return_msg == Type.ReturnMsgType.QD:
            print("ERROR: ", re_m.return_msg)
            break

        run_list.append(re_m)

    # return the run list for analysis
    return run_list


re = run_query("census", qw_1, 100, Type.QueryType.WCQ, Type.MechanismType.LM, alpha=0.02*32561)
analysis_results(re)

