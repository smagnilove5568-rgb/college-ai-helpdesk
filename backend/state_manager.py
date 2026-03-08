def update_state(state: dict, question: str):

    question = question.lower()

    programs = ["bca", "b.tech", "mba", "mca"]

    for program in programs:
        if program in question:
            state["program"] = program.upper()

    if "admission" in question:
        state["intent"] = "admission"

    if "fee" in question:
        state["intent"] = "fees"

    return state