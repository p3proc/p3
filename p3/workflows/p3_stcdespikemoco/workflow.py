from nipype import Workflow
from .nodedefs import definednodes
from p3.base import workflowgenerator

class stcdespikemocoworkflow(workflowgenerator):
    """ Defines the slice time correction, despike, motion correction workflow

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
                ('func','epi')
            ]),

            # Setup basefile for motion correction (pre-stc/despike)
            (dn.inputnode,dn.refrunonly,[
                ('func','epi')
            ]),
            (dn.refrunonly,dn.extractroi,[
                ('epi','in_file')
            ]),

            # do motion correction (before stc/despike)
            (dn.extractroi,dn.moco_before,[
                ('roi_file','basefile')
            ]),
            (dn.inputnode,dn.moco_before,[
                ('func','in_file')
            ]),

            # calculate FD
            (dn.moco_before,dn.calcFD,[
                ('oned_file','moco_params')
            ]),
            (dn.extract_stc,dn.calcFD,[
                ('TR','TR')
            ]),

            # Setup basefile for motion correction (post-stc/despike)
            (dn.stc_despike_pool,dn.refrunonly_post,[
                ('epi','epi')
            ]),
            (dn.refrunonly_post,dn.extractroi_post,[
                ('epi','in_file')
            ]),

            ### Do motion correction (after stc/despike)
            # Align to ref frame of ref run
            (dn.extractroi_post,dn.moco,[
                ('roi_file','fixed_image')
            ]),
            (dn.stc_despike_pool,dn.moco,[
                ('epi','moving_image')
            ]),

            # output to output node
            (dn.extractroi_post,dn.outputnode,[
                ('roi_file','refimg')
            ]),
            (dn.stc_despike_pool,dn.outputnode,[
                ('epi','func_stc_despike')
            ]),
            (dn.moco,dn.outputnode,[
                ('warp','warp_func_2_refimg')
            ]),
            (dn.moco,dn.outputnode,[
                ('warped_img','func_aligned')
            ]),

            # output epi alignments for QC
            (dn.moco,dn.datasink,[
               ('warped_img','p3_QC.stcdespikemoco.@epi_aligned')
            ]),

            # output rigid body transform motion params to file before despike/tshift
            (dn.moco_before,dn.datasink,[ # before
                ('oned_file','p3.@mocobefore')
            ]),
            (dn.calcFD,dn.datasink,[
                ('FD','p3.@FD'), # FD values
                ('tmask','p3.@tmask'), # tmask
                ('filt_moco','p3.@filt_moco'), # filtered moco
                ('filt_FD','p3.@filt_FD'), # filtered FD
                ('filt_tmask','p3.@filt_tmask'), # filtered tmask
            ])
        ])

        # Conditionals for Time Shift/Despiking
        if settings['despiking']:
            cls.workflow.connect([
                (dn.inputnode,dn.despike,[ # despike
                    ('func','in_file')
                ]),
                (dn.despike,dn.despike_pool,[
                    ('out_file','epi')
                ])
            ])
        else:
            cls.workflow.connect([
                (dn.inputnode,dn.skip_despike,[ # skip despike
                    ('func','epi')
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
