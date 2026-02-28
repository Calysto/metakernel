import sys

import pytest

from tests.utils import EvalKernel, get_kernel, get_log_text

try:
    import ipyparallel
except ImportError:
    ipyparallel = None

NO_IPYPARALLEL = ipyparallel is None


@pytest.mark.skipif(ipyparallel is None, reason="Requires ipyparallel")
@pytest.mark.skipif(sys.platform == "darwin", reason="Fails on darwin")
def test_parallel_magic() -> None:
    kernel = get_kernel(EvalKernel)
    # start up an EvalKernel on each node:
    kernel.do_execute("%parallel metakernel_python MetaKernelPython", False)
    # Now, execute something on each one:
    kernel.do_execute("%px cluster_rank", False)
    results = get_log_text(kernel)
    assert "[0, 1, 2]" in results, results


# Starting the cluster from here doesn't work with pytest
# so we start `ipcluster` before we test.

# def setup_func():
#    ## start up a cluster in the background with three nodes:
#    os.system("ipcluster start --n=3 &")

# def teardown():
#    ## shutdown the cluster:
#    os.system("ipcluster stop")


# ---------------------------------------------------------------------------
# Helpers for mocking the cluster
# ---------------------------------------------------------------------------


class MockView:
    """Minimal stand-in for an ipyparallel view."""

    def __init__(self):
        self.executed = []

    def execute(self, code, block=False):
        self.executed.append(code)

    def __getitem__(self, key):
        return None

    def __setitem__(self, key, value):
        pass

    def scatter(self, name, values, flatten=False):
        pass

    def append(self, other):
        pass


class MockClient:
    """Stand-in for ipyparallel.Client that records how views were requested."""

    def __init__(self):
        self.ids = [0, 1, 2]
        self.accessed_with = []

    def __getitem__(self, item):
        self.accessed_with.append(item)
        return MockView()

    def load_balanced_view(self):
        return MockView()

    def __len__(self):
        return len(self.ids)


# ---------------------------------------------------------------------------
# line_parallel with ids
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_parallel_no_ids_uses_all_engines(monkeypatch) -> None:
    """ids=None selects all engines via client[:]."""
    client = MockClient()
    monkeypatch.setattr(ipyparallel, "Client", lambda: client)

    from metakernel.magics.parallel_magic import ParallelMagic

    magic = ParallelMagic(get_kernel(EvalKernel))
    magic.line_parallel("mymod", "MyClass")

    assert magic.view is not None
    assert slice(None, None, None) in client.accessed_with


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_parallel_ids_single_int(monkeypatch) -> None:
    """ids=[0] resolves to int 0 and selects engine 0 via client[0]."""
    client = MockClient()
    monkeypatch.setattr(ipyparallel, "Client", lambda: client)

    from metakernel.magics.parallel_magic import ParallelMagic

    magic = ParallelMagic(get_kernel(EvalKernel))
    magic.line_parallel("mymod", "MyClass", ids="[0]")

    assert magic.view is not None
    assert 0 in client.accessed_with


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_parallel_ids_slice(monkeypatch) -> None:
    """ids=[0:2] resolves to slice(0, 2) and selects engines 0-1 via client[slice]."""
    client = MockClient()
    monkeypatch.setattr(ipyparallel, "Client", lambda: client)

    from metakernel.magics.parallel_magic import ParallelMagic

    magic = ParallelMagic(get_kernel(EvalKernel))
    magic.line_parallel("mymod", "MyClass", ids="[0:2]")

    assert magic.view is not None
    assert slice(0, 2, None) in client.accessed_with


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_parallel_ids_slice_all(monkeypatch) -> None:
    """ids=[:] resolves to slice(None) and selects all engines via client[:]."""
    client = MockClient()
    monkeypatch.setattr(ipyparallel, "Client", lambda: client)

    from metakernel.magics.parallel_magic import ParallelMagic

    magic = ParallelMagic(get_kernel(EvalKernel))
    magic.line_parallel("mymod", "MyClass", ids="[:]")

    assert magic.view is not None
    assert slice(None, None, None) in client.accessed_with


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_parallel_ids_tuple_indexes(monkeypatch) -> None:
    """ids=[0,2] resolves to a tuple and calls client[item] for each element."""
    client = MockClient()
    monkeypatch.setattr(ipyparallel, "Client", lambda: client)

    from metakernel.magics.parallel_magic import ParallelMagic

    magic = ParallelMagic(get_kernel(EvalKernel))
    magic.line_parallel("mymod", "MyClass", ids="[0,2]")

    assert magic.view is not None
    assert 0 in client.accessed_with
    assert 2 in client.accessed_with


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_parallel_ids_invalid_falls_back_to_all(monkeypatch) -> None:
    """An ids value that fails eval falls back to client[:] (all engines)."""
    client = MockClient()
    monkeypatch.setattr(ipyparallel, "Client", lambda: client)

    from metakernel.magics.parallel_magic import ParallelMagic

    magic = ParallelMagic(get_kernel(EvalKernel))
    magic.line_parallel("mymod", "MyClass", ids="[[[invalid")

    assert magic.view is not None
    assert slice(None, None, None) in client.accessed_with


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_parallel_ids_stores_module_class_kernel_name(monkeypatch) -> None:
    """line_parallel stores module_name, class_name, and kernel_name on the magic."""
    client = MockClient()
    monkeypatch.setattr(ipyparallel, "Client", lambda: client)

    from metakernel.magics.parallel_magic import ParallelMagic

    magic = ParallelMagic(get_kernel(EvalKernel))
    magic.line_parallel("mymod", "MyClass", kernel_name="mykernel")

    assert magic.module_name == "mymod"
    assert magic.class_name == "MyClass"
    assert magic.kernel_name == "mykernel"


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_parallel_ids_sets_cluster_variables_on_kernel(monkeypatch) -> None:
    """line_parallel sets cluster_size and cluster_rank=-1 on the host kernel."""
    client = MockClient()
    monkeypatch.setattr(ipyparallel, "Client", lambda: client)

    from metakernel.magics.parallel_magic import ParallelMagic

    kernel = get_kernel(EvalKernel)
    magic = ParallelMagic(kernel)
    magic.line_parallel("mymod", "MyClass")

    assert kernel.get_variable("cluster_size") == len(client.ids)
    assert kernel.get_variable("cluster_rank") == -1


# ---------------------------------------------------------------------------
# Helpers for line_px / _clean_code tests
# ---------------------------------------------------------------------------


class _PxView:
    """MockView whose __getitem__ can return a value or raise an exception."""

    def __init__(self, return_value=None, raises=None, fail_times=0):
        self.called_with = []
        self._return_value = return_value
        self._raises = raises
        self._fail_times = fail_times  # raise on first N calls, then succeed
        self._call_count = 0

    def __getitem__(self, key):
        self._call_count += 1
        self.called_with.append(key)
        if self._raises is not None:
            if self._fail_times == 0 or self._call_count <= self._fail_times:
                raise self._raises
        return self._return_value

    def __setitem__(self, key, value):
        pass

    def execute(self, code, block=False):
        pass

    def scatter(self, name, values, flatten=False):
        pass


def _make_px_magic(view=None, kernel_name="default"):
    from metakernel.magics.parallel_magic import ParallelMagic

    kernel = get_kernel(EvalKernel)
    magic = ParallelMagic(kernel)
    magic.view = view if view is not None else _PxView()
    magic.kernel_name = kernel_name
    return magic


# ---------------------------------------------------------------------------
# _clean_code
# ---------------------------------------------------------------------------


def test_clean_code_strips_whitespace() -> None:
    magic = _make_px_magic()
    assert magic._clean_code("  hello  ") == "hello"


def test_clean_code_escapes_double_quotes() -> None:
    magic = _make_px_magic()
    assert magic._clean_code('say "hi"') == 'say \\"hi\\"'


def test_clean_code_escapes_newlines() -> None:
    magic = _make_px_magic()
    assert magic._clean_code("a\nb") == "a\\nb"


def test_clean_code_combined() -> None:
    magic = _make_px_magic()
    assert magic._clean_code('  "a"\n"b"  ') == '\\"a\\"\\n\\"b\\"'


# ---------------------------------------------------------------------------
# line_px
# ---------------------------------------------------------------------------


def test_line_px_stores_result_in_retval() -> None:
    magic = _make_px_magic(view=_PxView(return_value=[0, 1, 2]))
    magic.line_px("cluster_rank")
    assert magic.retval == [0, 1, 2]


def test_line_px_uses_magic_kernel_name_by_default() -> None:
    view = _PxView()
    magic = _make_px_magic(view=view, kernel_name="mykernel")
    magic.line_px("x")
    assert "mykernel" in view.called_with[0]


def test_line_px_overrides_kernel_name_when_provided() -> None:
    view = _PxView()
    magic = _make_px_magic(view=view, kernel_name="default")
    magic.line_px("x", kernel_name="scheme")
    assert "scheme" in view.called_with[0]
    assert "default" not in view.called_with[0]


def test_line_px_expression_appears_in_view_call() -> None:
    view = _PxView()
    magic = _make_px_magic(view=view)
    magic.line_px("1 + 1")
    assert "1 + 1" in view.called_with[0]


def test_line_px_set_variable_stores_result_on_kernel() -> None:
    magic = _make_px_magic(view=_PxView(return_value=42))
    magic.line_px("x", set_variable="myvar")
    assert magic.kernel.get_variable("myvar") == 42
    assert magic.retval is None


def test_line_px_evaluate_true_sets_code() -> None:
    magic = _make_px_magic()
    magic.line_px("my_expression", evaluate=True)
    assert magic.code == "my_expression"


def test_line_px_evaluate_false_leaves_code_unchanged() -> None:
    magic = _make_px_magic()
    magic.code = "original"
    magic.line_px("new_expression", evaluate=False)
    assert magic.code == "original"


def test_line_px_exception_stores_error_string() -> None:
    magic = _make_px_magic(view=_PxView(raises=RuntimeError("engine down")))
    magic.line_px("x")
    assert "engine down" in magic.retval


def test_line_px_retry_true_succeeds_clears_retry_flag(monkeypatch) -> None:
    import metakernel.magics.parallel_magic as pmod

    monkeypatch.setattr(pmod.time, "sleep", lambda _: None)
    magic = _make_px_magic(view=_PxView(return_value="ok"))
    magic.retry = True
    magic.line_px("x")
    assert magic.retval == "ok"
    assert magic.retry is False


def test_line_px_retry_true_all_fail_raises(monkeypatch) -> None:
    import metakernel.magics.parallel_magic as pmod

    monkeypatch.setattr(pmod.time, "sleep", lambda _: None)
    magic = _make_px_magic(view=_PxView(raises=RuntimeError("dead")))
    magic.retry = True
    with pytest.raises(Exception, match="Cluster clients have not started"):
        magic.line_px("x")


# ---------------------------------------------------------------------------
# cell_px
# ---------------------------------------------------------------------------


def test_cell_px_stores_result_in_retval() -> None:
    magic = _make_px_magic(view=_PxView(return_value=[0, 1, 2]))
    magic.code = "cluster_rank"
    magic.cell_px()
    assert magic.retval == [0, 1, 2]


def test_cell_px_uses_magic_kernel_name_by_default() -> None:
    view = _PxView()
    magic = _make_px_magic(view=view, kernel_name="mykernel")
    magic.code = "x"
    magic.cell_px()
    assert "mykernel" in view.called_with[0]


def test_cell_px_overrides_kernel_name_when_provided() -> None:
    view = _PxView()
    magic = _make_px_magic(view=view, kernel_name="default")
    magic.code = "x"
    magic.cell_px(kernel_name="scheme")
    assert "scheme" in view.called_with[0]
    assert "default" not in view.called_with[0]


def test_cell_px_code_appears_in_view_call() -> None:
    view = _PxView()
    magic = _make_px_magic(view=view)
    magic.code = "1 + 1"
    magic.cell_px()
    assert "1 + 1" in view.called_with[0]


def test_cell_px_set_variable_stores_result_on_kernel() -> None:
    magic = _make_px_magic(view=_PxView(return_value=99))
    magic.code = "x"
    magic.cell_px(set_variable="myvar")
    assert magic.kernel.get_variable("myvar") == 99
    assert magic.retval is None


def test_cell_px_evaluate_true_sets_evaluate_flag() -> None:
    magic = _make_px_magic()
    magic.code = "x"
    magic.cell_px(evaluate=True)
    assert magic.evaluate is True


def test_cell_px_evaluate_false_sets_evaluate_flag() -> None:
    magic = _make_px_magic()
    magic.code = "x"
    magic.evaluate = True  # pre-set to confirm it gets overwritten
    magic.cell_px(evaluate=False)
    assert magic.evaluate is False


# ---------------------------------------------------------------------------
# Helpers for line_pmap tests
# ---------------------------------------------------------------------------


class _LoadBalancedView:
    """Mock for an ipyparallel load-balanced view."""

    def __init__(self, return_value=None):
        self.map_async_calls = []
        self._return_value = return_value

    def map_async(self, f, args):
        self.map_async_calls.append((f, list(args)))
        return self._return_value


def _make_pmap_magic(lb_view=None, kernel_name="default"):
    from metakernel.magics.parallel_magic import ParallelMagic

    kernel = get_kernel(EvalKernel)
    magic = ParallelMagic(kernel)
    magic.view_load_balanced = lb_view if lb_view is not None else _LoadBalancedView()
    magic.kernel_name = kernel_name
    return magic


# ---------------------------------------------------------------------------
# line_pmap
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_pmap_stores_result_in_retval() -> None:
    lb_view = _LoadBalancedView(return_value="async_result")
    magic = _make_pmap_magic(lb_view=lb_view)
    magic.line_pmap("myfunc", "[1, 2, 3]")
    assert magic.retval == "async_result"


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_pmap_evaluates_args_list() -> None:
    lb_view = _LoadBalancedView()
    magic = _make_pmap_magic(lb_view=lb_view)
    magic.line_pmap("myfunc", "[10, 20, 30]")
    _, mapped_args = lb_view.map_async_calls[0]
    assert mapped_args == [10, 20, 30]


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_pmap_evaluates_args_range() -> None:
    lb_view = _LoadBalancedView()
    magic = _make_pmap_magic(lb_view=lb_view)
    magic.line_pmap("myfunc", "range(3)")
    _, mapped_args = lb_view.map_async_calls[0]
    assert mapped_args == [0, 1, 2]


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_pmap_uses_magic_kernel_name_by_default() -> None:
    lb_view = _LoadBalancedView()
    magic = _make_pmap_magic(lb_view=lb_view, kernel_name="mykernel")
    magic.line_pmap("myfunc", "[]")
    f, _ = lb_view.map_async_calls[0]
    assert f.__defaults__[0] == "mykernel"


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_pmap_overrides_kernel_name_when_provided() -> None:
    lb_view = _LoadBalancedView()
    magic = _make_pmap_magic(lb_view=lb_view, kernel_name="default")
    magic.line_pmap("myfunc", "[]", kernel_name="scheme")
    f, _ = lb_view.map_async_calls[0]
    assert f.__defaults__[0] == "scheme"


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_pmap_function_name_captured_in_lambda() -> None:
    lb_view = _LoadBalancedView()
    magic = _make_pmap_magic(lb_view=lb_view)
    magic.line_pmap("my_special_func", "[]")
    f, _ = lb_view.map_async_calls[0]
    assert f.__defaults__[1] == "my_special_func"


@pytest.mark.skipif(NO_IPYPARALLEL, reason="Requires ipyparallel")
def test_line_pmap_set_variable_stores_result_on_kernel() -> None:
    lb_view = _LoadBalancedView(return_value="result")
    magic = _make_pmap_magic(lb_view=lb_view)
    magic.line_pmap("myfunc", "[1]", set_variable="myvar")
    assert magic.kernel.get_variable("myvar") == "result"
    assert magic.retval is None


# ---------------------------------------------------------------------------
# post_process
# ---------------------------------------------------------------------------


def test_post_process_returns_retval_for_nonempty_truthy_list() -> None:
    magic = _make_pmap_magic()
    magic.retval = [1, 2, 3]
    assert magic.post_process(None) == [1, 2, 3]


def test_post_process_returns_none_for_all_falsy_list() -> None:
    magic = _make_pmap_magic()
    magic.retval = [0, None, False]
    assert magic.post_process(None) is None


def test_post_process_returns_none_for_empty_list() -> None:
    magic = _make_pmap_magic()
    magic.retval = []
    assert magic.post_process(None) is None


def test_post_process_returns_retval_for_non_list() -> None:
    magic = _make_pmap_magic()
    magic.retval = "result"
    assert magic.post_process(None) == "result"


def test_post_process_ignores_retval_argument() -> None:
    magic = _make_pmap_magic()
    magic.retval = "from_self"
    assert magic.post_process("ignored_argument") == "from_self"


def test_post_process_returns_retval_when_any_raises() -> None:
    class _Ambiguous:
        def __bool__(self):
            raise ValueError("ambiguous truth value")

    magic = _make_pmap_magic()
    magic.retval = [_Ambiguous()]
    assert magic.post_process(None) is magic.retval
