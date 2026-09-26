from typing import Any

def build_agent_prompt(goal:str,tools:list[dict[str,Any]],history:dict[str,Any])->str:
    tool_description = ""
    for tool in tools:
        tool_description+=f"""
TOOL NAME:
{tool["NAME"]}
DESCRIPTION:
{tool["Description"]}
PARAMETERS:
{tool["parameters"]}"""
        execution_history=""
        for message in history:
            execution_history+=f"""
ROLE: {message.get("role")}
TOOL:{message.get("tool","")}
CONTENT:{message.get("content")}
"""
            return f"""
You are document analysis agent
your goal is :
{goal}
You have access to the following tools
{tool_description}
Previous execution history
{execution_history}
You must decide what to do next.
If you need information from a tool, return ONLY valid JSON
using this format:
{{
    "action": "tool_name",
    "arguments": {{
        "argument_name": "argument_value"
    }}
}}
If you have enough information to answer the user's goal, return:

{{
    "action": "final_answer",
    "arguments": {{}},
    "final_answer": "your final answer"
}}
Rules:

1. Only use the tools provided above.
2. Never invent a tool.
3. Never invent tool arguments.
4. Use information returned by tools.
5. Do not use outside knowledge when answering document questions.
6. If the available information is insufficient, clearly say so.
7. Return ONLY valid JSON.
8. Do not include Markdown code fences.
9. Do not include explanations outside the JSON object.
""".strip()