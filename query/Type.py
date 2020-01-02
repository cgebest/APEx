from enum import Enum


class QueryType(Enum):
    """enum type for different query type"""
    WCQ = 1
    ICQ = 2
    TCQ = 3


class MechanismType(Enum):
    """enum type for different mechanism"""
    LM = 10
    LM_SM = 11
    LCM = 20
    LCM_SM = 21
    LCM_OM = 22
    LCM_MP = 23
    LCT = 30
    LCT_NM = 31


class ReturnMsgType(Enum):
    QD = 'Denied lack of budget'
    SUCCESS = 'Success'


mechanism_name_dict = {MechanismType.LM: 'WCQ-LM',
                       MechanismType.LM_SM: 'WCQ-SM',
                       MechanismType.LCM: 'ICQ-LM',
                       MechanismType.LCM_SM: 'ICQ-SM',
                       MechanismType.LCM_OM: 'ICQ-OM',
                       MechanismType.LCM_MP: 'ICQ-MPM',
                       MechanismType.LCT: 'TCQ-LM',
                       MechanismType.LCT_NM: 'TCQ-TM'
                       }

wcq_mechanisms = [MechanismType.LM, MechanismType.LM_SM]
icq_mechanisms = [MechanismType.LCM, MechanismType.LCM_SM, MechanismType.LCM_MP]
tcq_mechanisms = [MechanismType.LCT, MechanismType.LCT_NM]