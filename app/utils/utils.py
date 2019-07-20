from typing import (List, Dict)
from collections import namedtuple

test_data = [{"workpiece": '#W-5829-8',
              "process": '#P-3959-28',
              "machine": '#M-2304-14',
              "time": 5,
              "order": 2},
             {"workpiece": '#W-5829-8',
              "process": '#P-5852-27',
              "machine": '#M-671-13',
              "time": 11,
              "order": 1},
             {"workpiece": '#W-5829-8',
              "process": '#P-7792-26',
              "machine": '#M-8763-12',
              "time": 10,
              "order": 0},
             {"workpiece": '#W-554-9',
              "process": '#P-6810-29',
              "machine": '#M-671-13',
              "time": 5,
              "order": 0},
             {"workpiece": '#W-554-9',
              "process": '#P-8883-30',
              "machine": '#M-3836-15',
              "time": 10,
              "order": 1}]

ReshapeData = namedtuple("ReshapeData",
                         ["result", "workpiece", "machine", "process", "reverse_workpiece", "reverse_machine"])


def make_reverse_index(arr: list) -> dict:
    result = {}
    for i in range(len(arr)):
        result[arr[i]] = i
    return result


def filter_value(origin: list, except_value: int) -> list:
    return list(filter(lambda v: v != except_value, origin))


def reshape_data(data: List[Dict]) -> ReshapeData:
    def make_array(r: dict) -> ReshapeData:
        workpieces = list(set(map(lambda v: v["workpiece"], data)))
        machines = list(set(map(lambda v: v["machine"], data)))
        process = [-1 for _ in workpieces]
        reverse_workpieces = make_reverse_index(workpieces)
        reverse_machines = make_reverse_index(machines)
        ans = [-1 for _ in r.keys()]

        for key, val in r.items():
            # print(val, type(val))
            m = max(*map(lambda v: v["order"], val)) + 1 if len(val) > 1 else val[0]["order"]
            t = [-1 for _ in range(m + 1)]
            x = [-1 for _ in range(m + 1)]
            for p in val:
                t[p["order"]] = (reverse_machines[p["machine"]], p["time"])
                x[p["order"]] = p["process"]
            x = filter_value(x, -1)
            t = filter_value(t, -1)
            if ans[reverse_workpieces[key]] == -1:
                ans[reverse_workpieces[key]] = t
            else:
                ans[reverse_workpieces[key]].append(t)

            process[reverse_workpieces[key]] = x
        process = filter_value(process, -1)
        ans = filter_value(ans, -1)
        return ReshapeData(ans, workpieces, machines, process, reverse_machines, reverse_workpieces)

    result = {}
    for value in data:
        w = value["workpiece"]
        if w in result:
            result[w].append(value)
        else:
            result[w] = [value]
    # print(result)
    return make_array(result)


if __name__ == "__main__":
    print(reshape_data(test_data).result)
    print(reshape_data(test_data).machine)
