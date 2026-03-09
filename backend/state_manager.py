def update_state(state, intent, question):

    if not state:
        state = {}

    state["intent"] = intent

    # Detect program names
    programs = ["bca", "btech", "mba", "mca"]

    for program in programs:
        if program in question.lower():
            state["program"] = program.upper()

    return state