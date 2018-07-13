from nipype import Workflow
from .nodedefs import definednodes
from ppp.base import workflowgenerator

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

            # Setup basefile for motion correction (pre-stc/despike)
            (dn.inputnode,dn.firstrunonly,[
                ('epi','epi')
            ]),
            (dn.firstrunonly,dn.extractroi,[
                ('epi','in_file')
            ]),

            # do motion correction (before stc/despike)
            (dn.extractroi,dn.volreg_before,[
                ('roi_file','basefile')
            ]),
            (dn.inputnode,dn.volreg_before,[
                ('epi','in_file')
            ]),

            # Setup basefile for motion correction (post-stc/despike)
            (dn.stc_despike_pool,dn.firstrunonly_post,[
                ('epi','epi')
            ]),
            (dn.firstrunonly_post,dn.extractroi_post,[
                ('epi','in_file')
            ]),

            ### Do motion correction (after stc/despike)
            # Align to first frame of first run
            (dn.extractroi_post,dn.volreg,[
                ('roi_file','basefile')
            ]),
            (dn.stc_despike_pool,dn.volreg,[
                ('epi','in_file')
            ]),

            # output to output node
            (dn.extractroi,dn.outputnode,[
                ('roi_file','refimg')
            ]),
            (dn.volreg,dn.outputnode,[
                ('out_file','epi_aligned')
            ]),
            (dn.volreg,dn.outputnode,[
                ('oned_matrix_save','epi2epi1')
            ]),
            (dn.stc_despike_pool,dn.outputnode,[
                ('epi','tcat')
            ]),

            # output epi alignments for QC
            (dn.volreg,dn.datasink,[
                ('out_file','p3_QC')
            ]),

            # output motion params to file before/after despike/tshift
            (dn.volreg_before,dn.datasink,[ # before
                ('oned_file','p3.@mocobefore')
            ]),
            (dn.volreg,dn.datasink,[ # after
                ('oned_file','p3.@mocoafter')
            ])
        ])

        # Conditionals for Time Shift/Despiking
        if settings['despiking']:
            cls.workflow.connect([
                (dn.inputnode,dn.despike,[ # despike
                    ('epi','in_file')
                ]),
                (dn.despike,dn.despike_pool,[
                    ('out_file','epi')
                ])
            ])
        else:
            cls.workflow.connect([
                (dn.inputnode,dn.skip_despike,[ # skip despike
                    ('epi','epi')
                ]),
                (dn.skip_despike,dn.despike_pool,[
                    ('epi','epi')
                ])
            ])
        if settings['slice_time_correction']:
            cls.workflow.connect([
                (dn.despike_pool,dn.tshift,[ # time shift
                    ('epi','in_file')
                ]),
                (dn.extract_stc,dn.tshift,[
                    ('slicetiming','tpattern'),
                    ('TR','tr')
                ]),
                (dn.tshift,dn.stc_despike_pool,[
                    ('out_file','epi')
                ]),
            ])
        else:
            cls.workflow.connect([
                (dn.despike_pool,dn.skip_stc,[ # skip time shift
                    ('epi','epi')
                ]),
                (dn.skip_stc,dn.stc_despike_pool,[
                    ('epi','epi')
                ]),
            ])

        # return workflow
        return cls.workflow
