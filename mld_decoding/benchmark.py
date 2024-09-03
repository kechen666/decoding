import numpy as np
from qiskit import QuantumCircuit
from typing import Dict, List
from qiskit_aer import AerSimulator

from look_up_table import get_logical, look_up_table_all_stablizer_correct_readout, mz_mx_results, get_look_up_table_all_stablizer


class d_3_surface_code_mld_benchmark:
    def __init__(
        self,
        decoder: str,
        circ: QuantumCircuit,
        noise_model_func=None,
        correct_logical_value: int = 0,
    ):
        self.decoder = "mld"
        self.circ = circ

        self.correct_logical_value = correct_logical_value
        self.noise_model_func = noise_model_func
        self.data: Dict[str, List[float]] = {
            "physical_error_rates": [],
            "logical_error_rates": [],
        }

    def logical_error_rate_look_up_table_all(
        self, readout_strings: Dict[str, int], look_up_table: Dict[tuple,int] = None
    ) -> float:
        """
        Args:
            readout_strings: a dictionary of readout strings along with counts
            e.g. {"1 00000000":48, "1 00100000":12, ...}

            look_up_table (Optional[float]): Probability of IID data qubit X/Z flip. Defaults to None.

        Returns:
            error_rate (float): = (number of unsuccessful logical value predictions) / (total number of predictions )
        """
        total_count = 0.0
        total_errors = 0.0
        if look_up_table == None:
            raise("No look up table, can't decode.")

        for readout, count in readout_strings.items():
            total_count += count
            
            # 修改对应的输入
            list_readout = readout.split(" ")
            
            # 最开始一定全部都是0.
            syndromes_1 = list_readout[-1]
            len_stablizer = int(len(syndromes_1))
            syndromes_0 = "0"*len_stablizer
            
            # 最上面的逻辑X值
            readout_logical = get_logical(list_readout[0], 3)
            syndromes = " ".join([readout_logical, syndromes_1, syndromes_0])
            
            # 纠错之后的逻辑X值
            predicted_logical_value = look_up_table_all_stablizer_correct_readout(syndromes, look_up_table)
            
            if predicted_logical_value != self.correct_logical_value:
                total_errors += count
                
        return total_errors / total_count 

    def single(
        self, physical_error_rate: Dict[str, Dict], i_error:float, save_data: bool = True, shots: int = 2048,
    ):
        """运行单次量子纠错实验, 其中暂时只支持d=3, 最大似然法(Maximum Likelihood Decoding, ML)的实验。
        
        注意, 目前的look up table, 是根据电路运行结果, 也就是syndromes和对应逻辑算符的逻辑比特来生成的。
        因此, 运行的量子电路次数越多, 生成的look up table也越准确, 基于look up table 解码得到的逻辑错误率也越准确。
        
        参考论文：

        Args:
            physical_error_rate (Dict[str, Dict]): 用于初始化噪声模型的参数
            i_error (float): I门的噪声参数, 由于不输入surface code中, 因此单独列出来.
            save_data (bool, optional): 是否保存实验数据. Defaults to True.
            shots (int, optional): 电路运行的次数, 运行次数越多, 越准确. Defaults to 2048.

        Returns:
            float: 逻辑错误率
        """
        results = (
            AerSimulator(method = "stabilizer").run(
                self.circ,
                noise_model=self.noise_model_func(physical_error_rate, i_error),
                optimization_level=0,
                shots=shots,
            )
            .result()
            .get_counts()
        )
        
        counts_all = mz_mx_results(results, syndrome_num=8)
        look_up_table_all = get_look_up_table_all_stablizer(counts_all)
        
        logical_error_rate_value_look_table_all = self.logical_error_rate_look_up_table_all(
            results, look_up_table=look_up_table_all
        )
        
        print(f"逻辑错误率:{logical_error_rate_value_look_table_all}")
        
        print("用于模拟的噪声参数为: " + str(physical_error_rate))
        if save_data:
            self.append_data(physical_error_rate, logical_error_rate_value_look_table_all)
        return logical_error_rate_value_look_table_all

    def append_data(self, physical_error_rate: float, logical_error_rate: float):
        try:
            data = np.load(self.filename)
            physical_error_rates = data["physical_error_rates"]
            logical_error_rates = data["logical_error_rates"]
        except:
            physical_error_rates = np.array([])
            logical_error_rates = np.array([])

        physical_error_rates = np.append(physical_error_rates, physical_error_rate)
        logical_error_rates = np.append(logical_error_rates, logical_error_rate)

        indxs = np.argsort(physical_error_rates)
        np.savez(
            self.filename,
            d=self.decoder.params["d"],
            T=self.decoder.params["T"],
            physical_error_rates=physical_error_rates[indxs],
            logical_error_rates=logical_error_rates[indxs],
        )