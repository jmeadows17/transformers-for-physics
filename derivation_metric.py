import json
import torch
from evaluate import load
import numpy as np
from itertools import combinations

def balanced_brackets(eq):
    a, b, c = 0, 0, 0
    for i in eq:
        if i == "(":
            a += 1
        if i == "{":
            b += 1
        if i == "[":
            c += 1
        if i == ")":
            a -= 1
        if i == "}":
            b -= 1
        if i == "]":
            c -= 1
    if a != 0 or b != 0 or c != 0:
        return False
    else:
        return True

def score(ref, pred, metric_name, metric):
    if not balanced_brackets(pred) or '=' not in pred:
        return 0

    #Check if LHS and RHS are identical

    try:
        lhs, rhs = pred.split('=')
        if lhs.replace(" ","") == rhs.replace(" ",""):
            return 0
    except:
        pass
    
    try:
        if metric_name == "rouge":
            score = metric.compute(predictions=[pred],references=[ref])['rouge2']
        if metric_name == "bleu":
            score = metric.compute(predictions=[pred],references=[ref])['bleu']
        if metric_name == "gleu":
            score = metric.compute(predictions=[pred],references=[ref])['google_bleu']
        return score
    except:
        return 0

def optimize_score(ref, pred, metric_name, return_equations=False):
    
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
        
        scores = [score(ref, pred, metric_name, metric) for ref, pred in zip(ref_copy, pred_copy)]
        avg_scores.append(np.mean(scores))
        alignments.append((ref_copy, pred_copy))
    
    max_index = np.argmax(avg_scores)
    
    if return_equations:
        return avg_scores[max_index], alignments[max_index]
    else:
        return avg_scores[max_index]
