from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def d_3_surface_code(circ, data, mx, mz):
    # mx0
    circ.h(mx[0])
    circ.cx(mx[0], data[1])
    circ.cx(mx[0], data[0])
    circ.h(mx[0])
    circ.barrier()
    
    # mx1
    circ.h(mx[1])
    circ.cx(mx[1], data[2])
    circ.cx(mx[1], data[1])
    circ.cx(mx[1], data[5])
    circ.cx(mx[1], data[4])
    circ.h(mx[1])
    circ.barrier()
    
    # mx2
    circ.h(mx[2])
    circ.cx(mx[2], data[4])
    circ.cx(mx[2], data[3])
    circ.cx(mx[2], data[7])
    circ.cx(mx[2], data[6])
    circ.h(mx[2])
    circ.barrier()

    # mx3
    circ.h(mx[3])
    circ.cx(mx[3], data[8])
    circ.cx(mx[3], data[7])
    circ.h(mx[3])
    circ.barrier()

    # mz0
    circ.cx(data[1], mz[0])
    circ.cx(data[4], mz[0])
    circ.cx(data[0], mz[0])
    circ.cx(data[3], mz[0])
    circ.barrier()

    # mz1
    circ.cx(data[2],mz[1])
    circ.cx(data[5],mz[1])    
    circ.barrier()
    
    # mz2
    circ.cx(data[3], mz[2])
    circ.cx(data[6], mz[2])
    circ.barrier()
    
    # mz3
    circ.cx(data[5], mz[3])
    circ.cx(data[8], mz[3])
    circ.cx(data[4], mz[3])
    circ.cx(data[7], mz[3])
    circ.barrier()
    
def get_d_3_surface_code(base_circuit, data, mx, mz):
    circ = base_circuit.copy()
    d_3_surface_code(circ, data, mx, mz)
    return circ

def measurement(circ, mx, mz, c0):
    # measure all mx and mz
    circ.measure(mz[0], c0[0])
    circ.measure(mz[1], c0[1])
    circ.measure(mz[2], c0[2])
    circ.measure(mz[3], c0[3])
    circ.measure(mx[0], c0[4])
    circ.measure(mx[1], c0[5])
    circ.measure(mx[2], c0[6])
    circ.measure(mx[3], c0[7])
    circ.barrier()
    return circ

def readout_z(circ,data, c1):
    # readout logical X error.
    circ.measure(data[0], c1[0])
    circ.measure(data[1], c1[1])
    circ.measure(data[2], c1[2])
    
    return circ

def reset_m(circ, mx, mz):
    # reset all mx and mz
    circ.reset(mz[0])
    circ.reset(mz[1])
    circ.reset(mz[2])
    circ.reset(mz[3])
    circ.reset(mx[0])
    circ.reset(mx[1])
    circ.reset(mx[2])
    circ.reset(mx[3])
    circ.barrier()
    return circ

def i_gate(circ, data):
    # i gate on all data qubits
    for i in range(9):
        circ.id(data[i])
    circ.barrier()
    return circ

if __name__ == "__main__":
    # 构建码矩为3的一轮量子电路
    data = QuantumRegister(9, name='data')
    mx = QuantumRegister(4, name='mx')
    mz = QuantumRegister(4, name='mz')

    c0 = ClassicalRegister(8, name="c_m")
    c1 = ClassicalRegister(3,name="readout")

    base_circ = QuantumCircuit(data, mz, mx, c0, c1)
    
    circ = get_d_3_surface_code(base_circ, data, mx, mz)