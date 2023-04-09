" Script Info  {{{
"=============================================================================
"      Licence: The MIT Licence (see LICENCE file)
" Name Of File: nvim_gpt.py
"  Description: The GPT plugin for Neovim offers a convenient way to interact with the AI model through a vertical buffer. Although implementing a fast browser in a console-based vertical buffer has been challenging, the GPT-based solution effectively allows for streamlined and accessible AI assistance within your Neovim workspace.
"   Maintainer: Jordan Cason
"      Version: 0.0.1
"        Usage: 
"
"=============================================================================
" }}}

if !has('python3')
    echomsg ':python3 is not available, vim-find-test will not be loaded.'
    finish
endif
