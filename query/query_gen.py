import math


trip_amount_bound = 10.0
trip_amount_step = 0.1
# trip_amount_bound = 1000000
# trip_amount_step = 10000

trip_distance_bound = 10.0
trip_distance_step = 0.1

income_capgain_bound = 5000.0
income_capgain_step = 50.0
# income_capgain_bound = 100000
# income_capgain_step = 1000


# generate qw1, given the workload size l
def qw_1(l):
    bin_size = income_capgain_bound / l
    predicates = []
    for i in range(0, l):
        p = str(i * bin_size) + "<=capgain and capgain<" + str((i + 1) * bin_size)
        predicates.append(p)

    return predicates[:l]


# generate qw2, given the workload size l
def qw_2(l):
    bin_size = income_capgain_bound / l
    predicates = []
    for i in range(0, l):
        p = "capgain>0 and capgain<=" + str((i + 1) * bin_size)
        predicates.append(p)

    return predicates[:l]


# generate qw3, given workload size l
def qw_3(l):
    bin_size = trip_distance_bound / l
    predicates = []
    for i in range(0, l):
        p = "trip_distance<=" + str((i + 1) * bin_size)
        predicates.append(p)

    return predicates[:l]


# qw4
def qw_4(l):
    domain_passenger_count = 10
    count_total_amount = int(l / domain_passenger_count)
    total_amount_bin_size = trip_amount_bound / count_total_amount
    predicates = []

    for i in range(0, count_total_amount):
        l_total_amount = i * total_amount_bin_size
        r_total_amount = (i + 1) * total_amount_bin_size
        for j in range(0, domain_passenger_count):
            p = str(l_total_amount) + "<=total_amount and total_amount<" + str(r_total_amount) + \
                " and passenger_count=" + str(j)
            predicates.append(p)

    return predicates[:l]


# qi1
def qi_1(l):
    return qw_2(l)


# qi2
def qi_2(l):
    if l == 1:
        l = 2
    count_capgain = int(l / 2.0)  # two values on second dimension
    total_capgain_bin_size = int(income_capgain_bound / count_capgain)
    predicates = []
    for i in range(0, count_capgain):
        l_capgain = i * total_capgain_bin_size
        r_capgain = (i + 1) * total_capgain_bin_size

        p1 = str(l_capgain) + "<=capgain and capgain<" + str(r_capgain) + " and sex='Male'"
        p2 = str(l_capgain) + "<=capgain and capgain<" + str(r_capgain) + " and sex='Female'"

        predicates.append(p1)
        predicates.append(p2)

    return predicates[:l]


# qi3
def qi_3(l):
    bin_size = trip_amount_bound / l
    predicates = []
    for i in range(0, l):
        p = str(i * bin_size) + "<=fare_amount and fare_amount<" + str((i + 1) * bin_size)
        predicates.append(p)

    return predicates[:l]


# qi4
def qi_4(l):
    domain = trip_amount_bound
    bin_size = domain / l
    predicates = []
    for i in range(0, l):
        p = "total_amount<=" + str((i + 1) * bin_size)
        predicates.append(p)

    return predicates[:l]


# qt1
def qt_1(l):
    bin_size = income_capgain_bound / l
    predicates = []
    for i in range(0, l):
        # p = str(i * bin_size) + "<=capgain and age<50 and age>30 and capgain<" + str((i + 1) * bin_size)
        p = "age=" + str(i)
        predicates.append(p)

    return predicates[:l]


# qt2
def qt_2(l):
    predicates = []

    age = range(1, 101)
    workclass = ['Private', 'Self-emp-not-inc', 'Self-emp-inc', 'Federal-gov',
                 'Local-gov', 'State-gov', 'Without-pay', 'Never-worked']
    education = ['Bachelors', 'Some-college', '11th', 'HS-grad', 'Prof-school', 'Assoc-acdm', 'Assoc-voc',
                  '9th', '7th-8th', '12th', 'Masters', '1st-4th', '10th', 'Doctorate', '5th-6th', 'Preschool']
    edunum = range(1, 17)
    marital = ['Married-civ-spouse', 'Divorced', 'Never-married', 'Separated',
               'Widowed', 'Married-spouse-absent', 'Married-AF-spouse']
    occupation = ['Tech-support', 'Craft-repair', 'Other-service', 'Sales', 'Exec-managerial', 'Prof-specialty',
                  'Handlers-cleaners', 'Machine-op-inspct', 'Adm-clerical', 'Farming-fishing', 'Transport-moving',
                  'Priv-house-serv', 'Protective-serv', 'Armed-Forces']
    relationship = ['Wife', 'Own-child', 'Husband', 'Not-in-family', 'Other-relative', 'Unmarried']
    race = ['White', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other', 'Black']
    sex = ['Male', 'Female']
    capgain = frange(0, income_capgain_bound, income_capgain_step)
    caploss = range(0, 100, 1)
    hourweek = range(1, 101)
    country = ['United-States', 'Cambodia', 'England', 'Puerto-Rico', 'Canada', 'Germany', 'Outlying-US(Guam-USVI-etc)',
               'India', 'Japan', 'Greece', 'South', 'China', 'Cuba', 'Iran', 'Honduras', 'Philippines', 'Italy',
               'Poland', 'Jamaica', 'Vietnam', 'Mexico', 'Portugal', 'Ireland', 'France', 'Dominican-Republic',
               'Laos', 'Ecuador', 'Taiwan', 'Haiti', 'Columbia', 'Hungary', 'Guatemala', 'Nicaragua',
               'Scotland', 'Thailand', 'Yugoslavia', 'El-Salvador', 'Trinadad&Tobago', 'Peru',
               'Hong', 'Holand-Netherlands']

    idx = 0
    while len(predicates) < l:

        start_wl = len(predicates)

        # age
        if idx < len(age):
            p = "age=" + str(age[idx])
            predicates.append(p)

        # work class
        if idx < len(workclass):
            p = "workclass='" + str(workclass[idx]) + "'"
            predicates.append(p)

        # education
        if idx < len(education):
            p = "education='" + str(education[idx]) + "'"
            predicates.append(p)

        if idx < len(edunum):
            p = "edunum=" + str(edunum[idx])
            predicates.append(p)

        if idx < len(marital):
            p = "marital='" + str(marital[idx]) + "'"
            predicates.append(p)

        if idx < len(occupation):
            p = "occupation='" + str(occupation[idx]) + "'"
            predicates.append(p)

        if idx < len(relationship):
            p = "relationship='" + str(relationship[idx]) + "'"
            predicates.append(p)

        if idx < len(race):
            p = "race='" + str(race[idx]) + "'"
            predicates.append(p)

        if idx < len(sex):
            p = "sex='" + str(race[idx]) + "'"
            predicates.append(p)

        if idx < len(capgain):
            p = str(capgain[idx]) + "<capgain and capgain<" + str(capgain[idx + 1])
            predicates.append(p)

        if idx < len(caploss):
            p = str(caploss[idx]) + "<caploss and caploss<" + str(capgain[idx + 1])
            predicates.append(p)

        if idx < len(hourweek):
            p = "hourweek=" + str(hourweek[idx])
            predicates.append(p)

        if idx < len(country):
            p = "country='" + country[idx] + "'"
            predicates.append(p)

        end_wl = len(predicates)
        if start_wl == end_wl:
            break

        idx += 1

    return predicates[:l]


# qt3
def qt_3(l):
    
    predicates = []
    domain = 266
    count_range = int(math.sqrt(l))
    step = int(domain / count_range) + 1

    for i in range(0, count_range):
        left_pickup = 1 + i * step
        right_pickup = 1 + (i + 1) * step
        for j in range(0, count_range):
            left_dropoff = 1 + j * step
            right_dropoff = 1 + (j + 1) * step

            p = str(left_pickup) + "<=PULocationID and PULocationID<" + str(right_pickup) + " and " \
                + str(left_dropoff) + "<=DOLocationID and DOLocationID< " + str(right_dropoff)

            predicates.append(p)

    return predicates[:l]


# qt4
def qt_4(l):

    predicates = []

    pickup_date = range(1, 31)
    pickup_time = range(1, 25)
    dropoff_date = range(1, 31)
    dropoff_time = range(1, 25)

    passenger_count = range(1, 11)
    trip_distance = frange(1.0, trip_distance_bound, trip_distance_step)

    PULocationID = range(1, 266)
    DOLocationID = range(1, 266)
    fare_amount = frange(0, trip_amount_bound, trip_amount_step)
    tip_amount = frange(0, trip_amount_bound, trip_amount_step)
    tolls_amount = frange(0, trip_amount_bound, trip_amount_step)
    total_amount = frange(0, trip_amount_bound, trip_amount_step)

    idx = 0
    while len(predicates) < l:
        start_wl = len(predicates)

        if idx < len(pickup_date):
            p = "date(tpep_pickup_datetime)=" + str(pickup_date[idx])
            predicates.append(p)

        if idx < len(pickup_time):
            p = "hour(tpep_pickup_datetime)=" + str(pickup_time[idx])
            predicates.append(p)

        if idx < len(dropoff_date):
            p = "date(tpep_dropoff_datetime)=" + str(dropoff_date[idx])
            predicates.append(p)

        if idx < len(dropoff_time):
            p = "hour(tpep_dropoff_datetime)=" + str(dropoff_time[idx])
            predicates.append(p)

        if idx < len(passenger_count):
            p = "passenger_count=" + str(passenger_count[idx])
            predicates.append(p)

        if idx < len(trip_distance):
            p = str(trip_distance[idx]) + "<=trip_distance and trip_distance<" + str(trip_distance[idx + 1])
            predicates.append(p)

        if idx < len(PULocationID):
            p = "PULocationID=" + str(PULocationID[idx])
            predicates.append(p)

        if idx < len(DOLocationID):
            p = "DOLocationID=" + str(DOLocationID[idx])
            predicates.append(p)

        if idx < len(fare_amount):
            p = str(fare_amount[idx]) + "<=fare_amount and fare_amount<" + str(fare_amount[idx + 1])
            predicates.append(p)

        if idx < len(tip_amount):
            p = str(tip_amount[idx]) + "<=tip_amount and tip_amount<" + str(tip_amount[idx + 1])
            predicates.append(p)

        if idx < len(tolls_amount):
            p = str(tolls_amount[idx]) + "<=tolls_amount and tolls_amount<" + str(tolls_amount[idx + 1])
            predicates.append(p)

        if idx < len(total_amount):
            p = str(total_amount[idx]) + "<=total_amount and total_amount<" + str(total_amount[idx + 1])
            predicates.append(p)

        end_wl = len(predicates)
        if start_wl == end_wl:
            break

        idx += 1

    return predicates[:l]


def frange(x, y, jump):
    re_list = []
    while x <= y:
        re_list.append(x)
        x += jump
    return re_list

# wl = 100
# pp = gen_qt_4(wl)
# for i in range(0, wl):
#     print(pp[i])
#
# print(len(pp))