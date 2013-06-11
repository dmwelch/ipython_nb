# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Nipype helper code and misc examples/functions

# <codecell>

def examineNode(filename):
    """ Load a .plkz file and print out important information.  Return the node object """
    import pickle
    import pprint
    import gzip
    
    try:
        in_file = gzip.open(filename)
        temp = pickle.load(in_file)
    except ImportError, err:
        raise ImportError('Please add path to module %s to PYTHONPATH' % err.message.split(' ')[-1])
    finally:
        in_file.close()
    print(temp)
    # pprintint.pprint(temp.inputs)
    # pprint.pprint(temp.outputs)
    # out = temp.interface._list_outputs()
    # pprint.pprint(out)
    # pprint.pprint(temp.outputs)
    # temp.inputs.trait_view
    # temp.interface.input
    # temp.interface._format_arg('in_file', temp.inputs.trait, temp.inputs.in_file)
    return temp

# <headingcell level=2>

# Example use of examineNode

# <codecell>

node = examineNode('rsDataSink/_node.pklz')
node.inputs
#node.outputs

