from nipype import Workflow
from .nodedefs import definednodes
from ..base import workflowgenerator

class timeshiftanddespikeworkflow(workflowgenerator):
    """ Defines the time shift and despike workflow

        TODO

    """

    def __init__(self,name,settings):
        # call base constructor
        super().__init__(name,settings)

        # crete node definitions from settings
        self.dn = definednodes(settings)

        # connect the workflow
        self.workflow.connect([ # connect nodes
            ### Extract Slice timing info + TR
            (self.dn.inputnode,self.dn.extract_stc,[
                ('epi','epi')
            ]),

            ### Time Shift/Despiking
            (self.dn.inputnode,self.dn.despike,[ # despike
                ('epi','in_file')
            ]),
            (self.dn.despike,self.dn.tshift,[ # time shift
                ('out_file','in_file')
            ]),
            (self.dn.extract_stc,self.dn.tshift,[
                ('slicetiming','tpattern'),
                ('TR','tr')
            ]),

            ### Setup basefile for motion correction
            (self.dn.inputnode,self.dn.firstrunonly,[
                ('epi','epi')
            ]),
            (self.dn.firstrunonly,self.dn.extractroi,[
                ('epi','in_file')
            ]),

            ### Do the actual motion correction
            # Align to first frame of first run
            (self.dn.extractroi,self.dn.volreg,[
                ('roi_file','basefile')
            ]),
            (self.dn.tshift,self.dn.volreg,[
                ('out_file','in_file')
            ]),

            # output to output node
            (self.dn.volreg,self.dn.outputnode,[
                ('oned_matrix_save','epi2epi1')
            ]),
            (self.dn.extractroi,self.dn.outputnode,[
                ('roi_file','refimg')
            ]),
            (self.dn.tshift,self.dn.outputnode,[
                ('out_file','tcat')
            ])
        ])
