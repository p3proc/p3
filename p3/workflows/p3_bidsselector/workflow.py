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

        # avg over all anats if enabled
        if settings['avganats']:
            # connect the workflow
            cls.workflow.connect([ # connect nodes
                # align anats to each other
                (dn.selectanat,dn.alignanattoanat,[
                    ('anat_reference','reference'),
                    ('anat_align','in_file')
                ]),
                (dn.selectanat,dn.mergeanatlist,[
                    ('anat_reference','in1'),
                ]),
                (dn.alignanattoanat,dn.mergeanatlist,[
                    ('out_file','in2'),
                ]),
                (dn.mergeanatlist,dn.avganat,[
                    ('out','anat_list'),
                ]),

                # output to output node
                (dn.avganat,dn.outputnode,[
                    ('avg_anat','anat')
                ]),

                # output QC
                (dn.alignanattoanat,dn.datasink,[ # output of each anatomy image to anatomy reference
                    ('out_file','p3_QC.bidsselector.@alignanattoanat')
                ]),
                (dn.selectanat,dn.datasink,[ # ouptut original images for comparison
                    ('anat_align','p3_QC.bidsselector.@originals')
                ]),
                (dn.avganat,dn.datasink,[ # output of average anatomy image
                    ('avg_anat','p3_QC.bidsselector.@avganat')
                ])
            ])
        else: # use only the selected reference frame
            # connect the workflow
            cls.workflow.connect([ # connect nodes
                # output to output node
                (dn.selectanat,dn.outputnode,[
                    ('anat_reference','anat')
                ])
            ])

        # connect nodes common to both options
        cls.workflow.connect([
            # specify subject to process
            (dn.inputnode,dn.bidsselection,[
                ('subject','subject')
            ]),

            # select anat to reference to
            (dn.bidsselection,dn.selectanat,[
                ('anat','anat')
            ]),

            # set outputs
            (dn.bidsselection,dn.outputnode,[
                ('func','func')
            ]),
            (dn.inputnode,dn.outputnode,[
                ('subject','subject')
            ])
        ])

        # return workflow
        return cls.workflow
