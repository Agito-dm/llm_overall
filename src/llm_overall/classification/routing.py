from llm_overall.classification.categories import Category

ROUTING_INSTRUCTIONS: dict[Category, str] = {
    Category.SUPPORT: (
        "Provide structured technical assistance in Russian. "
        "Explain the likely cause, give numbered troubleshooting "
        "steps, and suggest how to verify the solution. "
        "Do not invent technical details."
    ),
    Category.FEEDBACK: (
        "Respond politely in Russian. "
        "Acknowledge the user's feedback, thank them for "
        "sharing it, and address any specific suggestions. "
        "Do not promise changes that are not confirmed."
    ),
    Category.COMPLAINT: (
        "Respond with empathy and professionalism in Russian. "
        "Acknowledge the problem without blaming the user. "
        "Suggest a realistic next step or resolution. "
        "Do not promise refunds or outcomes without evidence."
    ),
    Category.SALES: (
        "Provide a concise and helpful sales-oriented response "
        "in Russian. Focus on the user's needs, explain relevant "
        "benefits, and suggest a reasonable next step. "
        "Avoid aggressive persuasion and invented offers."
    ),
    Category.GENERAL_QUESTION: (
        "Answer the user's question clearly in Russian. "
        "Explain important concepts with simple examples "
        "when helpful. Be factual and avoid unnecessary detail."
    ),
}


def get_route(category: Category) -> str:
    try:
        return ROUTING_INSTRUCTIONS[category]
    except KeyError as exc:
        raise ValueError(f"Unknown routing category: {category}") from exc
