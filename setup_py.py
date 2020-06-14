# Find entry_points in a setup.py

import ast
from pathlib import Path


class Visitor(ast.NodeVisitor):
    def visit_Call(self, node):
        eps = None

        # Only process if the call has kwargs
        if len(node.keywords) > 0:
            # If one kwarg is 'entry_points', grab the contents
            for kw in node.keywords:
                if kw.arg == "entry_points":
                    eps = kw.value

        if eps:
            # entry_points is a dict, so Constant('flake8.extension') will only appear once!
            breakpoint()
            # Look in the ep's for any that're flake8 extensions
            # This is fragile if there are any non-literal-defined keys in the
            ep_dict = {
                k: v
                for k, v in zip(eps.keys, eps.values)
                if k.value == "flake8.extension"
            }

            # Process the entry point contents
            for k in ep_dict:
                breakpoint()  # print(ep_dict[k])

        self.generic_visit(node)


if __name__ == "__main__":
    v = Visitor()
    v.visit(ast.parse(Path("sample_setup.py").read_text(), "setup.py", "exec"))
