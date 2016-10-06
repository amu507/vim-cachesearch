# -*- coding: utf-8 -*-
import cachesearch.search
from vimenv import env

CACHE_FILE=env.var("g:g_DataPath")+"\\cachesearch"

if not globals().has_key("g_SearchEngin"):
    g_SearchEngin=cachesearch.search.CCacheSearch(CACHE_FILE)

