command! -nargs=* -complete=dir Search call Search(<f-args>) 
command! -nargs=* SaveSearch call SaveSearch(<f-args>) 

nnoremap ft :Search <C-R>=expand("<cword>")<CR><CR>
vnoremap ft "ay:call Search(@a)<CR>
nnoremap fd :let _func=expand("<cword>")\|call Search(_func,"n","","", "def " .  _func . "\\(\|class " . _func . "\\(" )<CR>
nnoremap fu :let _func=expand("<cword>")\|call Search(_func,"n","","", "[^a-zA-Z]" .  _func . "\\(" )<CR>
nnoremap ff :Search <C-R>=expand("<cword>")<CR> f<c-left><left>
"nnoremap cs :Search <C-R>=expand("<cword>")<CR> n<c-b><c-right><c-right>
nnoremap fc :call Search('<C-R>=expand("<cword>")<CR>' ,'n','<C-R>=expand("%:e")<CR>','<C-R>=expand("%:p:h")<CR>')<home><c-right><c-right><left>
nnoremap fa :call Search('<C-R>=expand("<cword>")<CR>' ,'n','<C-R>=expand("%:e")<CR>')<home><c-right><c-right><left>
nnoremap fo :call Search('<C-R>=expand("<cword>")<CR>' ,'or','<C-R>=expand("%:e")<CR>','<C-R>=expand("%:p:h")<CR>')<home><c-right><c-right><left>

function! Search(...)
let lstRet=[]
python << EOF
import cachesearch 
from vimenv import env
lstArgs=env.var("a:000")
cachesearch.g_SearchEngin.Search(*lstArgs)
EOF
endfunction

function! SaveSearch(...)
python << EOF
import cachesearch
cachesearch.g_SearchEngin.WriteData()
EOF
endfunction

function! LookSearch(...)
python << EOF
#i=env.var('input("hhhhhhhhhhh")')
import cachesearch
from vimenv import env
lstRoot=cachesearch.g_SearchEngin.GetAllRoot()
lstChoose=env.choices(lstRoot)
if lstChoose:
    cachesearch.g_SearchEngin.DelRoot(lstChoose[0],lstChoose[1])
    cachesearch.g_SearchEngin.WriteData()
EOF
endfunction

function! KillSearch(...)
python << EOF
#i=env.var('input("hhhhhhhhhhh")')
import dirobserver
dirobserver.KillAll()
EOF
endfunction

