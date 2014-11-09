
from metakernel.tests.utils import (get_kernel, get_log_text, EvalKernel,
                                    clear_log_text)


def test_spell_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""%%spell testme
print("ok")
    """, False)
    kernel.do_execute("%spell testme", False)
    text = get_log_text(kernel)
    assert "ok" in text, text
    clear_log_text(kernel)

    kernel.do_execute("%spell -l learned", False)
    text = get_log_text(kernel)
    assert "testme" in text, text
    clear_log_text(kernel)

    kernel.do_execute("%spell -d testme", False)
    kernel.do_execute("%spell -l learned", False)
    text = get_log_text(kernel)
    assert "testme" not in text, text
    clear_log_text(kernel)

    
