import time

from inference.events import emit_event


class ToolInterface:

    name="base_tool"
    description=""

    def execute(self,input_data):

        raise NotImplementedError()


TOOLS = {}

def list_tools():

    result=[]

    for tool in TOOLS.values():

        result.append({

            "name":getattr(tool,"name","unknown"),

            "description":getattr(tool,"description","no description"),

            "args":getattr(tool,"args",[])

        })

    return result


def register_tool(tool):

    TOOLS[tool.name]=tool


def get_tool(tool_name):

    return TOOLS.get(tool_name)


def execute_tool(tool_name,input_data=None):

    if tool_name == "list":

        return {

            "error":False,
            "tools":list_tools()

        }

    tool=get_tool(tool_name)

    if not tool:

        return {

            "error":True,
            "message":"tool not found"

        }

    try:

        result=tool.execute(input_data)

        emit_event(

            "tool_called",

            {

                "tool":tool_name,
                "args":input_data,
                "timestamp":time.time()

            }

        )

        return {

            "error":False,
            "result":result

        }

    except Exception as e:

        return {

            "error":True,
            "message":str(e)

        }


class RuntimeTool(ToolInterface):

    name="runtime"

    description="shows runtime engine status"

    args=["detail","history"]

    def execute(self,input_data):

        from inference.inference import inference_status

        return inference_status()


register_tool(RuntimeTool())
