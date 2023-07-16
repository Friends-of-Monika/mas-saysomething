from textwrap import indent
from mistune._list import render_list
from mistune.core import BaseRenderer, BlockState
from mistune.util import strip_end


class RSTRenderer(BaseRenderer):
    """A renderer for converting Markdown to ReST."""
    NAME = 'rst'

    #: marker symbols for heading
    HEADING_MARKERS = {
      1: '=',
      2: '-',
      3: '~',
      4: '^',
      5: '"',
      6: "'",
    }
    INLINE_IMAGE_PREFIX = 'img-'

    def iter_tokens(self, tokens, state):
        prev = None
        for tok in tokens:
            # ignore blank line
            if tok['type'] == 'blank_line':
                continue
            tok['prev'] = prev
            prev = tok
            yield self.render_token(tok, state)

    def __call__(self, tokens, state):
        state.env['inline_images'] = []
        out = self.render_tokens(tokens, state)
        # special handle for line breaks
        out += '\n\n'.join(self.render_referrences(state)) + '\n'
        return strip_end(out)

    def render_referrences(self, state):
        images = state.env['inline_images']
        for index, token in enumerate(images):
            attrs = token['attrs']
            alt = self.render_children(token, state)
            ident = self.INLINE_IMAGE_PREFIX + str(index)
            yield '.. |' + ident + '| image:: ' + attrs['url'] + '\n   :alt: ' + alt

    def render_children(self, token, state):
        children = token['children']
        return self.render_tokens(children, state)

    def text(self, token, state):
        text = token['raw']
        return text.replace('|', r'\|')

    def emphasis(self, token, state):
        return '*' + self.render_children(token, state) + '*'

    def strong(self, token, state):
        return '**' + self.render_children(token, state) + '**'

    def link(self, token, state):
        attrs = token['attrs']
        text = self.render_children(token, state)
        return '`' + text + ' <' + attrs['url'] + '>`__'

    def image(self, token, state):
        refs = state.env['inline_images']
        index = len(refs)
        refs.append(token)
        return '|' + self.INLINE_IMAGE_PREFIX + str(index) + '|'

    def codespan(self, token, state):
        return '``' + token['raw'] + '``'

    def linebreak(self, token, state):
        return '<linebreak>'

    def softbreak(self, token, state):
        return ' '

    def inline_html(self, token, state):
        # rst does not support inline html
        return ''

    def paragraph(self, token, state):
        children = token['children']
        if len(children) == 1 and children[0]['type'] == 'image':
            image = children[0]
            attrs = image['attrs']
            title = attrs.get('title')
            alt = self.render_children(image, state)
            text = '.. figure:: ' + attrs['url']
            if title:
                text += '\n   :alt: ' + title
            text += '\n\n' + indent(alt, '   ')
        else:
            text = self.render_tokens(children, state)
            lines = text.split('<linebreak>')
            if len(lines) > 1:
                text = '\n'.join('| ' + line for line in lines)
        return text + '\n\n'

    def heading(self, token, state):
        attrs = token['attrs']
        text = self.render_children(token, state)
        marker = self.HEADING_MARKERS[attrs['level']]
        return text + '\n' + marker * len(text) + '\n\n'

    def thematic_break(self, token, state):
        return '--------------\n\n'

    def block_text(self, token, state):
        return self.render_children(token, state) + '\n'

    def block_code(self, token, state):
        attrs = token.get('attrs', {})
        info = attrs.get('info')
        code = indent(token['raw'], '   ')
        if info:
            lang = info.split()[0]
            return '.. code:: ' + lang + '\n\n' + code + '\n'
        else:
            return '::\n\n' + code + '\n\n'

    def block_quote(self, token, state):
        text = indent(self.render_children(token, state), '   ')
        prev = token['prev']
        ignore_blocks = (
            'paragraph',
            'thematic_break',
            'linebreak',
            'heading',
        )
        if prev and prev['type'] not in ignore_blocks:
            text = '..\n\n' + text
        return text

    def block_html(self, token, state):
        raw = token['raw']
        return '.. raw:: html\n\n' + indent(raw, '   ') + '\n\n'

    def block_error(self, token, state):
        return ''

    def list(self, token, state):
        return render_list(self, token, state)
