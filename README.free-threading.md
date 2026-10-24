# Free-threaded source builds

FontTools 4.67.0 already requests Cython freethreading_compatible=True. Its
cached generated C can nevertheless be older than that configuration. On a
free-threaded interpreter, regenerate all six accelerators with Cython>=3.3
inside the ordinary isolated pip build. No accelerators are removed and no
consumer flags are needed. Individual mutable Lexer/Pen objects retain their
normal single-owner contract; independent instances can run concurrently.
