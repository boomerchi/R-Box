import re
import sublime
import os
from .utils import execute_command, read_registry


class RscriptMixins:
    message_shown = False

    def custom_env(self):
        paths = self.additional_paths()
        env = os.environ.copy()
        if paths:
            sep = ";" if sublime.platform() == "windows" else ":"
            env["PATH"] = env["PATH"] + sep + sep.join(paths)
        return env

    def rcmd(self, script=None, file=None, args=None):
        cmd = [self.rscript_binary()]
        if script:
            cmd = cmd + ["-e", script]
        elif file:
            cmd = cmd + [file]
        if args:
            cmd = cmd + args

        try:
            return execute_command(cmd, env=self.custom_env())
        except FileNotFoundError:
            print("Rscript binary not found.")
            if not self.message_shown:
                sublime.message_dialog(
                    "Rscript binary cannot be found automatically."
                    "The path to `Rscript` can be specified in the R-Box settings.")
                self.message_shown = True
            return ""
        except Exception as e:
            print("R-Box:", e)
            return ""

    def list_installed_packages(self):
        return self.rcmd("cat(rownames(installed.packages()))").strip().split(" ")

    def list_package_objects(self, pkg, exported_only=True):
        if exported_only:
            objects = self.rcmd("cat(getNamespaceExports(asNamespace('{}')))".format(pkg))
        else:
            objects = self.rcmd("cat(objects(asNamespace('{}')))".format(pkg))
        return objects.strip().split(" ")

    def show_function(self, pkg, funct):
        out = self.rcmd("args({}:::{})".format(pkg, funct))
        out = re.sub(r"^function ", funct, out).strip()
        out = re.sub(r"NULL(?:\n|\s)*$", "", out).strip()
        return out

    def show_function_args(self, pkg, funct):
        out = self.rcmd("cat(names(formals({}:::{})))".format(pkg, funct))
        return out.strip().split(" ")


class RBoxSettingsMixins:
    _rscript_binary = None
    _additional_paths = None

    def rbox_settings(self, key, default):
        s = sublime.load_settings('R-Box.sublime-settings')
        return s.get(key, default)

    def rscript_binary(self):
        rscript_binary = self.rbox_settings("rscript_binary", self._rscript_binary)
        if not rscript_binary:
            if sublime.platform() == "windows":
                try:
                    rscript_binary = os.path.join(
                        read_registry("Software\\R-Core\\R", "InstallPath")[0],
                        "bin",
                        "Rscript.exe")
                except:
                    pass
        if not rscript_binary:
            rscript_binary = "Rscript"
        self._rscript_binary = rscript_binary
        return rscript_binary

    def additional_paths(self):
        additional_paths = self.rbox_settings("additional_paths", [])
        if not additional_paths:
            additional_paths = self._additional_paths
        if not additional_paths:
            if sublime.platform() == "osx":
                additional_paths = execute_command(
                    "/usr/bin/login -fpql $USER $SHELL -l -c 'echo -n $PATH'", shell=True)
                additional_paths = additional_paths.strip().split(":")
        if not additional_paths:
            additional_paths = "Rscript"

        self._additional_paths = additional_paths
        return additional_paths


class RBoxViewMixins:
    VALIDCALL = re.compile(r"(?:([a-zA-Z][a-zA-Z0-9.]*)(?::::?))?([.a-zA-Z0-9_-]+)\s*\($")

    def function_name_at_point(self, view, pt):
        if not view.match_selector(pt, "meta.function-call.r"):
            return None, None
        scope_begin = view.extract_scope(pt).begin()
        if view.match_selector(scope_begin, "support.function.r, variable.function.r"):
            scope_begin = view.find("\(", scope_begin).begin() + 1
        line = self.extract_line(view, scope_begin, truncated=True)
        m = self.VALIDCALL.search(line)
        if m:
            return m.groups()
        else:
            return None, None

    def inline_packages_for_view(self, view):
        packages = []
        for s in view.find_all(r"""(library|require)\(["']?[a-zA-Z][a-zA-Z0-9.]*"""):
            pkg = packages.append(re.sub(r"""(library|require)\(["']?""", "", view.substr(s)))
            if pkg and pkg not in packages:
                packages.append(pkg)
        return packages

    def extract_line(self, view, pt, truncated=False):
        if truncated:
            row, _ = view.rowcol(pt)
            line_begin = view.text_point(row, 0)
            return view.substr(sublime.Region(line_begin, pt))
        else:
            return view.substr(view.line(pt))


class RBoxMixins(RBoxViewMixins, RscriptMixins, RBoxSettingsMixins):

    pass