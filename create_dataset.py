import json
import re

with open('LaTeX.txt', 'r') as f:
    content = f.read()
    sections = content.split('\\section')
    
def create_example(derivation_example, field):
    
    # name of the derivation
    name = re.sub(r'[\n{}]', '', derivation_example.split("\\begin{equation}")[0])
    if ("\\" in name) and ("$" not in name) and ('\\"' not in name):
        name = re.sub(r'[\n{}]', '', derivation_example.split("\\begin{multline}")[0])
    
    # list of equations
    multline_eqs = [i.split('\\end{multline}')[0].replace('\n','') for i in derivation_example.split("\\begin{multline}")[1:]]
    equation_eqs = [i.split('\\end{equation}')[0].replace('\n','') for i in derivation_example.split("\\begin{equation}")[1:]]
    unsorted_equation_list = equation_eqs + multline_eqs
    eq_idxs = {eq:derivation_example.replace("\n",'').index(eq) for eq in unsorted_equation_list}
    equation_list = [item[0].replace('\\\\','') for item in sorted(eq_idxs.items(), key = lambda x:x[1])]
    
    premises = [remove_spaces(i.replace("%PREM",'')) for i in equation_list if "prem" in i.lower()]
    
    goal_equation = remove_spaces(equation_list[-1])
    
    # ground truth derivation
    derivation = remove_spaces(" and ".join(equation_list).replace("%PREM",''))
    
    # prompt
    p = "Given "
    for premise in premises[:-1]:
        p += premise + " and "
    p += premises[-1] + ", "
    p += "then obtain " + goal_equation
    
    # make dictionary entry
    example = {
        "name":name,
        "field":field,
        "premises":premises,
        "derivation":derivation,
        "prompt":p
    }
    
    return example

remove_spaces = lambda eq: " ".join([i for i in eq.split(" ") if i != ""])

# UPDATE this array as LaTeX sections get added: 
# Electromagnetism = 5, Quantum = 6
idxs = [5, 6]

# create dataset
data = []
for i in idxs:
    section = sections[i]
    field = section.split("{")[1].split("}")[0]
    subsections = section.split("\\subsection")[1:]
    for derivation_example in subsections:
        data.append(create_example(derivation_example, field))
        
with open("physics_derivations.json", "w") as f:
    json.dump(data, f)
