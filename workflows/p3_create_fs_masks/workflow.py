from nipype import Workflow
from .nodedefs import definednodes
from ppp.base import workflowgenerator

class bidsselectorworkflow(workflowgenerator):
    """ Defines the bids selector workflow

        TODO

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # create node definitions from settings
        dn = definednodes(settings)

        # only run if recon all enabled
        if settings['run_recon_all']:
            # connect the workflow
            cls.workflow.connect([ # connect nodes
                # convert aparc+aseg to nii.gz
                (dn.inputnode,dn.mri_convert,[
                    ('aparc_aseg','in_file')
                ]),

                # concatenate warps and warp aparc+aseg
                (dn.inputnode,dn.join_warps,[
                    ('nonlin_warp','nonlin_warp'),
                    ('t1_2t1_2_atlas_transform','t1_2_atlas_transform'),
                    ('fs2mpr','fs2mpr')
                ]),
                (dn.join_warps,dn.aparc_aseg_align,[
                    ('concat_warp','warp')
                ]),
                (dn.mri_convert,dn.aparc_aseg_align,[
                    ('out_file','in_file')
                ]),

                # do stuff to the freesurfer masks...
                (dn.aparc_aseg_align,dn.calc1,[
                    ('out_file','in_file_a')
                ]),
                (dn.inputnode,dn.epi_firstrun,[
                    ('epi_at','epi_at')
                ]),
                (dn.calc1,dn.resample1,[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample1,[
                    ('epi_at','master')
                ]),

                # TODO I need to add the first run epi
                # the major WM compartments, with 4 erosions at the T1 resolution followed by resampling to the BOLD resolution
                (dn.aparc_aseg_align,dn.calc2_wm,[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_wm,dn.calc3_wm[0],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc3_wm[0],dn.calc3_wm[1],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc3_wm[1],dn.calc3_wm[2],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc3_wm[2],dn.calc3_wm[3],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_wm,dn.resample2_wm[0],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_wm[0],[
                    ('epi_at','master')
                ]),
                (dn.calc3_wm[0],dn.resample2_wm[1],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_wm[1],[
                    ('epi_at','master')
                ]),
                (dn.calc3_wm[1],dn.resample2_wm[2],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_wm[2],[
                    ('epi_at','master')
                ]),
                (dn.calc3_wm[2],dn.resample2_wm[3],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_wm[3],[
                    ('epi_at','master')
                ]),
                (dn.calc3_wm[3],dn.resample2_wm[4],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_wm[4],[
                    ('epi_at','master')
                ]),

                # the major CSF compartments, with 4 erosions at the T1 resolution followed by resampling to the BOLD resolution
                (dn.aparc_aseg_align,dn.calc2_csf,[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_csf,dn.calc3_csf[0],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc3_csf[0],dn.calc3_csf[1],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc3_csf[1],dn.calc3_csf[2],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc3_csf[2],dn.calc3_csf[3],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_csf,dn.resample2_csf[0],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_csf[0],[
                    ('epi_at','master')
                ]),
                (dn.calc3_csf[0],dn.resample2_csf[1],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_csf[1],[
                    ('epi_at','master')
                ]),
                (dn.calc3_csf[1],dn.resample2_csf[2],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_csf[2],[
                    ('epi_at','master')
                ]),
                (dn.calc3_csf[2],dn.resample2_csf[3],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_csf[3],[
                    ('epi_at','master')
                ]),
                (dn.calc3_csf[3],dn.resample2_csf[4],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_csf[4],[
                    ('epi_at','master')
                ]),

                # the gray matter ribbon (amygdala and hippocampus need to be added - 17 18 53 54
                (dn.aparc_aseg_align,dn.calc2_gmr,[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_gmr,dn.resample2_gmr,[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_gmr,[
                    ('epi_at','master')
                ]),

                # the cerebellum
                (dn.aparc_aseg_align,dn.calc2_cb,[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_cb,dn.calc3_cb[0],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc3_cb[0],dn.calc3_cb[1],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_cb,dn.resample2_cb[0],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_cb[0],[
                    ('epi_at','master')
                ]),
                (dn.calc3_cb[0],dn.resample2_cb[1],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_cb[1],[
                    ('epi_at','master')
                ]),
                (dn.calc3_cb[1],dn.resample2_cb[2],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_cb[2],[
                    ('epi_at','master')
                ]),

                # the subcortical nuclei
                (dn.aparc_aseg_align,dn.calc2_scn,[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_scn,dn.calc3_scn[0],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc3_scn[0],dn.calc3_scn[1],[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_scn,dn.resample2_scn[0],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_scn[0],[
                    ('epi_at','master')
                ]),
                (dn.calc3_scn[0],dn.resample2_scn[1],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_scn[1],[
                    ('epi_at','master')
                ]),
                (dn.calc3_scn[1],dn.resample2_scn[2],[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_scn[2],[
                    ('epi_at','master')
                ]),

                # all gray matter
                (dn.aparc_aseg_align,dn.calc2_gm,[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_gm,dn.resample2_gm,[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_gm,[
                    ('epi_at','master')
                ])
            ])

        cls.workflow.connect([ # connect nodes
            # create images of the atlas and the MPRAGE and the FS segmentation, resampled to BOLD resolution
            (dn.inputnode,dn.epi_resampled,[
                ('out_file','atlas')
            ]),
            (dn.inputnode,dn.epi_resampled,[
                ('out_file','T1')
            ]),
            (dn.aparc_aseg_align,dn.epi_resampled,[
                ('out_file','aparc_aseg')
            ]),
            (dn.inputnode,dn.epi_resampled,[
                ('epi_at','epi')
            ]),

            # output data to datasink
            (dn.epi_resampled,dn.datasink,[
                ('atlas_epi','fs_masks.@atlas_epi'),
                ('T1_epi','fs_masks.@T1_epi'),
                ('aparc_aseg_epi','fs_masks.@aparc_aseg_epi')
            ])
        ])

        # return workflow
        return cls.workflow
