"SPrint print buffered alternative"

# =====================================================================
# SPrint framework
# =====================================================================
import textwrap


class SPrint:
    "An alternative to print"

    def __init__(self):
        self.list = []

    def __call__(self, *args):
        "Append to buffer when called, to mimic print behavior"
        self.add(*args)

    def add(self, *args):
        "Append to buffer"
        for line in args:
            self.list.append(str(line))

    @property
    def text(self):
        "Return the currently buffered text"
        return "\n".join(self.list)

    def render(self, stdout=True, var=True, indent=None):
        "Render the print buffer"

        text = self.text
        if indent:
            text = textwrap.indent(text, indent)

        if stdout:
            print(text)

        if var:
            return text

        return None
