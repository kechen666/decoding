import itertools
import random

from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error


def get_physical_error_rate(num_qubits=17, cnot_error = 0.01, h_error = 0.001)->dict:
    """生成物理噪声模型所需的参数, 包括CNOT门和Hadamard门对应的错误率。
        其中, 暂时假设所以CNOT门和H门的参数一致。

    Args:
        num_qubits (int): 量子比特数
        cnot_error (float): CNOT门的去极化参数
        h_error (float): Hadamard门的去极化参数

    Returns:
        Dict: 物理噪声模型所需的参数
    """
    physical_error_rate = {}
    cnot_depolarizing_error_physical = {}
    h_depolarizing_error_physical = {}

    # cnot gate with depolarizing error
    for key in list(itertools.combinations(range(num_qubits),2)):
        inv_key = (key[1], key[0])
        value = cnot_error
        
        cnot_depolarizing_error_physical[key] = value
        cnot_depolarizing_error_physical[inv_key] = value
    
    # h gate with depolarizing error
    for key in range(num_qubits):
        key = (key,)
        value = h_error
        h_depolarizing_error_physical[key] = value

    physical_error_rate['cx'] = cnot_depolarizing_error_physical
    physical_error_rate['h'] = h_depolarizing_error_physical
    return physical_error_rate

def get_noise_model(physical_error_rate, i_error):
    """构建噪声模型

    Args:
        physical_error_rate (dict): 用于噪声模型设置的物理参数
        i_error (float): I门对应的错误率

    Returns:
        _type_: _description_
    """
    noise_model = NoiseModel()
    for gate_name, depolarizing_error_physical in physical_error_rate.items():
    # 生成随机的噪声模型
        if gate_name == "cx":
            for qubit_pairs, dep_param in depolarizing_error_physical.items():
                dep_error = depolarizing_error(dep_param, 2)
                noise_model.add_quantum_error(dep_error, ['cx'], qubit_pairs)
        elif gate_name == "h":
            for qubit, dep_param in depolarizing_error_physical.items():
                dep_error = depolarizing_error(dep_param, 1)
                noise_model.add_quantum_error(dep_error, ['h'], qubit)
    # 添加I门的错误率，因为I门不作为Surface code中的门，单独列出来。
    error_gate = depolarizing_error(i_error, 1)
    noise_model.add_all_qubit_quantum_error(error_gate, "id")
    return noise_model