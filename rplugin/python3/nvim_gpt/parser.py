import re
import pynvim

class CommentParser:
    def __init__(self, language, buffer, nvim):
        self.nvim = nvim
        self.language = language
        self.lang_delimiters = {
            "python": ('"""', '"""'),
            "rust": ('/*!', '*/'),
            # Add more languages and their delimiters here
        }
        if language not in self.lang_delimiters:
            raise ValueError(f"Unsupported language: {language}, but you can add it to the CommentParser Class")

        self.start_delimiter, self.end_delimiter = self.lang_delimiters[language]
        self.start_code_block = False
        self.output = buffer
        self.output[0] = self.start_delimiter
        self.cache = []

        self.nvim.command('redraw')

    def clear_cache(self, delimiter):
        lines = "".join(self.cache).replace("```", delimiter).split("\n")
        self.output[-1] += lines[0]
        lines.pop(0)
        for line in lines:
            self.output.append(line)
            self.nvim.command('redraw')
        self.cache = []
        self.nvim.command('redraw')

    def process_token(self, token):
        clear=True
        self.cache.append(token)
        temp = "".join(self.cache)
        if "`" in temp:
            clear=False
            if re.search("`.+[\x00-\x7F]`", temp):
                clear=True

        if temp[-1] == "\n":
            clear=False

        if not clear:
            if re.search("```.*\n[\x00-\x7F]", temp, re.DOTALL):
                self.cache = ["".join(self.cache).replace(self.language, "")]
                self.start_code_block = not self.start_code_block
                clear=True

        if clear:
            if self.start_code_block:
                self.clear_cache(self.end_delimiter)
            if not self.start_code_block:
                self.clear_cache(self.start_delimiter)
