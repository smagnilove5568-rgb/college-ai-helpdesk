def update_state(state, intent, question):

    if not state:
        state = {}

    # store detected intent
    state["intent"] = intent

    # detect program names in the question
    programs = ["bca", "btech", "mba", "mca"]

    for program in programs:
        if program in question.lower():
            state["program"] = program.upper()

    return state