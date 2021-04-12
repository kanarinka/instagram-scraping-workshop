#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 11 2021

@author: kanarinka
"""
import csv

fname = 'test.csv'
csvFile = open(fname, 'w', encoding="utf-8")

fieldnames = [
			'shortcode',
			'mediaid',
			'title'
			]

csvWriter = csv.DictWriter(csvFile, fieldnames=fieldnames)
csvWriter.writeheader()


row = {
	'shortcode': 'gablasdk',
	'mediaid': 12345,
	'title': 'blip'
	}

csvWriter.writerow(row)
csvFile.close()