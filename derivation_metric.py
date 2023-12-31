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
    # equation level checks go here
    
    if not balanced_brackets(pred):
        return 0

    if ('=' not in pred) and ("\\geq" not in pred) and ("\\leq" not in pred):
        return 0

    # Check if LHS and RHS are identical (exact matching)
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

    # this removes repeated equations (exact matching)
    # This could be improved by using e.g. ROUGE to compute similarity between
    # equations in the SAME derivation, then removing equations that are too similar (beyond exact matching)
    ref_eqs, pred_eqs = [], []
    for eq in pred.split("and"):
        if eq not in pred_eqs:
            pred_eqs.append(eq)
    for eq in ref.split("and"):
        if eq not in ref_eqs:
            ref_eqs.append(eq)

    # this finds the length difference between ref and pred derivations (by equation number)
    diff = abs(len(ref_eqs) - len(pred_eqs))

    positions_range = len(ref_eqs) + 1 if len(ref_eqs) < len(pred_eqs) else len(pred_eqs) + 1
    
    # if difference in derivation lengths is greater than one of the actual derivations, return 0
    if diff > positions_range:
        return 0

    # this then finds the optimal place to put the empty strings
    # such that the averaged score is maximised
    avg_scores, alignments = [], []
    for positions in combinations(range(positions_range), diff):
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
