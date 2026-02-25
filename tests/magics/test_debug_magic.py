from tests.utils import EvalKernel, get_kernel


def test_debug_magic() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""%%debug
print('ok')
""")
