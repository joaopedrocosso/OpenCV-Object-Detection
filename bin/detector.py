import os
import sys
src_pasta = os.path.join(os.path.dirname(__file__), '../src')
sys.path.append(src_pasta)

import runner

runner.main()