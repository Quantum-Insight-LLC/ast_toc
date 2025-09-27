"""AST parser for extracting Python file structure."""

import ast


class ASTParser:
    """Parser for extracting classes, functions and imports from Python files."""

    def parse_file(self, file_path: str) -> dict[str, list[str]]:
        """Parse Python file and extract structure.

        Args:
            file_path: Path to Python file

        Returns:
            Dict with keys: classes, functions, imports
        """
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {"classes": [], "functions": [], "imports": []}

        classes = []
        functions = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and not self._is_nested(node, tree):
                # Extract class name and methods (top-level classes only)
                class_info = f"class {node.name}"
                if node.bases:
                    bases = [self._get_name(base) for base in node.bases]
                    class_info += f"({', '.join(bases)})"
                classes.append(class_info)

                # Add methods to functions list
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = (
                            f"{node.name}.{item.name}({self._format_args(item.args)})"
                        )
                        functions.append(method_info)

            elif isinstance(node, ast.FunctionDef) and not self._is_nested(node, tree):
                # Top-level functions only
                func_info = f"def {node.name}({self._format_args(node.args)})"
                functions.append(func_info)

            elif isinstance(node, ast.Import | ast.ImportFrom) and not self._is_nested(
                node, tree
            ):
                import_info = self._format_import(node)
                if import_info:
                    imports.append(import_info)

        return {"classes": classes, "functions": functions, "imports": imports}

    def _is_nested(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if function is nested inside a class or another function."""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef | ast.FunctionDef):
                for child in parent.body:
                    if child is node:
                        return True
        return False

    def _format_args(self, args: ast.arguments) -> str:
        """Format function arguments without type annotations."""
        arg_parts = []

        # Regular arguments (skip 'self' for methods)
        for arg in args.args:
            if arg.arg != "self":
                arg_parts.append(arg.arg)

        # *args
        if args.vararg:
            arg_parts.append(f"*{args.vararg.arg}")

        # **kwargs
        if args.kwarg:
            arg_parts.append(f"**{args.kwarg.arg}")

        return ", ".join(arg_parts)

    def _format_import(self, node: ast.AST) -> str:
        """Format import statement."""
        if isinstance(node, ast.Import):
            return f"import {', '.join(alias.name for alias in node.names)}"
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = ", ".join(alias.name for alias in node.names)
            return f"from {module} import {names}"
        return ""

    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "Unknown"
