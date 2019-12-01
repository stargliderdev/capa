#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
count file type in dir
find . -type f | sed -n 's/..*\.//p' | sort | uniq -c
"""
