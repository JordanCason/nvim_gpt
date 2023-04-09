# nvim_gpt

## Introduction

The GPT plugin for Neovim, which was quickly put together, offers a convenient way to interact with the AI model through a vertical buffer. You can effectively allows for streamlined and accessible AI access within your Neovim workspace. Please note that there may be many bugs, fixes, and improvements needed, and any contributions are highly appreciated.

## Installation

If you use vim-plug, add the plugin to your Neovim configuration file:
```
call plug#begin()
Plug 'numirias/semshi', { 'do': ':UpdateRemotePlugins' }
call plug#end()
```

If you don't use vim-plug, make sure to call UpdateRemotePlugins:
```
:UpdateRemotePlugins
```

Create a config:
```
~/.config/nvim/nvimgpt/config.toml
```
There is an example config in the src code.

## Usage
Add the following to your .vimrc or init.vim to enable visual selection and pressing Enter to open the GPT buffer:
```
vnoremap <silent> <expr> <CR> ':<C-u>call NewGPTBuffer()<CR>'
```

## Contributing

If you find this project useful and come across any bugs or issues, feel free to contribute. Here's how you can do it:

 - Fork the repository.
 - Create a new branch for your changes.
 - Make your changes and commit them to your branch.
 - Push your branch to your fork.
 - Create a pull request from your fork's branch to the main repository.

