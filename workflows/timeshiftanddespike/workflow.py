from nipype import Workflow
from .nodedefs import definednodes
from p3.base import workflowgenerator

class timeshiftanddespikeworkflow(workflowgenerator):
    """ Defines the time shift and despike workflow

        TODO

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # create node definitions from settings
        dn = definednodes(settings)

        # connect the workflow
        cls.workflow.connect([ # connect nodes
            ### Extract Slice timing info + TR
            (dn.inputnode,dn.extract_stc,[
                ('epi','epi')
            ]),

            ### Time Shift/Despiking
            (dn.inputnode,dn.despike,[ # despike
                ('epi','in_file')
            ]),
            (dn.despike,dn.tshift,[ # time shift
                ('out_file','in_file')
            ]),
            (dn.extract_stc,dn.tshift,[
                ('slicetiming','tpattern'),
                ('TR','tr')
            ]),

            ### Setup basefile for motion correction
            (dn.inputnode,dn.firstrunonly,[
                ('epi','epi')
            ]),
            (dn.firstrunonly,dn.extractroi,[
                ('epi','in_file')
            ]),

            ### Do the actual motion correction
            # Align to first frame of first run
            (dn.extractroi,dn.volreg,[
                ('roi_file','basefile')
            ]),
            (dn.tshift,dn.volreg,[
                ('out_file','in_file')
            ]),

            # output to output node
            (dn.volreg,dn.outputnode,[
                ('oned_matrix_save','epi2epi1')
            ]),
            (dn.extractroi,dn.outputnode,[
                ('roi_file','refimg')
            ]),
            (dn.tshift,dn.outputnode,[
                ('out_file','tcat')
            ])
        ])

        # return workflow
        return cls.workflow
