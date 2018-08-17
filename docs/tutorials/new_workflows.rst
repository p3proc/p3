.. _`Creating New Workflows`:

Creating New Workflows
----------------------
The main feature of p3 is to be able to create new workflows and integrate them into your pipeline seamlessly. This
tutorial will show you how to do just that.

1. Create a folder to store your workflows. We'll import this folder later when we want to include our customworkflowworkflow.

   .. code:: bash

        # Here we create a folder called myworkflows in the home directory
        mkdir ~/myworkflows
        cd ~/myworkflows
        touch __init__.py # The generates an __init__.py file, which makes this folder importable

2. Create a new workflow with the **--create_new_workflow** option.

   .. code:: bash

        # We create a new workflow called "customworkflow";
        p3proc --create_new_workflow customworkflow

   This will generate a folder called **customworkflow** in the **myworkflows** directory. Inside the **customworkflow** folder should
   be 4 files:

   **__init__.py**
        makes the workflow importable

   **custom.py**
        stores custom functions for use with a `Function Interface`_

   **nodedefs.py**
        defines nodes of the workflow

   **workflow.py**
        defines the node connections of the workflow and it is what p3 imports

3. Set inputs and outputs to your workflow.

   In order for our workflow to integrate with the rest of the pipeline, it must have input and output fields defined
   to communicate with other workflows. This is done with the **set_input** and **set_output** methods in the **nodedefs.py**
   file. In this example, let's assume we want to do a simple skullstrip of our T1. So our input expects a T1 image and the
   output will be a skullstripped T1 image.

   .. code:: python

        """ nodedefs.py """

        from p3.base import basenodedefs
        from .custom import *

        class definednodes(basenodedefs):
            """
                Initialize nodes here
            """

            def __init__(self,settings):
                # call base constructor
                super().__init__(settings)

                # define input/output nodes
                self.set_input([
                    'T1' # we set this to be a T1 image
                ])
                self.set_output([
                    'skullstripped_T1' # we set this to be a skullstripped image
                ])

   Both the **set_input** and **set_output** methods accept a list as an argument. So you can specify multiple input/
   output fields with a list.

4. Create a node with an interface.

   For our workflow to do something we need to define a node. In p3, nodes are all defined in the **nodedefs.py**
   file and imported into **workflow.py**. These nodes are the same nodes used in nipype_, so all of the interfaces that
   nipype uses, p3 can use as well.

   Continuing with our example let's use FSL's skullstrip in our workflow. To do this we create a node and apply the fsl.BET
   interface to it (Don't forget the import statement at the top!).

   .. code:: python

        """ nodedefs.py """

        from p3.base import basenodedefs
        from .custom import *
        from nipype.interfaces import fsl # DON'T FORGET ME OuO!

        class definednodes(basenodedefs):
            """
                Initialize nodes here
            """

            def __init__(self,settings):
                # call base constructor
                super().__init__(settings)

                # define input/output nodes
                self.set_input([
                    'T1' # we set this to be a T1 image
                ])
                self.set_output([
                    'skullstripped_T1' # we set this to be a skullstripped image
                ])

                # Define our fsl skullstrip node
                self.fsl_skullstrip = Node(
                    fsl.BET(), # we use the fsl BET interface
                    name='fsl_skullstrip' # this names the node
                )

   You can read more about nodes and interfaces at the nipype_ documentation.

5. Connect the nodes together.

   Now we need to connect our workflow's nodes together. This will tell the workflow how data should be passed
   from node to node. In our example, we want our workflow the "T1" image from the input to be passed to the
   "skullstripped_T1" output. This is done in the **workflow.py** file.

   .. code:: python

        """ workflow.py """

        from nipype import Workflow
        from .nodedefs import definednodes
        from p3.base import workflowgenerator

        class newworkflow(workflowgenerator):
            """ newworkflow

                Description goes here

            """

            def __new__(cls,name,settings):
                # call base constructor
                super().__new__(cls,name,settings)

                # create node definitions from settings
                dn = definednodes(settings)

                # connect the workflow
                cls.workflow.connect([
                    # node connections go here
                ])

                # return workflow
                return cls.workflow

   Let's add in the connections.

   .. code:: python

        """ workflow.py """

        from nipype import Workflow
        from .nodedefs import definednodes
        from p3.base import workflowgenerator

        class newworkflow(workflowgenerator):
            """ newworkflow

                Description goes here

            """

            def __new__(cls,name,settings):
                # call base constructor
                super().__new__(cls,name,settings)

                # create node definitions from settings
                dn = definednodes(settings)

                # connect the workflow
                cls.workflow.connect([
                    (dn.inputnode,dn.fsl_skullstrip,[
                        ('T1','in_file') # this sets the T1 field or our input to the in_file of the BET interface
                    ]),
                    (dn.inputnode,dn.fsl_skullstrip,[
                        ('out_file','skullstripped_T1') # this sets the out_file of the BET interface to the skullstripped_T1 of our output
                    ])
                ])

                # return workflow
                return cls.workflow

  Our simple skullstrip workflow is now ready for use!

6. Import the workflow and register the connections in the settings file.

   First, create a settings file.

   .. code:: bash

        # This is for native install, use mounts if using docker/singularity
        p3proc -g settings.json


   Now we need to edit our settings file to include our new workflow.

   .. code:: bash

        # Under the "workflows" key of settings.json
        "workflows": [
            "p3_bidsselector",
            "p3_freesurfer",
            "p3_skullstrip",
            "p3_stcdespikemoco",
            "p3_fieldmapcorrection",
            "p3_alignanattoatlas",
            "p3_alignfunctoanat",
            "p3_alignfunctoatlas",
            "p3_create_fs_masks",
            "customworkflow" # This uses the workflow's folder name!
        ],

   To connect it to other workflows, we use the "connection" key of settings.json.

   .. code:: bash

        "connections": [
            {
                "source": "p3_bidsselector",
                "destination": "customworkflow",
                "links": [
                    [
                        "output.anat",
                        "input.T1" # this is the T1 input in our custom workflow
                    ]
                ]
            },
            {
                "source": "customworkflow",
                "destination": "p3_alignanattoatlas",
                "links": [
                    [
                        "output.skullstripped_T1", # this is our skullstripped T1 output
                        "input.T1_skullstrip"
                    ]
                ]
            },
            ...
        ]

7. Run p3 with the new workflow.

   Now we can run p3 with the new workflow we've incoporated. To do this use the settings file and
   specify the workflows directory that we made in step 1.

   .. code:: bash

        # run p3
        p3proc ~/dataset ~/output -w ~/myworkflows -s settings.json

   This will run your pipeline with the your custom workflow.

.. include:: ../links.rst
