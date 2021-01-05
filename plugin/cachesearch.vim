command! -nargs=* -complete=dir Search call Search(<f-args>) 
command! -nargs=* SaveSearch call SaveSearch(<f-args>) 

nnoremap ft :Search <C-R>=expand("<cword>")<CR><CR>
vnoremap ft "ay:call Search(@a)<CR>
nnoremap fd :let _func=expand("<cword>")\|call Search(_func,"n","","",GetDefineString(_func))<CR><CR>
nnoremap fu :let _func=expand("<cword>")\|call Search(_func,"n","","", "[^a-zA-Z0-9\'\"_]" .  _func . "[^a-zA-Z0-9\'\"_]" )<CR>
nnoremap ff :Search <C-R>=expand("<cword>")<CR> fr<c-left><left>
nnoremap ffa :Search <C-R>=expand("<cword>")<CR> far<c-left><left>
"nnoremap cs :Search <C-R>=expand("<cword>")<CR> n<c-b><c-right><c-right>
nnoremap fc :call Search('<C-R>=expand("<cword>")<CR>' ,'n','<C-R>=expand("%:e")<CR>','<C-R>=expand("%:p:h")<CR>')<home><c-right><c-right><left>
nnoremap fca :call Search('<C-R>=expand("<cword>")<CR>' ,'ar','<C-R>=expand("%:e")<CR>','<C-R>=expand("%:p:h")<CR>')<home><c-right><c-right><left>
nnoremap fa :call Search('<C-R>=expand("<cword>")<CR>' ,'nr','<C-R>=expand("%:e")<CR>')<home><c-right><c-right><left>
nnoremap faa :call Search('<C-R>=expand("<cword>")<CR>' ,'ar','<C-R>=expand("%:e")<CR>')<home><c-right><c-right><left>
nnoremap fo :call Search('<C-R>=expand("<cword>")<CR>' ,'or','<C-R>=expand("%:e")<CR>','<C-R>=expand("%:p:h")<CR>')<home><c-right><c-right><left>
"nnoremap fcc :call ClearSearchCache()<cr>

func! GetDefineString(_func)
	let sName=""
	let sExt=expand("%:e")
	let tPreFix=[]
	let tSufFix=[]
	if sExt=="vim"
		let tPreFix=["func! ","function! ","let "]
	elseif sExt=="js" ||sExt=="ts"
		let tPreFix=["function\\s+", "^\\s*", "\\s*class ", "private\\s+", "publi\\s+c", "async\\s+"]
        let tSufFix=["\\s*=\\s*function", "\\s*=\\s*async\\s+function"]
	elseif sExt=="lua"||sExt=="js"
		let tPreFix=["function ","function [0-9a-zA-Z_]+[:\.]","async function ", "^\\s*"]
		let tSufFix=["[ ]*=[ ]*function", "[ ]*=[ ]*async function"]
	elseif sExt=="py"
		let tPreFix=["def ","class "]
	elseif sExt=="sol"
		let tPreFix=["function +","modifier +"]
	else
		let tPreFix=["class ","int ","void ","long "]
	endif
	let tName=[]
	for sPrefix in tPreFix
		call add(tName,sPrefix.a:_func."[^0-9a-zA-Z_]")
	endfor
	for sSuffix in tSufFix
		call add(tName,a:_func.sSuffix)
	endfor
	return join(tName,"\|")
endfunc

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

function! ClearSearchCache()
python << EOF
import cachesearch
cachesearch.g_SearchEngin.InitCache()
EOF
endfunction

