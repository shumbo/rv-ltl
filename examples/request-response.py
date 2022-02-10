import random
from rv_ltl.b4 import B4
from rv_ltl.core import Always, Atomic, Eventually, Implies

random.seed(30)


def attempt():
    return random.choice([True] * 1 + [False] * 99)


count = 0
lst = None
while True:
    count += 1
    lst = []
    request = Atomic("request")
    response = Atomic("request")
    phi = Always(Implies(request, Eventually(response)))
    b = None
    for i in range(300):
        t = (attempt(), attempt())
        lst.append(t)
        phi.update({request: t[0], response: t[1]})
        b = phi.evaluate()
        if b == B4.FALSE:
            break
    if b.is_truthy:
        break

print(count)
