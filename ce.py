from typing import Any
from claripy import *

class SquBV:
    def __init__(self) -> None:
        self.bv: ast.BV
        self.value: int # 无论是BVV还是BVS都被赋予了一个fuzz过程中的具体值 便于分支探索 而BVS用于最后的路径求解

    @property
    def symbolic(self) -> bool:
        return self.bv.symbolic
        
    @property
    def concrete(self) -> bool:
        return self.bv.concrete
    
    @property
    def concrete_value(self) -> Any:
        return self.concrete_value

class SquBVS(SquBV):
    def __init__(self, name: str, value: int, size: int) -> None:
        super().__init__()
        self.bv = BVS(name, size)
        self.value = value
    
class SquBVV(SquBV):
    def __init__(self, value: str, size: int) -> None:
        super().__init__()
        self.bv = BVV(value, size)
        self.value = value

import random

a = SquBVV(5, 256)
b = SquBVV(10, 256)

solver = Solver()

fuzz_value = random.randint(0, 20)
s = SquBVS("s", fuzz_value, 256)

branch_is_interesting = [False, False, True, True]

while True:

    if a.value < s.value: # 实际二进制程序中的约束 与具体值的比较 不过不同的是我们需要对其中的可能被符号化的值进行约束计算
        # not interesting
        solver.add(a.bv >= s.bv)
        print("here alreadly reached")

    elif b.value < s.value: # 实际二进制程序中的约束 与具体值的比较 不过不同的是我们需要对其中的可能被符号化的值进行约束计算
        # not interesting
        solver.add(b.bv >= s.bv)
        print("here alreadly reached")

    else:

        if not solver.satisfiable():
            raise UnsatError()
        
        # 如果想进入分支 就需要提前设置约束条件 
        # 但是不想进入的话 就进入后设置相反的约束
        solver.add(a.bv * s.bv == b.bv)
         
        if a.value * s.value == b.value:

            # here is unreached
            solver.simplify()
            
            if solver.satisfiable() and s.symbolic:
                print(solver.eval(s.bv, 1)[0])
                break
            else:
                raise UnsatError("unsat")

    if solver.satisfiable():
        concolic_value = solver.eval(s.bv, 1)[0]
        s.value = concolic_value
    else:
        raise UnsatError()

