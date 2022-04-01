#python examples/FCCee/flavour/generic-analysis/preSel.py

from config.common_defaults import deffccdicts
import os

#basedir=os.path.join(os.getenv('FCCDICTSDIR', deffccdicts), '') + "yaml/FCCee/spring2021/IDEA/"
basedir="/afs/cern.ch/user/g/gguerrie/FCC/FCCAnalyses/"
outdir="/eos/home-g/gguerrie/public/outputs/FCCee/flavour/generic-analysis/test_new_evt_batch/"

import multiprocessing
NUM_CPUS = int(multiprocessing.cpu_count()-2)
process_list=[
    'p8_ee_Zbb_ecm91',
#    'p8_ee_Zbb_ecm91_EvtGen_Bc2TauNuTAUHADNU',    
#    'p8_ee_Zbb_ecm91_EvtGen_Bu2TauNuTAUHADNU',    
#    'p8_ee_Zcc_ecm91',
#    'p8_ee_Zuds_ecm91'
#    'p8_ee_Zbb_ecm91_EvtGen_Bd2KstTauTau'
]

#output_list=['p8_ee_Zbb_ecm91']
output_list=[]

fraction=0.0001
#fraction=0.01

inputana="/afs/cern.ch/user/g/gguerrie/FCC/FCCAnalyses/examples/FCCee/flavour/Afb/analysis/analysis.py"

import config.runDataFrame as rdf
#import config.runDataFrameBatch as rdf
myana=rdf.runDataFrame(basedir,process_list, outlist=output_list)
#myana=rdf.runDataFrameBatch(basedir,process_list, outlist=output_list)


myana.run(ncpu=NUM_CPUS,fraction=fraction, outDir=outdir)
#myana.run(ncpu=NUM_CPUS,fraction=fraction, inputana=inputana, outDir=outdir)
