"""Generate the code reference pages and navigation."""

from pathlib import Path
import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

for path in sorted(Path('tree').rglob('*.py')):
    module_path = path.relative_to('tree').with_suffix('')

    if module_path.as_posix() != '__init__':
        doc_path = path.relative_to('tree').with_suffix('.md')
        full_doc_path = Path('docs/reference', doc_path)
        parts = tuple(module_path.parts)
        nav[parts] = doc_path.as_posix()
        with mkdocs_gen_files.open(full_doc_path.absolute(), "w") as fd:
            ident = ".".join(parts)
            fd.write(f"::: tree.{ident}")

with mkdocs_gen_files.open('reference/SUMMARY.md', 'w') as nav_file:
    nav_file.writelines(nav.build_literate_nav())
