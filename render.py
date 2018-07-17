import re


class Render(object):
    def __init__(self, text, *contexts):
        """Replace variables in template with values given."""

        self.context = {}
        for context in contexts:
            self.context.update(context)

        buffered = ''

        tokens = re.split(r"(?s)({{.*?}})", text)
        for token in tokens:
            if token.startswith("{{"):
                # An expression to evaluate.
                buffered += self.context[token[2:-2].strip()]
            else:
                # Literal content, if not empty, output it.
                if token:
                    buffered += token

        self.buffered = buffered

    def render(self):
        return self.buffered
