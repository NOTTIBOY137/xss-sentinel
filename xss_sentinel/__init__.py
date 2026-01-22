"""XSS Sentinel - ML-powered XSS vulnerability scanner"""

import os
import warnings
import sys
from contextlib import redirect_stderr
from io import StringIO

# Suppress TensorFlow warnings before any imports
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress INFO and WARNING messages

# Suppress TensorFlow deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='tensorflow')
warnings.filterwarnings('ignore', category=DeprecationWarning, module='tf_keras')
warnings.filterwarnings('ignore', message='.*sparse_softmax_cross_entropy.*')
warnings.filterwarnings('ignore', message='.*oneDNN.*')
warnings.filterwarnings('ignore', message='.*The name tf.losses.*')

# Store original stderr for TensorFlow imports
_original_stderr = sys.stderr

__version__ = '0.1.0'
