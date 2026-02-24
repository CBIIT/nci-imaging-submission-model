# Generates CRDC compatible submission sheets from the NCI Imaging Submission Model

import bento_mdf
import pandas as pd
import os
import argparse

def mdfBuildLoadSheets(mdf):
    loadsheets = {}
    nodes = mdf.nodes
    for node in nodes:
        nodeprops = mdf.nodes[node].props
        nodelist = []
        for prop in nodeprops:
            if 'Template' in mdf.props[(node, prop)].tags:
                # Remove any property that is set to 'Template: No'
                if mdf.props[(node,prop)].tags['Template'].get_attr_dict()['value'] != 'No':
                    nodelist.append(prop)
            else:
                nodelist.append(prop)

        # Now need to add the relationship columns.  There are usually expressed as node.property
        srcedges = mdf.edges_by_src(mdf.nodes[node])
        for srcedge in srcedges:
            # Need to find the destination node:
            dstnode = srcedge.dst.handle
            #Now get the properties for that node
            dstprops = mdf.nodes[dstnode].props
            reqlist = []
            for dstprop in dstprops:
                # Relationship columns are based on key columns in the dst node
                if 'is_key' in mdf.props[(dstnode, dstprop)].get_attr_dict():
                    if mdf.props[(dstnode, dstprop)].get_attr_dict()['is_key'] == 'True':
                        reqlist.append(f"{dstnode}.{dstprop}")
            if len(reqlist) > 0:
                for entry in reqlist:
                    nodelist.insert(0, entry)
            
        nodelist.insert(0, 'type')

        load_df = pd.DataFrame(columns=nodelist)
        loadsheets[node] = load_df
    return loadsheets

def main(args):
    # Get a list of the mdf files from ./model-desc
    mdffiles = []
    for x in os.listdir(args.mdfdir):
        if x.endswith(".yml"):
            #mdffiles.append(x)
            mdffiles.append(f"{args.mdfdir}/{x}")

    # Create the model object
    mdfmodel = bento_mdf.MDF(*mdffiles)
    mdfmodel = mdfmodel.model

    loadsheets = mdfBuildLoadSheets(mdfmodel)
    for node, loadsheet in loadsheets.items():
        filename = f"{args.sheetdir}/{mdfmodel.handle}_Data_Loading_Template_{node}_{mdfmodel.version}.tsv"
        loadsheet.to_csv(filename, sep="\t", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mdfdir", required=True,  help="Directory containing the model MDF files")
    parser.add_argument('-s', '--sheetdir', required=True, help="Diretory where submission sheets should be written")

    args = parser.parse_args()

    main(args)

