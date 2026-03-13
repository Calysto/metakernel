# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, MetaKernel, option


class LSMagicMagic(Magic):
    @option(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Also show magic search paths and any load errors.",
    )
    def line_lsmagic(self, verbose: bool = False) -> None:
        """
        %lsmagic [-v] - list the current line and cell magics

        This line magic will list all of the available cell and line
        magics installed in the system and in your personal magic
        folder.

        Use -v/--verbose to also show the directories that were searched
        and any errors that occurred while loading magic files.

        Example:
            %lsmagic
            %lsmagic -v
        """
        line_magics = self.kernel.line_magics.keys()
        cell_magics = self.kernel.cell_magics.keys()

        mp = self.kernel.magic_prefixes["magic"]
        out = [
            "Available line magics:",
            "  ".join(sorted([(mp + lm) for lm in line_magics])),
            "",
            "Available cell magics:",
            "  ".join(sorted([(mp + mp + cm) for cm in cell_magics])),
        ]

        if verbose:
            search_paths = getattr(self.kernel, "magic_search_paths", [])
            load_errors = getattr(self.kernel, "magic_load_errors", [])
            out += ["", "Magic search paths:"]
            for path in search_paths:
                out.append(f"  {path}")
            if load_errors:
                out += ["", "Load errors:"]
                for path, error in load_errors:
                    out.append(f"  {path}: {error}")
            else:
                out += ["", "No load errors."]

        self.kernel.Print("\n".join(out))


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(LSMagicMagic)
