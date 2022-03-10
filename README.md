Experimental chess data analysis tools, trying to make sense of chess.

### Build lczero python binding

In order to build the lczero python binding, follow the build instructions at https://github.com/LeelaChessZero/lc0#building-and-running-lc0, but specify an additional argument to the build.sh script:

    ./build.sh -Dpython_bindings=true

Then copy the generated library from build/release/ to lczero/ in this project. After that you should be able to import lczero.backend from python3.
