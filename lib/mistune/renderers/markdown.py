import re
from textwrap import indent
from mistune._list import render_list
from mistune.core import BaseRenderer, BlockState
from mistune.util import strip_end

fenced_re = re.compile(r'^(?:`|~)+', re.M)


class MarkdownRenderer(BaseRenderer):
    """A renderer to re-format Markdown text."""
    NAME = 'markdown'

    def __call__(self, tokens, state):
        out = self.render_tokens(tokens, state)
        # special handle for line breaks
        out += '\n\n'.join(self.render_referrences(state)) + '\n'
        return strip_end(out)

    def render_referrences(self, state):
        ref_links = state.env['ref_links']
        for key in ref_links:
            attrs = ref_links[key]
            text = '[' + attrs['label'] + ']: ' + attrs['url']
            title = attrs.get('title')
            if title:
                text += ' "' + title + '"'
            yield text

    def render_children(self, token, state):
        children = token['children']
        return self.render_tokens(children, state)

    def text(self, token, state):
        return token['raw']

    def emphasis(self, token, state):
        return '*' + self.render_children(token, state) + '*'

    def strong(self, token, state):
        return '**' + self.render_children(token, state) + '**'

    def link(self, token, state):
        label = token.get('label')
        text = self.render_children(token, state)
        out = '[' + text + ']'
        if label:
            return out + '[' + label + ']'

        attrs = token['attrs']
        url = attrs['url']
        title = attrs.get('title')
        if text == url and not title:
            return '<' + text + '>'
        elif 'mailto:' + text == url and not title:
            return '<' + text + '>'

        out += '('
        if '(' in url or ')' in url:
            out += '<' + url + '>'
        else:
            out += url
        if title:
            out += ' "' + title + '"'
        return out + ')'

    def image(self, token, state):
        return '!' + self.link(token, state)

    def codespan(self, token, state):
        return '`' + token['raw'] + '`'

    def linebreak(self, token, state):
        return '  \n'

    def softbreak(self, token, state):
        return '\n'

    def blank_line(self, token, state):
        return ''

    def inline_html(self, token, state):
        return token['raw']

    def paragraph(self, token, state):
        text = self.render_children(token, state)
        return text + '\n\n'

    def heading(self, token, state):
        level = token['attrs']['level']
        marker = '#' * level
        text = self.render_children(token, state)
        return marker + ' ' + text + '\n\n'

    def thematic_break(self, token, state):
        return '***\n\n'

    def block_text(self, token, state):
        return self.render_children(token, state) + '\n'

    def block_code(self, token, state):
        attrs = token.get('attrs', {})
        info = attrs.get('info', '')
        code = token['raw']
        if code and code[-1] != '\n':
            code += '\n'

        marker = token.get('marker')
        if not marker:
            marker = _get_fenced_marker(code)
        return marker + info + '\n' + code + marker + '\n\n'

    def block_quote(self, token, state):
        text = indent(self.render_children(token, state), '> ')
        return text + '\n\n'

    def block_html(self, token, state):
        return token['raw'] + '\n\n'

    def block_error(self, token, state):
        return ''

    def list(self, token, state):
        return render_list(self, token, state)


def _get_fenced_marker(code):
    found = fenced_re.findall(code)
    if not found:
        return '```'

    ticks = []  # `
    waves = []  # ~
    for s in found:
        if s[0] == '`':
            ticks.append(len(s))
        else:
            waves.append(len(s))

    if not ticks:
        return '```'

    if not waves:
        return '~~~'
    return '`' * (max(ticks) + 1)
