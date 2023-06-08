init -80 python in _fom_saysomething_markdown:

    import mistune

    ## Plugins

    def spoiler(md):
        # This is a copy-paste from the source code, except it doesn't
        # add a block spoiler parser function here. And also modifies
        # the inline pattern a little (so it's Discord-like, ||spoiler||)
        INLINE_SPOILER_PATTERN = r'\|\|\s*(?P<spoiler_text>.+?)\s*\|\|'
        from mistune.plugins.spoiler import parse_inline_spoiler, render_inline_spoiler
        md.inline.register('inline_spoiler', INLINE_SPOILER_PATTERN, parse_inline_spoiler)
        if md.renderer and md.renderer.NAME == 'html':
            md.renderer.register('inline_spoiler', render_inline_spoiler)

    def subset(md):
        # Disable unnecessary syntax
        md.block.rules.remove('fenced_code')
        md.block.rules.remove('indent_code')
        md.block.rules.remove('thematic_break')
        md.block.rules.remove('block_quote')
        md.block.rules.remove('list')
        md.block.rules.remove('ref_link')
        md.block.rules.remove('raw_html')

        # Actually, heading idea *isn't that bad*, but we sure need some logic
        # in place to make the TERRIBLY LARGE lines fit inside the dialog box.
        md.block.rules.remove('axt_heading')
        md.block.rules.remove('setex_heading')

        # Disable inline syntax as well
        md.inline.rules.remove('codespan')
        md.inline.rules.remove('link')
        md.inline.rules.remove('auto_link')
        md.inline.rules.remove('auto_email')
        md.inline.rules.remove('inline_html')

    ## Renderer

    class RenPyRenderer(mistune.HTMLRenderer):
        def __init__(self):
            super(RenPyRenderer, self).__init__()

        ## Formatting

        def text(self, text): # Plain text
            return text.replace("{", "{{")

        def emphasis(self, text): # *Emphasis*
            return '{i}' + text + '{/i}'

        def strong(self, text): # **Strong**
            return '{b}' + text + '{/b}'

        def strikethrough(self, text): # ~~Strikethrough~~
            return "{s}" + text + "{/s}"

        def inline_spoiler(self, text): # ||Spoiler||
            return "{=edited}" + text + "{=normal}"

        ## HTML overrides

        def linebreak(self):
            return '\n'

        def softbreak(self):
            return '\n'

        def paragraph(self, text):
            return text

        def blank_line(self):
            return ''

        def block_text(self, text):
            return text


    ## Markdown render function

    render = mistune.create_markdown(plugins=['strikethrough', spoiler, subset],
                                     renderer=RenPyRenderer())