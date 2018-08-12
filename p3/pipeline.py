import inspect
from nipype import Workflow,config,logging
from .base import workflowgenerator
from shutil import copy2
import os

def create_and_run_p3_workflow(imported_workflows,settings):
    """
        Create main workflow
    """

    # Set nipype debug messages if enabled
    if settings['debug']:
        config.set('logging','workflow_level','DEBUG')
        config.set('logging','workflow_level','DEBUG')
    # always hash on content
    config.set('execution','hash_method','content')
    # stop on first crash
    config.set('execution','stop_on_first_crash','true')
    logging.update_logging(config)

    # define subworkflows from imported workflows
    subworkflows = generate_subworkflows(imported_workflows,settings)

    # create a workflow
    p3 = Workflow(name='p3_pipeline',base_dir=settings['tmp_dir'])

    # get connections
    connections = generate_connections(subworkflows,settings)

    # connect nodes
    p3.connect(connections)

    # apply sideloads
    sideload_nodes(p3,connections,settings)

    # Create graph images
    p3.write_graph(graph2use='flat',simple_form=False)
    p3.write_graph(graph2use='colored')

    # copy the grpah files to the output directory
    copy2(os.path.join(settings['tmp_dir'],'p3_pipeline','graph.png'),settings['output_dir'])
    copy2(os.path.join(settings['tmp_dir'],'p3_pipeline','graph_detailed.png'),settings['output_dir'])

    # Run pipeline (check multiproc setting)
    if not settings['disable_run']:
        if settings['multiproc']:
            p3.run(plugin='MultiProc')
        else:
            p3.run()

def sideload_nodes(p3,connections,settings):
    """
        Sideload values into nodes
    """
    # loop over sideload list and set the input for the node
    for sideload in settings['sideload']:
        # construct the node name
        nodename = '{}.{}'.format(sideload['workflow'],sideload['node'])
        # set the input for the selected field
        p3.get_node(nodename).set_input(sideload['input'][0],sideload['input'][1])

        # get edge list for the entire pipeline
        edge_list = p3._graph.edges
        # find edges of the destination node whose input we are overriding
        edge_dest = [edge for edge in edge_list if edge[1].name == sideload['workflow']]
        for edge in edge_dest:
            edge_data = p3._graph.get_edge_data(*edge) # get edge data
            # check if the connection contains the field we are trying to replace
            for connection in edge_data['connect']:
                # disconnect the nodes if it is the field we are replacing
                if connection[1] == '{}.{}'.format(sideload['node'],sideload['input'][0]):
                    p3.disconnect(edge[0],connection[0],edge[1],connection[1])
                    print('Disconnect: {}'.format((edge[0].name,connection[0],edge[1].name,connection[1])))

        # get the edge list for the workflow
        edge_list = p3.get_node(sideload['workflow'])._graph.edges
        # find edges of the destination node whose input we are overriding
        edge_dest = [edge for edge in edge_list if edge[1].name == sideload['node']]
        # loop through each edge pair and check if the field we are side loading exists with that pair
        for edge in edge_dest:
            edge_data = p3.get_node(sideload['workflow'])._graph.get_edge_data(*edge) # get edge data
            # check if the connection contains the field we are trying to replace
            for connection in edge_data['connect']:
                # disconnect the nodes if it is the field we are replacing
                if connection[1] == '{}'.format(sideload['input'][0]):
                    p3.get_node(sideload['workflow']).disconnect(edge[0],connection[0],edge[1],connection[1])
                    print('Disconnect: {}'.format((edge[0].name,connection[0],edge[1].name,connection[1])))

        # print sideload status
        print('\nSideload Status for node {}.{}:'.format(sideload['workflow'],sideload['node']))
        print(p3.get_node('{}.{}'.format(sideload['workflow'],sideload['node'])).inputs)

def generate_subworkflows(imported_workflows,settings):
    """
        TODO: document this function
    """

    # create sub-workflows
    subworkflows = {}
    # loop over all imported workflows
    for name,wf in imported_workflows.items():
        # find the class whos base is the workflowgenerator
        for obj in dir(wf):
            if inspect.isclass(getattr(wf,obj)): # check if object is class
                # the object is a workflowgenerator object
                if getattr(wf,obj).__bases__[0] == workflowgenerator:
                    # create and assign the workflow to the dictionary
                    subworkflows[name] = getattr(wf,obj)(name,settings)

    # return subworkflows
    return subworkflows

def generate_connections(subworkflows,settings):
    """
        TODO: document this function
    """

    # define initial connection list
    connections = []

    # go through connections in settings and build connections list
    for connection_entry in settings['connections']:
        # append to connections list
        connections.append(( # define tuple
            subworkflows[connection_entry['source']],
            subworkflows[connection_entry['destination']],
            [tuple(link) for link in connection_entry['links']] # convert each entry in links list to tuple
        ))

    # return connection list
    return connections
