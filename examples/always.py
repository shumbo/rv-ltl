import random
from rv_ltl import Always, Atomic, B4


def attempt():
    return random.choice([True] * 100 + [False] * 2)


count = 0
lst = None
while True:
    count += 1
    lst = []
    ap1 = Atomic()
    phi = Always(ap1)
    b = None
    for i in range(300):
        n = attempt()
        lst.append(n)
        phi.update({ap1: n})
        b = phi.evaluate()
        if b == B4.FALSE:
            break
    if b.is_truthy:
        break

print(count)
