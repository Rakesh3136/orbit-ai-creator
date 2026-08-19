from orbit.models import Script


def demo_script() -> Script:
    return Script(
        title="Why the Internet Keeps Getting More Expensive to Run",
        hook=(
            "The internet feels invisible, but behind every tap is a physical machine, a network, and a growing energy bill. "
            "The surprising part is how much of that infrastructure is still expanding."
        ),
        body=(
            "A modern online service depends on data centers, networking equipment, storage, cooling, and power systems.\n\n"
            "As software becomes more computationally demanding, operators have to add more capacity while keeping latency low and reliability high.\n\n"
            "That creates a simple tension: the digital world feels weightless to the user, but its underlying infrastructure is physical, capital-intensive, and constantly being rebuilt.\n\n"
            "For viewers, the useful question is not whether the internet is getting expensive in one single way. It is which part of the stack is absorbing the next wave of demand."
        ),
        conclusion=(
            "The next time an online service feels instant, remember that the experience is sitting on top of a very real machine economy. "
            "That physical layer is where the future of the internet is often decided."
        ),
    )
