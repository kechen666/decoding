from itertools import product

def get_logical(readout, d):
    """根据数据比特测量值, 转换为逻辑值

    Args:
        readout (str): 对应逻辑算符的数据比特测量值
        d (int): surface code码矩

    Returns:
        str: 逻辑算符的测量值, 0或1.
    """
    if len(readout)!= d:
        raise("readout len not eq the d")
    return str(readout.count("1")%2)

def initialize_counts(syndrome_num=8):
    """初始化计数器, 用于记录syndrome的测量值和逻辑值.

    Returns:
        _type_: syndrome测量值和逻辑值的计数器
    """
    counts = {}
    # Generate all combinations of 0 and 1 for 8 syndrome values and 1 logical value
    for combination in product([0, 1], repeat = syndrome_num+1):
        counts[combination] = 0
    return counts

def mz_mx_results(results, syndrome_num=8):
    """计算测量值和逻辑值的频率, 用于构建look up table.

    Args:
        results (dict): IBM电路输出的测量值

    Returns:
        dict: syndrome测量值和逻辑值的概率分布
    """
    total_count = 0.0
    
    # Initialize counts for each combination of mx, mz values and logical states
    counts = initialize_counts(syndrome_num=syndrome_num)

    for readout, count in results.items():
        total_count += count
        
        list_readout = readout.split(" ")
        syndromes_1 = list_readout[-1]

        readout_logical = get_logical(list_readout[0], 3)
        
        # string to tuple
        stablizer_values = tuple(int(syndromes_1[i]) for i in range(8))
        logical_value = int(readout_logical)
        
        # Update the appropriate count
        counts[stablizer_values + (logical_value,)] += count

    for key, value in counts.items():
        counts[key] = value / total_count
    return counts

def get_look_up_table_all_stablizer(counts):
    """根据syndrome测量值和逻辑值的概率分布, 构建look up table.

    Args:
        counts (_type_): syndrome测量值和逻辑值的概率分布

    Returns:
        dict: look up table
    """
    look_up_table = {}
    error = 0
    for key, value in counts.items():
        stablizer = key[:8]
        logical = key[8:]
        if stablizer not in look_up_table:
            look_up_table[stablizer] = logical[0]
        elif stablizer in look_up_table:
            if value > counts[stablizer +(0,)]:
                # print(key, mz +(0,))
                # print(value, counts[mz +(0,)])
                look_up_table[stablizer] = logical[0]
                error += counts[stablizer +(0,)]
            else:
                error += value
    return look_up_table

def look_up_table_all_stablizer_correct_readout(readout, look_up_table):
    """根据look up table, 对逻辑值进行纠错.

    Args:
        readout (str): 对应测量值, 包含逻辑算符和stablizer对应的syndrome。 比如: 0 10100000, 其中第一位是逻辑值, 后面分别对应MX和MZ的syndrome测量值。
        look_up_table (dict): 用于MLD纠错的look up table

    Returns:
        int: 基于look up table 解码并且纠错之后的测量值
    """
    readout_logical = readout.split(" ")[0]
    stablizer = tuple([int(readout.split(" ")[1][i]) for i in range(8)])
    
    # print(readout_logical,stablizer)
    return (int(readout_logical)+int(look_up_table[stablizer]))%2