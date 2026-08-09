"""Validate the import boundary of shipped xplane-fdau modules."""

from __future__ import annotations

import ast
from collections.abc import Mapping
import sys


_HOST_OR_LEGACY_ROOTS = frozenset({"XPLM", "XPPython3", "q4xpcc", "xp", "xpwebapi", "xplane_fdr"})
_NETWORK_ROOTS = frozenset(
    {
        "ftplib",
        "http",
        "imaplib",
        "poplib",
        "smtplib",
        "socket",
        "ssl",
        "telnetlib",
        "urllib",
        "xmlrpc",
    }
)
_ALLOWED_ROOTS = frozenset(sys.stdlib_module_names) | {"__future__", "xplane_fdau"}
_IMPORT_LOADER_NAMES = frozenset({"__import__", "import_module"})
_DYNAMIC_EXECUTION_CALLS = frozenset(
    {
        "__import__",
        "builtins.__import__",
        "eval",
        "builtins.eval",
        "exec",
        "builtins.exec",
        "importlib.__import__",
        "importlib.import_module",
        "importlib.reload",
        "importlib.machinery.ExtensionFileLoader",
        "importlib.machinery.SourceFileLoader",
        "importlib.machinery.SourcelessFileLoader",
        "importlib.util.find_spec",
        "importlib.util.module_from_spec",
        "importlib.util.spec_from_file_location",
        "importlib.util.spec_from_loader",
        "pydoc.locate",
        "pkgutil.resolve_name",
        "pkgutil.walk_packages",
        "runpy.run_module",
        "runpy.run_path",
        "zipimport.zipimporter",
    }
)


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _qualified_name(node: ast.AST, bindings: Mapping[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return bindings.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        parent = _qualified_name(node.value, bindings)
        return f"{parent}.{node.attr}" if parent is not None else None
    if isinstance(node, ast.Call):
        called = _qualified_name(node.func, bindings)
        if called in {"getattr", "builtins.getattr"} and len(node.args) >= 2:
            parent = _qualified_name(node.args[0], bindings)
            attribute = _literal_string(node.args[1])
            if parent is not None and attribute is not None:
                return f"{parent}.{attribute}"
        if called in {"vars", "builtins.vars"} and len(node.args) == 1:
            parent = _qualified_name(node.args[0], bindings)
            if parent is not None:
                return f"{parent}.__dict__"
    if isinstance(node, ast.Subscript):
        attribute = _literal_string(node.slice)
        if attribute not in _IMPORT_LOADER_NAMES:
            return None
        parent = _qualified_name(node.value, bindings)
        if parent is not None and parent.endswith(".__dict__"):
            return f"{parent.removesuffix('.__dict__')}.{attribute}"
    return None


def _is_dynamic_execution(called: str) -> bool:
    return called in _DYNAMIC_EXECUTION_CALLS or called.rsplit(".", 1)[-1] in _IMPORT_LOADER_NAMES


def _bindings(tree: ast.AST) -> dict[str, str]:
    bindings: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".", 1)[0]
                bindings[local] = alias.name if alias.asname else local
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module is not None:
            for alias in node.names:
                if alias.name != "*":
                    bindings[alias.asname or alias.name] = f"{node.module}.{alias.name}"

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if value is None:
            continue
        resolved = _qualified_name(value, bindings)
        if resolved is None:
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                bindings[target.id] = resolved
    return bindings


def runtime_import_violations(source: str, *, filename: str = "<runtime>") -> tuple[str, ...]:
    """Return every forbidden static or dynamic import in one runtime module."""
    tree = ast.parse(source, filename=filename)
    bindings = _bindings(tree)
    violations: list[str] = []

    for node in ast.walk(tree):
        imported: list[str] = []
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module is not None:
            imported.append(node.module)

        for module in imported:
            root = module.split(".", 1)[0]
            location = f"{filename}:{getattr(node, 'lineno', 0)}"
            if root in _HOST_OR_LEGACY_ROOTS:
                violations.append(f"{location}: forbidden host or legacy import '{module}'")
            elif root in _NETWORK_ROOTS:
                violations.append(f"{location}: forbidden network import '{module}'")
            elif root not in _ALLOWED_ROOTS:
                violations.append(f"{location}: forbidden third-party import '{module}'; only stdlib and xplane_fdau are allowed")

        if isinstance(node, ast.Call):
            called = _qualified_name(node.func, bindings)
            if called is not None and _is_dynamic_execution(called):
                violations.append(f"{filename}:{node.lineno}: dynamic import mechanism '{called}' is forbidden")

    return tuple(violations)
