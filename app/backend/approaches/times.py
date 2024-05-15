gpt_4_turbo_times = [
    (4.908212661743164, 10.351208925247192),
    (3.1006109714508057, 7.84944224357605),
    (3.292912483215332, 8.236476421356201),
    (2.962204933166504, 8.381002426147461),
    (4.171103000640869, 7.224525690078735),
]

# print min, max, average of first time in tuple
print("gpt-4-turbo")
print("min", min([x[0] for x in gpt_4_turbo_times]))
print("max", max([x[0] for x in gpt_4_turbo_times]))
print("avg", sum([x[0] for x in gpt_4_turbo_times]) / len(gpt_4_turbo_times))


gpt_4o_times = [
    (2.528897523880005, 3.6543009281158447),
    (3.1480963230133057, 4.39872670173645),
    (2.2817306518554688, 3.357989072799682),
    (3.386105537414551, 4.526637315750122),
    (2.673431634902954, 3.4933059215545654),
]

# print min, max, average of first time in tuple
print("gpt-4o")
print("min", min([x[0] for x in gpt_4o_times]))
print("max", max([x[0] for x in gpt_4o_times]))
print("avg", sum([x[0] for x in gpt_4o_times]) / len(gpt_4o_times))
