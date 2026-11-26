from random import Random


def work_orders():
    rng = Random(1088)
    for _ in range(140):
        minutes = rng.randint(10,360)
        mass = round(rng.uniform(.1,40),2)
        stones = rng.randint(0,8)
        backlog = rng.randint(0,24)
        turnaround = 1 + .021 * minutes + .057 * mass + .19 * stones + .25 * backlog
        hours = max(1.0, turnaround + rng.triangular(-2,5,.5) * (1+.02*backlog))
        yield minutes,mass,stones,backlog,round(hours,3)
