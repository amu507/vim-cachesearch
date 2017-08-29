# -*- coding: utf-8 -*-
import cachesearch.search
from vimenv import env

if not globals().has_key("g_SearchEngin"):
    CACHE_FILE=cachesearch.search.FormatPathStr(env.var("g:g_DataPath"),"cachesearch")
    g_SearchEngin=cachesearch.search.CCacheSearch(CACHE_FILE)

