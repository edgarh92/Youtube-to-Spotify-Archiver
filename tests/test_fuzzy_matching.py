#!/usr/bin/env python3

from thefuzz import fuzz, process

results = {'Pirate Ship', 'Mal - Instrumental', 'Flight From Seoul : B747', 'Mal'}

print(process.extract("PO.U.RYU - Mal", results, limit=3))