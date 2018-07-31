from nipype import Workflow
from .nodedefs import definednodes
from p3.base import workflowgenerator

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
                (dn.inputnode,dn.get_aparc_aseg,[
                    ('aparc_aseg','aparc_aseg')
                ]),
                (dn.get_aparc_aseg,dn.mri_convert,[
                    ('out_file','in_file')
                ]),

                # align freesurfer to anat image
                (dn.inputnode,dn.align_fs_2_anat,[
                    ('T1','fixed_image'),
                    ('orig','moving_image')
                ]),

                # concatenate warps and align aparc+aseg to atlas
                (dn.align_fs_2_anat,dn.join_warps,[
                    ('composite_transform','affine_fs_2_anat')
                ]),
                (dn.inputnode,dn.join_warps,[
                    ('affine_anat_2_atlas','affine_anat_2_atlas'),
                    ('warp_anat_2_atlas','warp_anat_2_atlas')
                ]),
                (dn.join_warps,dn.apply_warp,[
                    ('fs_concat_transform','transform')
                ]),
                (dn.mri_convert,dn.apply_warp,[
                    ('out_file','in_file')
                ]),

                # do stuff to the freesurfer masks...
                (dn.apply_warp,dn.calc1,[
                    ('out_file','in_file_a')
                ]),
                (dn.inputnode,dn.epi_firstrun,[
                    ('func_atlas','epi_at')
                ]),
                (dn.calc1,dn.resample1,[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample1,[
                    ('epi_at','master')
                ]),

                # the major WM compartments, with 4 erosions at the T1 resolution followed by resampling to the BOLD resolution
                (dn.apply_warp,dn.calc2_wm,[
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
                (dn.apply_warp,dn.calc2_csf,[
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
                (dn.apply_warp,dn.calc2_gmr,[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_gmr,dn.resample2_gmr,[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_gmr,[
                    ('epi_at','master')
                ]),

                # the cerebellum
                (dn.apply_warp,dn.calc2_cb,[
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
                (dn.apply_warp,dn.calc2_scn,[
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
                (dn.apply_warp,dn.calc2_gm,[
                    ('out_file','in_file_a')
                ]),
                (dn.calc2_gm,dn.resample2_gm,[
                    ('out_file','in_file')
                ]),
                (dn.epi_firstrun,dn.resample2_gm,[
                    ('epi_at','master')
                ]),

                # resample aparc_aseg
                (dn.apply_warp,dn.epi_resampled,[
                    ('out_file','aparc_aseg')
                ]),

                # output data to datasink
                # white matter
                (dn.resample2_wm[0],dn.datasink,[
                    ('out_file','fs_masks.wm.@wm0')
                ]),
                (dn.resample2_wm[1],dn.datasink,[
                    ('out_file','fs_masks.wm.@wm1')
                ]),
                (dn.resample2_wm[2],dn.datasink,[
                    ('out_file','fs_masks.wm.@wm2')
                ]),
                (dn.resample2_wm[3],dn.datasink,[
                    ('out_file','fs_masks.wm.@wm3')
                ]),
                (dn.resample2_wm[4],dn.datasink,[
                    ('out_file','fs_masks.wm.@wm4')
                ]),
                # CSF
                (dn.resample2_csf[0],dn.datasink,[
                    ('out_file','fs_masks.csf.@csf0')
                ]),
                (dn.resample2_csf[1],dn.datasink,[
                    ('out_file','fs_masks.csf.@csf1')
                ]),
                (dn.resample2_csf[2],dn.datasink,[
                    ('out_file','fs_masks.csf.@csf2')
                ]),
                (dn.resample2_csf[3],dn.datasink,[
                    ('out_file','fs_masks.csf.@csf3')
                ]),
                (dn.resample2_csf[4],dn.datasink,[
                    ('out_file','fs_masks.csf.@csf4')
                ]),
                # Gray Matter Ribbon
                (dn.resample2_gmr,dn.datasink,[
                    ('out_file','fs_masks.gmr.@gmr')
                ]),
                # Cerebellum
                (dn.resample2_cb[0],dn.datasink,[
                    ('out_file','fs_masks.cb.@cb0')
                ]),
                (dn.resample2_cb[1],dn.datasink,[
                    ('out_file','fs_masks.cb.@cb1')
                ]),
                (dn.resample2_cb[2],dn.datasink,[
                    ('out_file','fs_masks.cb.@cb2')
                ]),
                # Subcortical Nuclei
                # Cerebellum
                (dn.resample2_scn[0],dn.datasink,[
                    ('out_file','fs_masks.scn.@scn0')
                ]),
                (dn.resample2_scn[1],dn.datasink,[
                    ('out_file','fs_masks.scn.@scn1')
                ]),
                (dn.resample2_scn[2],dn.datasink,[
                    ('out_file','fs_masks.scn.@scn2')
                ]),
                # All gray matter
                (dn.resample2_gm,dn.datasink,[
                    ('out_file','fs_masks.gm.@gm')
                ]),
                # aparc+aseg
                (dn.epi_resampled,dn.datasink,[
                    ('aparc_aseg_epi','fs_masks.aparc_aseg.@aparc_aseg_epi')
                ])
            ])

        cls.workflow.connect([ # connect nodes
            # create images of the atlas and the MPRAGE and the FS segmentation, resampled to BOLD resolution
            (dn.inputnode,dn.epi_resampled,[
                ('anat_atlas','T1')
            ]),
            (dn.inputnode,dn.epi_resampled,[
                ('func_atlas','epi')
            ]),

            # output data to datasink
            (dn.epi_resampled,dn.datasink,[
                ('T1_epi','p3.@T1_epi')
            ])
        ])

        # return workflow
        return cls.workflow
