import json
import torch
from evaluate import load
import numpy as np
from itertools import combinations


def score(ref, pred, metric_name, metric):
    if metric_name == "rouge":
        score = metric.compute(predictions=[pred],references=[ref])['rouge2']
    if metric_name == "bleu":
        score = metric.compute(predictions=[pred],references=[ref])['bleu']
    if metric_name == "gleu":
        score = metric.compute(predictions=[pred],references=[ref])['google_bleu']
    return score


def optimize_score(ref, pred, metric_name, return_equations=False):
    
    #load metric
    if metric_name == "gleu":
        metric = load("google_bleu")
    else:
        metric = load(metric_name)
    
    # make equation lists
    ref_eqs, pred_eqs = [], []

    for eq in pred.split("and"):
        if eq not in pred_eqs:
            pred_eqs.append(eq)

    for eq in ref.split("and"):
        if eq not in ref_eqs:
            ref_eqs.append(eq)
    
    # Find the difference in lengths
    diff = abs(len(ref_eqs) - len(pred_eqs))
    
    # List for storing average ROUGE scores
    avg_scores = []
    
    # List for storing the alignments
    alignments = []
    
    # Iterate over all possible positions to pad empty strings
    for positions in combinations(range(len(ref_eqs)+1), diff):
        # Create a copy of the original list
        ref_copy = ref_eqs.copy()
        pred_copy = pred_eqs.copy()
        
        # Pad the shorter list with empty strings at all possible positions
        if len(ref_eqs) < len(pred_eqs):
            for pos in positions:
                ref_copy.insert(pos, '')
        elif len(pred_eqs) < len(ref_eqs):
            for pos in positions:
                pred_copy.insert(pos, '')
        
        # Calculate and store the average ROUGE score
        scores = [score(ref, pred, metric_name, metric) for ref, pred in zip(ref_copy, pred_copy)]
        avg_scores.append(np.mean(scores))
        alignments.append((ref_copy, pred_copy))
    
    # Find the index of the maximum average ROUGE score
    max_index = np.argmax(avg_scores)
    
    # Return the maximum average ROUGE score and the corresponding alignment
    if return_equations:
        return avg_scores[max_index], alignments[max_index]
    else:
        return avg_scores[max_index]
