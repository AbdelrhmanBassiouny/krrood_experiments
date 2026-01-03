import os
import pytest
import ast
from krrood_experiments.owl_to_python import OwlToPythonConverter

def compare_ast(node1, node2):
    if type(node1) != type(node2): return False
    if isinstance(node1, ast.AST):
        for k, v in vars(node1).items():
            if k in ('lineno', 'col_offset', 'ctx', 'end_lineno', 'end_col_offset'): continue
            if not compare_ast(v, getattr(node2, k)): return False
        return True
    elif isinstance(node1, list):
        if len(node1) != len(node2): return False
        for i in range(len(node1)):
            if not compare_ast(node1[i], node2[i]): return False
        return True
    else: return node1 == node2

def get_assign_name(n):
    if isinstance(n, ast.AnnAssign):
        if isinstance(n.target, ast.Name): return n.target.id
    if isinstance(n, ast.Assign):
        if n.targets and isinstance(n.targets[0], ast.Name): return n.targets[0].id
    return ''

def normalize_class_body(node):
    if not isinstance(node, ast.ClassDef): return node
    docstring, assignments, methods, others = [], [], [], []
    body = node.body
    if body and isinstance(body[0], ast.Expr):
        val = body[0].value
        if hasattr(ast, 'Constant'):
            if isinstance(val, ast.Constant) and isinstance(val.value, str): docstring, body = [body[0]], body[1:]
        elif isinstance(val, ast.Str): docstring, body = [body[0]], body[1:]
    for item in body:
        if isinstance(item, (ast.AnnAssign, ast.Assign)): assignments.append(item)
        elif isinstance(item, ast.FunctionDef): methods.append(item)
        else: others.append(item)
    assignments.sort(key=get_assign_name)
    methods.sort(key=lambda n: n.name)
    node.body = docstring + assignments + methods + others
    return node

def normalize_module(tree):
    for node in tree.body:
        if isinstance(node, ast.ClassDef): normalize_class_body(node)
    return tree

def assert_ast_equal(content1, content2, filename):
    try:
        tree1 = ast.parse(content1)
        tree2 = ast.parse(content2)
    except SyntaxError:
        assert content1 == content2, f'Content mismatch in {filename}'
        return
    normalize_module(tree1)
    normalize_module(tree2)
    if not compare_ast(tree1, tree2): assert content1 == content2, f'AST structural mismatch in {filename}'

def test_lubm_regression(tmp_path):
    repo_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    resources_path = os.path.join(repo_dir, 'lubm', 'resources')
    owl_file = os.path.join(resources_path, 'lubm_clean.owl')
    _default_overrides = {'Person': {'age': 'int', 'telephone': 'str', 'title': 'str', 'email_address': 'str'}, 'Professor': {'tenured': 'bool'}, 'Publication': {'publication_date': 'str'}, 'Software': {'software_version': 'str'}, 'Thing': {'name': 'str', 'office_number': 'int', 'research_interest': 'str'}}
    converter = OwlToPythonConverter(predefined_data_types=_default_overrides)
    converter.load_ontology(owl_file)
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    output_base = output_dir / 'lubm_with_predicates'
    converter.save_to_file(str(output_base) + '.py')
    existing_dir = os.path.join(repo_dir, 'src', 'krrood_experiments', 'lubm')
    files_to_compare = ['lubm_with_predicates.py', 'lubm_with_predicates_properties.py', 'lubm_with_predicates_base.py', 'lubm_with_predicates.pyi']
    for filename in files_to_compare:
        generated_file = output_dir / filename
        existing_file = os.path.join(existing_dir, filename)
        with open(generated_file, 'r') as f: generated_content = f.read()
        with open(existing_file, 'r') as f: existing_content = f.read()
        assert_ast_equal(generated_content, existing_content, filename)

@pytest.mark.skip(reason='OWL2Bench ontology is not stable enough yet.')
def test_owl2bench_regression(tmp_path):
    repo_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    resources_path = os.path.join(repo_dir, 'owl2bench', 'resources', 'refactored_ontologies')
    owl_file = os.path.join(resources_path, 'owl2benchRlFixed.owl')
    _default_overrides = {'Person': {'age': 'int', 'telephone': 'str', 'title': 'str', 'email_address': 'str'}, 'Professor': {'tenured': 'bool'}, 'Publication': {'publication_date': 'str'}, 'Software': {'software_version': 'str'}, 'Thing': {'name': 'str', 'office_number': 'int', 'research_interest': 'str'}}
    converter = OwlToPythonConverter(predefined_data_types=_default_overrides)
    converter.load_ontology(owl_file)
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    output_base = output_dir / 'owl2bench_with_predicates'
    converter.save_to_file(str(output_base) + '.py')
    existing_dir = os.path.join(repo_dir, 'src', 'krrood_experiments', 'owl2bench')
    files_to_compare = ['owl2bench_with_predicates.py', 'owl2bench_with_predicates_properties.py', 'owl2bench_with_predicates_base.py', 'owl2bench_with_predicates.pyi']
    for filename in files_to_compare:
        generated_file = output_dir / filename
        existing_file = os.path.join(existing_dir, filename)
        with open(generated_file, 'r') as f: generated_content = f.read()
        with open(existing_file, 'r') as f: existing_content = f.read()
        assert_ast_equal(generated_content, existing_content, filename)
