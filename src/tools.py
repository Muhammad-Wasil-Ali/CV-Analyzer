# Actual Python functions
def get_job_trends(skill: str) -> dict:
    """Fake job market data - real project mein API call hogi"""
    trends = {
        "React": {"demand": "high", "avg_salary": "$80k", "top_companies": ["Meta", "Airbnb", "Netflix"]},
        "FastAPI": {"demand": "high", "avg_salary": "$90k", "top_companies": ["Uber", "Microsoft"]},
        "Docker": {"demand": "very high", "avg_salary": "$95k", "top_companies": ["Google", "Amazon"]},
        "PostgreSQL": {"demand": "medium", "avg_salary": "$75k", "top_companies": ["Stripe", "Shopify"]},
    }
    # Agar skill dict mein nahi toh default return karo
    return trends.get(skill, {"demand": "medium", "avg_salary": "$70k", "top_companies": []})


def execute_tool(tool_name: str, tool_args: dict) -> str:
    """LLM jo tool call kare usse yahan execute karte hain"""
    if tool_name == "get_job_trends":
        result = get_job_trends(tool_args["skill"])
        return str(result)
    return "Tool not found"


# LLM ko batana ke kaunse tools available hain
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_job_trends",
            "description": "Get current job market demand and salary trends for a specific skill",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill": {
                        "type": "string",
                        "description": "The skill to get job trends for e.g. React, Docker, Python"
                    }
                },
                "required": ["skill"]
            }
        }
    }
]