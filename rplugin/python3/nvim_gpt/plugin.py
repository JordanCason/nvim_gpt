from collections import deque
from datetime import datetime
from functools import lru_cache
import re
import os
import toml
from .parser import CommentParser

import openai

import pynvim
import requests
import json

@pynvim.plugin
class GPTChatPlugin(object):
    def __init__(self, nvim):
        # load the config
        # move out of init and build config on first call
        nvim_config_path = nvim.eval("stdpath('config')")
        config_file_path = os.path.join(nvim_config_path, "nvimgpt/config.toml")
        config = toml.load(config_file_path)

        self.nvim = nvim

        openai.api_key = config["openai_api_key"]
        self.chat_model = config["chat_model"]
        self.prompt = config["prompt"]
        self.messages_queue = deque(maxlen=12)

    @lru_cache(maxsize=518)
    def chat(self, message: str) -> str:
        self.messages_queue.append({"role": "user", "content": message})
        try:
            prompty = {
                "role": "user",
                "content": f"{self.prompt} Today is {datetime.now(): %A %d %B %Y %H:%M}",
            }
            response = openai.ChatCompletion.create(
                model=self.chat_model,
                messages=[prompty, *self.messages_queue],
                stream=True,
            )
        except openai.error.RateLimitError:
            reply = "to many requests."
        return response


    def get_visual_selection(self):
        (row1, col1) = self.nvim.eval("getpos(\"'<\")[1:2]")
        (row2, col2) = self.nvim.eval("getpos(\"'>\")[1:2]")
        lines = self.nvim.api.buf_get_lines(self.nvim.api.get_current_buf(), row1 - 1, row2, True)
        if len(lines) == 1:
            selected_text = lines[0][col1-1:col2-1]
        else:
            if col1 == 1:
                selected_text = lines[0] + "\n"
            else:
                selected_text = lines[0][col1-1:] + "\n"
            for line in lines[1:-1]:
                selected_text += line + "\n"
            selected_text += lines[-1][:col2-1]
        return selected_text

    def get_filetype(self):
        return self.nvim.eval('&filetype')

    def open_virtical_buffer(self):
        # Open a new vertical window in the current console on the left
        buf = self.nvim.api.create_buf(False, True)
        buf_num = self.nvim.api.buf_get_number(buf)

        self.nvim.api.buf_set_name(buf, f"chatbuffer{buf_num}")
        self.nvim.command('vnew | b {}'.format(buf_num))
        self.nvim.command("wincmd L")
        self.nvim.command('redraw')
        return buf

    @pynvim.function('NewGPTBuffer')
    def gpt_chat(self, args):
        buf_name = self.nvim.current.buffer.name
        selected_text = self.get_visual_selection()
        if "chatbuffer" in buf_name.split("/")[-1]:
            self.nvim.current.buffer.append("")
            self.nvim.current.buffer.append("")
            self.make_request(selected_text)
            return

        current_filetype = self.get_filetype()

        self.vertical_buffer = self.open_virtical_buffer()

        self.parser = CommentParser(current_filetype, self.vertical_buffer, self.nvim)

        initial_prompt = selected_text.split("\n")
        for line in initial_prompt:
            self.vertical_buffer.append(line)
            self.nvim.command('redraw')

        self.nvim.command(f'setlocal filetype={current_filetype}')
        self.nvim.command('setlocal buftype=nofile')

        self.vertical_buffer.append('')
        self.vertical_buffer.append('')
        self.nvim.command('redraw')
        self.make_request(selected_text)
        self.nvim.command('redraw')

        # file_path = "/home/jordan/.config/nvim/rplugin/python3/chats.txt"
        # save_buffer_cmd = f"autocmd BufDelete <buffer> call py3 GPTChatPlugin().save_buffer_to_file('{file_path}')"
        # self.nvim.command(save_buffer_cmd)

    def make_request(self, text):
        collected_messages = []
        for chunk in self.chat(text):
            if "content" in chunk['choices'][0]['delta']:
                chunk_message = chunk['choices'][0]['delta'].content
                collected_messages.append(chunk_message)
                self.parser.process_token(chunk_message)
                self.scroll_buffer()

        full_reply_content = ''.join(collected_messages)
        self.messages_queue.append({"role": "assistant", "content": full_reply_content})

    def scroll_buffer(self):
        self.nvim.command("normal! \<Esc>")
        self.nvim.command("normal! G")
        self.nvim.command("normal! zz")

    def save_buffer_to_file(self, file_path):
        buffer_content = "\n".join(self.nvim.current.buffer)
        with open(file_path, "w") as f:
            f.write(buffer_content)
