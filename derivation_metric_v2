import json
import torch
from evaluate import load
import numpy as np
from itertools import combinations

def balanced_brackets(eq):
    bracket_map = {"(": ")", "[": "]", "{": "}"}
    open_brackets = set(["(", "[", "{"])
    stack = []

    for i in eq:
        if i in open_brackets:
            stack.append(i)
        elif stack and i == bracket_map[stack[-1]]:
            stack.pop()
        else:
            return False
    return not stack

def fix_brackets(eq):
    bracket_map = {"(": ")", "[": "]", "{": "}"}
    open_brackets = set(["(", "[", "{"])
    stack = []
    fixed_eq = ""

    for i in eq:
        if i in open_brackets:
            stack.append(i)
        elif stack and i == bracket_map[stack[-1]]:
            stack.pop()
        elif not stack and i in bracket_map.values():
            continue

        fixed_eq += i

        while stack and bracket_map[stack[-1]] not in fixed_eq:
            fixed_eq += bracket_map[stack.pop()]

    while stack:
        fixed_eq += bracket_map[stack.pop()]

    return fixed_eq

def score(ref, pred, metric_name, metric, fix=False):
    if fix:
        pred = fix_brackets(pred)
    elif not balanced_brackets(pred) or '=' not in pred:
        return 0

    if metric_name == "rouge":
        score = metric.compute(predictions=[pred],references=[ref])['rouge2']
    if metric_name == "bleu":
        score = metric.compute(predictions=[pred],references=[ref])['bleu']
    if metric_name == "gleu":
        score = metric.compute(predictions=[pred],references=[ref])['google_bleu']
    return score

def optimize_score(ref, pred, metric_name, fix=False, return_equations=False):
    
    if metric_name == "gleu":
        metric = load("google_bleu")
    else:
        metric = load(metric_name)
    
    ref_eqs, pred_eqs = [], []

    for eq in pred.split("and"):
        if eq not in pred_eqs:
            pred_eqs.append(eq)

    for eq in ref.split("and"):
        if eq not in ref_eqs:
            ref_eqs.append(eq)
    
    diff = abs(len(ref_eqs) - len(pred_eqs))
    avg_scores = []
    alignments = []
    
    for positions in combinations(range(len(ref_eqs)+1), diff):
        ref_copy = ref_eqs.copy()
        pred_copy = pred_eqs.copy()
        
        if len(ref_eqs) < len(pred_eqs):
            for pos in positions:
                ref_copy.insert(pos, '')
        elif len(pred_eqs) < len(ref_eqs):
            for pos in positions:
                pred_copy.insert(pos, '')
        
        scores = [score(ref, pred, metric_name, metric, fix=fix) for ref, pred in zip(ref_copy, pred_copy)]
        avg_scores.append(np.mean(scores))
        alignments.append((ref_copy, pred_copy))
    
    max_index = np.argmax(avg_scores)
    
    if return_equations:
        return avg_scores[max_index], alignments[max_index]
    else:
        return avg_scores[max_index]
