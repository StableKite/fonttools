import concurrent.futures
import importlib
import sys
import sysconfig
import pytest

pytestmark = pytest.mark.skipif(not sysconfig.get_config_var('Py_GIL_DISABLED'), reason='free-threaded interpreter')
MODULES = ['fontTools.cu2qu.cu2qu', 'fontTools.qu2cu.qu2cu', 'fontTools.misc.bezierTools',
           'fontTools.feaLib.lexer', 'fontTools.pens.momentsPen', 'fontTools.varLib.iup']

def test_native_imports_keep_default_gil_disabled():
    assert 'gil' not in sys._xoptions
    assert not sys._is_gil_enabled()
    for name in MODULES:
        module = importlib.import_module(name)
        assert module.__file__.endswith('.so')
        assert not sys._is_gil_enabled()

def test_independent_native_moment_pens_run_concurrently():
    from fontTools.pens.momentsPen import MomentsPen
    def calculate(index):
        pen = MomentsPen(None)
        pen.moveTo((0, 0))
        pen.lineTo((4, 0))
        pen.lineTo((4, 2))
        pen.lineTo((0, 2))
        pen.closePath()
        return (pen.area, pen.momentX, pen.momentY)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(calculate, range(256))) == [(8, 16, 8)] * 256
    assert not sys._is_gil_enabled()

def test_independent_lexers_and_curve_conversions_run_concurrently():
    from fontTools.feaLib.lexer import Lexer
    from fontTools.cu2qu.cu2qu import curve_to_quadratic
    curve = [(0, 0), (10, 50), (40, 40), (50, 0)]
    def calculate(index):
        tokens = [(kind, text) for kind, text, location in Lexer('feature liga { sub f i by fi; } liga;', 'test.fea')]
        return tokens, curve_to_quadratic(curve, 1)
    expected = calculate(0)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        assert all(row == expected for row in pool.map(calculate, range(128)))
    assert not sys._is_gil_enabled()
