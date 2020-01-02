import pickle

Wx_cache_W = dict()
Wx_cache_x = dict()
Wx_cache_N = dict()


def remove_cache():
    with open('Wx.pkl', 'rb') as input:
        try:
            Wx_cache_W = pickle.load(input)
            Wx_cache_x = pickle.load(input)
            Wx_cache_N = pickle.load(input)
        except (OSError, IOError, FileNotFoundError) as e:
            Wx_cache_W = dict()
            Wx_cache_x = dict()
            Wx_cache_N = dict()

    for key, value in Wx_cache_W.items():
        print(key)

    # del Wx_cache_W['qt_31001']
    # del Wx_cache_x['qt_31001']
    # del Wx_cache_N['qt_31001']

    with open('Wx.pkl', 'wb') as output:
        pickle.dump(Wx_cache_W, output, pickle.HIGHEST_PROTOCOL)
        pickle.dump(Wx_cache_x, output, pickle.HIGHEST_PROTOCOL)
        pickle.dump(Wx_cache_N, output, pickle.HIGHEST_PROTOCOL)


remove_cache()
