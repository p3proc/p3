"""Define Nodes for time shift and despike workflow

TODO

"""
from ..nodedefs import basenodedefs

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    # call base constructor
    super().__init__(settings)

    # Create transform
    self.transformepi2epi2mpr2atl = MapNode(
        Function(
            input_names=['in_file','tfm1','tfm2','tfm3'],
            output_names=['master_transform'],
            function=concattransform
        ),
        iterfield=['tfm3'],
        name='transformepi2epi2mpr2atl'
    )

    # align images
    self.alignepi2atl = MapNode(
        afni.Allineate(
            args='-mast_dxyz 3',
            overwrite=True,
            outputtype='NIFTI_GZ'
        ),
        iterfield=['in_matrix','in_file'],
        name='alignepi2atl'
    )
