class JarvisTool:

    def __init__(self,name):

        self.name = name


    def execute(self,data):

        return {

            "error": True,

            "message": "tool not implemented"

        }


    def health(self):

        return "unknown"
