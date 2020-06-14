# Find entry_points in a setup.py

import ast
from pathlib import Path

class Visitor(ast.NodeVisitor): 
    def visit_Call(self, node): 
        eps = None 

        if len(node.keywords) > 0: 
                       
            for kw in node.keywords: 
                if kw.arg == "entry_points": 
                    eps = kw.value 
         
        if eps:             
            print(eps.keys[0].arg) 
 
        self.generic_visit(node) 


if __name__ == "__main__":
    v = Visitor()
    v.visit(ast.parse(Path('setup_test.py').read_text(), 'setup.py', 'exec'))

