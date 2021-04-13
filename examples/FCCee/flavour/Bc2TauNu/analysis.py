import sys
import ROOT

print ("Load cxx analyzers ... ",)
ROOT.gSystem.Load("libedm4hep")
ROOT.gSystem.Load("libpodio")
ROOT.gSystem.Load("libawkward")
ROOT.gSystem.Load("libawkward-cpu-kernels")
ROOT.gSystem.Load("libFCCAnalyses")

ROOT.gErrorIgnoreLevel = ROOT.kFatal
_edm  = ROOT.edm4hep.ReconstructedParticleData()
_pod  = ROOT.podio.ObjectID()
_fcc  = ROOT.dummyLoader

print ('edm4hep  ',_edm)
print ('podio    ',_pod)
print ('fccana   ',_fcc)


ROOT.gInterpreter.ProcessLine('''
TMVA::Experimental::RBDT<> bdt("Bc2TauNu_BDT", "/eos/experiment/fcc/ee/analyses/case-studies/flavour/Bc2TauNu/xgb_bdt.root");

computeModel = TMVA::Experimental::Compute<10, float>(bdt);
''')


class analysis():

    #__________________________________________________________
    def __init__(self, inputlist, outname, ncpu):
        self.outname = outname
        if ".root" not in outname:
            self.outname+=".root"

        ROOT.ROOT.EnableImplicitMT(ncpu)
        ROOT.EnableThreadSafety()
        self.df = ROOT.RDataFrame("events", inputlist)
        print (" done")
    #__________________________________________________________
    def run(self):
        #84702
        #df2 = (self.df.Range(1000)
        
        df2 = (self.df
               .Alias("MCRecoAssociations0", "MCRecoAssociations#0.index")
               .Alias("MCRecoAssociations1", "MCRecoAssociations#1.index")
               .Alias("Particle0", "Particle#0.index")

               .Define("RP_e",          "ReconstructedParticle::get_e(ReconstructedParticles)")
               .Define("RP_px",         "ReconstructedParticle::get_px(ReconstructedParticles)")
               .Define("RP_py",         "ReconstructedParticle::get_py(ReconstructedParticles)")
               .Define("RP_pz",         "ReconstructedParticle::get_pz(ReconstructedParticles)")
               .Define("RP_charge",     "ReconstructedParticle::get_charge(ReconstructedParticles)")
              
               .Define('EVT_thrust',          'Algorithms::minimize_thrust("Minuit2","Migrad")(RP_px, RP_py, RP_pz)')
               .Define('RP_thrustangle',      'Algorithms::getAxisCosTheta(EVT_thrust, RP_px, RP_py, RP_pz)')

               #hemis0 == negative angle, hemis1 == positive angle
               .Define('EVT_thrusthemis0_n',         'Algorithms::getAxisN(0)(RP_thrustangle, RP_charge)')
               .Define('EVT_thrusthemis1_n',         'Algorithms::getAxisN(1)(RP_thrustangle, RP_charge)')
               .Define('EVT_thrusthemis0_e',         'Algorithms::getAxisEnergy(0)(RP_thrustangle, RP_charge, RP_e)')
               .Define('EVT_thrusthemis1_e',         'Algorithms::getAxisEnergy(1)(RP_thrustangle, RP_charge, RP_e)')
               .Define('EVT_thrutshemis0_ncharged',  'EVT_thrusthemis0_n.at(1)')
               .Define('EVT_thrutshemis0_nneutral',  'EVT_thrusthemis0_n.at(2)')
               .Define('EVT_thrutshemis0_echarged',  'EVT_thrusthemis0_e.at(1)')
               .Define('EVT_thrutshemis0_eneutral',  'EVT_thrusthemis0_e.at(2)')
               .Define('EVT_thrutshemis1_ncharged',  'EVT_thrusthemis1_n.at(1)')
               .Define('EVT_thrutshemis1_nneutral',  'EVT_thrusthemis1_n.at(2)')
               .Define('EVT_thrutshemis1_echarged',  'EVT_thrusthemis1_e.at(1)')
               .Define('EVT_thrutshemis1_eneutral',  'EVT_thrusthemis1_e.at(2)')

               .Define('EVT_thrusthemis_emax','if (EVT_thrusthemis0_e.at(0)>EVT_thrusthemis1_e.at(0)) return EVT_thrusthemis0_e.at(0); else return EVT_thrusthemis1_e.at(0);')
               .Define('EVT_thrusthemis_emin','if (EVT_thrusthemis0_e.at(0)>EVT_thrusthemis1_e.at(0)) return EVT_thrusthemis1_e.at(0); else return EVT_thrusthemis0_e.at(0);')
               
               .Define('EVT_Echarged_max', 'if (EVT_thrutshemis0_echarged>EVT_thrutshemis1_echarged) return EVT_thrutshemis0_echarged; else return EVT_thrutshemis1_echarged')
               .Define('EVT_Echarged_min', 'if (EVT_thrutshemis0_echarged>EVT_thrutshemis1_echarged) return EVT_thrutshemis1_echarged; else return EVT_thrutshemis0_echarged')
               .Define('EVT_Eneutral_max', 'if (EVT_thrutshemis0_eneutral>EVT_thrutshemis1_eneutral) return EVT_thrutshemis0_eneutral; else return EVT_thrutshemis1_eneutral')
               .Define('EVT_Eneutral_min', 'if (EVT_thrutshemis0_eneutral>EVT_thrutshemis1_eneutral) return EVT_thrutshemis1_eneutral; else return EVT_thrutshemis0_eneutral')

               .Define('EVT_Ncharged_max','if (EVT_thrutshemis0_ncharged>EVT_thrutshemis1_ncharged) return float(EVT_thrutshemis0_ncharged); else return float(EVT_thrutshemis1_ncharged)')
               .Define('EVT_Ncharged_min','if (EVT_thrutshemis0_ncharged>EVT_thrutshemis1_ncharged) return float(EVT_thrutshemis1_ncharged); else return float(EVT_thrutshemis0_ncharged)')
               .Define('EVT_Nneutral_max','if (EVT_thrutshemis0_nneutral>EVT_thrutshemis1_nneutral) return float(EVT_thrutshemis0_nneutral); else return float(EVT_thrutshemis1_nneutral)')
               .Define('EVT_Nneutral_min','if (EVT_thrutshemis0_nneutral>EVT_thrutshemis1_nneutral) return float(EVT_thrutshemis1_nneutral); else return float(EVT_thrutshemis0_nneutral)')

               
               
               .Define("MVAVec", ROOT.computeModel, ("EVT_thrusthemis_emin", "EVT_thrusthemis_emax", "EVT_Echarged_min", "EVT_Echarged_max", "EVT_Eneutral_min",
                                                     "EVT_Eneutral_max", "EVT_Ncharged_min", "EVT_Ncharged_max", "EVT_Nneutral_min", "EVT_Nneutral_max"))
               .Define("MVA", "MVAVec.at(0)")
               #.Filter("MVA>0.1")
               
               #MC Vertex
               .Define("MCVertexObject", "myUtils::get_MCVertexObject(Particle, Particle0)")
               .Define("MC_Vertex_x",    "myUtils::get_MCVertex_x(MCVertexObject)")
               .Define("MC_Vertex_y",    "myUtils::get_MCVertex_y(MCVertexObject)")
               .Define("MC_Vertex_z",    "myUtils::get_MCVertex_z(MCVertexObject)")
               .Define("MC_Vertex_ind",  "myUtils::get_MCindMCVertex(MCVertexObject)")
               .Define("MC_Vertex_ntrk", "myUtils::get_NTracksMCVertex(MCVertexObject)")
               .Define("MC_Vertex_n",    "int(MC_Vertex_x.size())")

               #Reco Vertex
               .Define("VertexObject", "myUtils::get_VertexObject(MCVertexObject,ReconstructedParticles,EFlowTrack_1,MCRecoAssociations0,MCRecoAssociations1)")
               .Define("Vertex_x",     "myUtils::get_Vertex_x(VertexObject)")
               .Define("Vertex_y",     "myUtils::get_Vertex_y(VertexObject)")
               .Define("Vertex_z",     "myUtils::get_Vertex_z(VertexObject)")
               .Define("Vertex_xErr",  "myUtils::get_Vertex_xErr(VertexObject)")
               .Define("Vertex_yErr",  "myUtils::get_Vertex_yErr(VertexObject)")
               .Define("Vertex_zErr",  "myUtils::get_Vertex_zErr(VertexObject)")

               .Define("Vertex_chi2",  "myUtils::get_Vertex_chi2(VertexObject)")
               .Define("Vertex_mcind", "myUtils::get_Vertex_indMC(VertexObject)")
               .Define("Vertex_ind",   "myUtils::get_Vertex_ind(VertexObject)")
               .Define("Vertex_isPV",  "myUtils::get_Vertex_isPV(VertexObject)")
               .Define("Vertex_ntrk",  "myUtils::get_Vertex_ntracks(VertexObject)")
               .Define("Vertex_n",     "int(Vertex_x.size())")

               .Define("Vertex_d2PV",  "myUtils::get_Vertex_d2PV(VertexObject,-1)")
               .Define("Vertex_d2PVx", "myUtils::get_Vertex_d2PV(VertexObject,0)")
               .Define("Vertex_d2PVy", "myUtils::get_Vertex_d2PV(VertexObject,1)")
               .Define("Vertex_d2PVz", "myUtils::get_Vertex_d2PV(VertexObject,2)")
               
               .Define("Vertex_d2PVErr", "myUtils::get_Vertex_d2PVError(VertexObject,-1)")
               .Define("Vertex_d2PVxErr","myUtils::get_Vertex_d2PVError(VertexObject,0)")
               .Define("Vertex_d2PVyErr","myUtils::get_Vertex_d2PVError(VertexObject,1)")
               .Define("Vertex_d2PVzErr","myUtils::get_Vertex_d2PVError(VertexObject,2)")
               
               .Define("Vertex_d2PVSig",  "Vertex_d2PV/Vertex_d2PVErr")
               .Define("Vertex_d2PVxSig", "Vertex_d2PVx/Vertex_d2PVxErr")
               .Define("Vertex_d2PVySig", "Vertex_d2PVy/Vertex_d2PVyErr")
               .Define("Vertex_d2PVzSig", "Vertex_d2PVz/Vertex_d2PVzErr")

               .Define("Vertex_d2MC",   "myUtils::get_Vertex_d2MC(VertexObject,MCVertexObject,Vertex_mcind,-1)")
               .Define("Vertex_d2MCx",  "myUtils::get_Vertex_d2MC(VertexObject,MCVertexObject,Vertex_mcind,0)")
               .Define("Vertex_d2MCy",  "myUtils::get_Vertex_d2MC(VertexObject,MCVertexObject,Vertex_mcind,1)")
               .Define("Vertex_d2MCz",  "myUtils::get_Vertex_d2MC(VertexObject,MCVertexObject,Vertex_mcind,2)")

               .Define("RecoPartPID" ,"myUtils::PID(ReconstructedParticles, MCRecoAssociations0,MCRecoAssociations1,Particle)")
               .Define("RecoPartPIDAtVertex" ,"myUtils::get_RP_atVertex(RecoPartPID, VertexObject)")
               
               #build_tau23pi(float arg_masslow, float arg_masshigh, float arg_p, float arg_angle, bool arg_rho)
               .Define("Tau23PiCandidates",         "myUtils::build_tau23pi(VertexObject,RecoPartPIDAtVertex)")
               .Define("Tau23PiCandidates_n",       "myUtils::getFCCAnalysesComposite_N(Tau23PiCandidates)")
               .Define("Tau23PiCandidates_mass",    "myUtils::getFCCAnalysesComposite_mass(Tau23PiCandidates)")
               .Define("Tau23PiCandidates_q",       "myUtils::getFCCAnalysesComposite_charge(Tau23PiCandidates)")
               .Define("Tau23PiCandidates_vertex",  "myUtils::getFCCAnalysesComposite_vertex(Tau23PiCandidates)")
               .Define("Tau23PiCandidates_mcvertex","myUtils::getFCCAnalysesComposite_mcvertex(Tau23PiCandidates,VertexObject)")
               .Define("Tau23PiCandidates_px",      "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates,0)")
               .Define("Tau23PiCandidates_py",      "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates,1)")
               .Define("Tau23PiCandidates_pz",      "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates,2)")
               .Define("Tau23PiCandidates_p",       "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates,-1)")
               .Define("Tau23PiCandidates_B",       "myUtils::getFCCAnalysesComposite_B(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex)")
               
               .Define("Tau23PiCandidates_track",   "myUtils::getFCCAnalysesComposite_track(Tau23PiCandidates, VertexObject)")
               .Define("Tau23PiCandidates_d0",      "myUtils::get_trackd0(Tau23PiCandidates_track)")
               .Define("Tau23PiCandidates_z0",      "myUtils::get_trackz0(Tau23PiCandidates_track)")

               .Define("Tau23PiCandidates_rho",    "myUtils::build_rho(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex)")
               .Define("Tau23PiCandidates_rho1mass","myUtils::get_mass(Tau23PiCandidates_rho, 0)")
               .Define("Tau23PiCandidates_rho2mass","myUtils::get_mass(Tau23PiCandidates_rho, 1)")

               
               .Define("Tau23PiCandidates_pion1px", "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 0, 0)")
               .Define("Tau23PiCandidates_pion1py", "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 0, 1)")
               .Define("Tau23PiCandidates_pion1pz", "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 0, 2)")
               .Define("Tau23PiCandidates_pion1p",  "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 0, -1)")
               .Define("Tau23PiCandidates_pion1q",  "myUtils::getFCCAnalysesComposite_q(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 0)")
               .Define("Tau23PiCandidates_pion1d0", "myUtils::getFCCAnalysesComposite_d0(Tau23PiCandidates, VertexObject, 0)")
               .Define("Tau23PiCandidates_pion1z0", "myUtils::getFCCAnalysesComposite_z0(Tau23PiCandidates, VertexObject, 0)")
               
               .Define("Tau23PiCandidates_pion2px", "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 1, 0)")
               .Define("Tau23PiCandidates_pion2py", "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 1, 1)")
               .Define("Tau23PiCandidates_pion2pz", "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 1, 2)")
               .Define("Tau23PiCandidates_pion2p",  "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 1, -1)")
               .Define("Tau23PiCandidates_pion2q",  "myUtils::getFCCAnalysesComposite_q(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 1)")
               .Define("Tau23PiCandidates_pion2d0", "myUtils::getFCCAnalysesComposite_d0(Tau23PiCandidates, VertexObject, 1)")
               .Define("Tau23PiCandidates_pion2z0", "myUtils::getFCCAnalysesComposite_z0(Tau23PiCandidates, VertexObject, 1)")
               
               .Define("Tau23PiCandidates_pion3px", "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 2, 0)")
               .Define("Tau23PiCandidates_pion3py", "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 2, 1)")
               .Define("Tau23PiCandidates_pion3pz", "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 2, 2)")
               .Define("Tau23PiCandidates_pion3p",  "myUtils::getFCCAnalysesComposite_p(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 2, -1)")
               .Define("Tau23PiCandidates_pion3q",  "myUtils::getFCCAnalysesComposite_q(Tau23PiCandidates, VertexObject, RecoPartPIDAtVertex, 2)")
               .Define("Tau23PiCandidates_pion3d0", "myUtils::getFCCAnalysesComposite_d0(Tau23PiCandidates, VertexObject, 2)")
               .Define("Tau23PiCandidates_pion3z0", "myUtils::getFCCAnalysesComposite_z0(Tau23PiCandidates, VertexObject, 2)")

               .Define("TrueTau23Pi_vertex",        "myUtils::get_trueVertex(MCVertexObject,Particle,Particle0, 15, 541)")
               .Define("TrueTau23Pi_track",         "myUtils::get_truetrack(TrueTau23Pi_vertex, MCVertexObject, Particle)")
               .Define("TrueTau23Pi_d0",            "myUtils::get_trackd0(TrueTau23Pi_track)")
               .Define("TrueTau23Pi_z0",            "myUtils::get_trackz0(TrueTau23Pi_track)")

               #.Define('RP2MC',                    "ReconstructedParticle2MC::getRP2MC_index(MCRecoAssociations0,MCRecoAssociations1,RecoPartPIDAtVertex)") 
               #.Define("Tau23PiCandidatesTM",      "myUtils::add_truthmatched2(Tau23PiCandidates, Particle, VertexObject, RP2MC, RecoPartPIDAtVertex, Particle0)")
               #.Define("Tau23PiCandidates_tm",     "myUtils::getFCCAnalysesComposite_truthMatch(Tau23PiCandidatesTM)")

               .Define("Vertex_thrusthemis_angle",   "myUtils::get_Vertex_thrusthemis_angle(VertexObject, RecoPartPIDAtVertex, EVT_thrust)")
               #hemis0 == negative angle, hemis1 == positive angle
               .Define("Vertex_thrusthemis_emin",    "myUtils::get_Vertex_thrusthemis_emin(Vertex_thrusthemis_angle, EVT_thrusthemis0_e.at(0), EVT_thrusthemis1_e.at(0))")

               
               
           )
        # select branches for output file
        branchList = ROOT.vector('string')()
        for branchName in [

                "EVT_thrusthemis_emin", "EVT_thrusthemis_emax",
                "EVT_Echarged_min", "EVT_Echarged_max",
                "EVT_Eneutral_min", "EVT_Eneutral_max",
                "EVT_Ncharged_min", "EVT_Ncharged_max",
                "EVT_Nneutral_min", "EVT_Nneutral_max",

                "MC_Vertex_x", "MC_Vertex_y", "MC_Vertex_z", 
                "MC_Vertex_ntrk", "MC_Vertex_n",
                
                "Vertex_x", "Vertex_y", "Vertex_z",
                "Vertex_xErr", "Vertex_yErr", "Vertex_zErr",
                "Vertex_isPV", "Vertex_ntrk", "Vertex_chi2", "Vertex_n",
                "Vertex_thrusthemis_angle", "Vertex_thrusthemis_emin",

                "Vertex_d2PV", "Vertex_d2PVx", "Vertex_d2PVy", "Vertex_d2PVz",
                "Vertex_d2PVErr", "Vertex_d2PVxErr", "Vertex_d2PVyErr", "Vertex_d2PVzErr",
                
                "MVA",

                "TrueTau23Pi_vertex","TrueTau23Pi_d0","TrueTau23Pi_z0",
                
                "Tau23PiCandidates_n", "Tau23PiCandidates_mass", "Tau23PiCandidates_vertex", "Tau23PiCandidates_mcvertex", "Tau23PiCandidates_B",
                "Tau23PiCandidates_px", "Tau23PiCandidates_px", "Tau23PiCandidates_pz", "Tau23PiCandidates_p", "Tau23PiCandidates_q",  "Tau23PiCandidates_d0",  "Tau23PiCandidates_z0",
                #"Tau23PiCandidates_rho1px", "Tau23PiCandidates_rho1py", "Tau23PiCandidates_rho1pz",
                "Tau23PiCandidates_rho1mass",
                #"Tau23PiCandidates_rho2px", "Tau23PiCandidates_rho2py", "Tau23PiCandidates_rho2pz",
                "Tau23PiCandidates_rho2mass",
                
                "Tau23PiCandidates_pion1px", "Tau23PiCandidates_pion1px", "Tau23PiCandidates_pion1pz", "Tau23PiCandidates_pion1p", "Tau23PiCandidates_pion1q", "Tau23PiCandidates_pion1d0", "Tau23PiCandidates_pion1z0",
                "Tau23PiCandidates_pion2px", "Tau23PiCandidates_pion2px", "Tau23PiCandidates_pion2pz", "Tau23PiCandidates_pion2p", "Tau23PiCandidates_pion2q", "Tau23PiCandidates_pion2d0", "Tau23PiCandidates_pion2z0",
                "Tau23PiCandidates_pion3px", "Tau23PiCandidates_pion3px", "Tau23PiCandidates_pion3pz", "Tau23PiCandidates_pion3p", "Tau23PiCandidates_pion3q", "Tau23PiCandidates_pion3d0", "Tau23PiCandidates_pion3z0",
                

                
                ]:
            branchList.push_back(branchName)

        #opts = ROOT.RDF.RSnapshotOptions()
        #opts.fCompressionAlgorithm = ROOT.ROOT.kLZ4
        #opts.fCompressionLevel = 3
        #opts.fAutoFlush = -1024*1024*branchList.size()
        #df2.Snapshot("events", self.outname, branchList, opts)
        df2.Snapshot("events", self.outname, branchList)

# example call for standalone file
# python examples/FCCee/flavour/Bc2TauNu/analysis.py  /eos/experiment/fcc/ee/generation/DelphesEvents/fcc_tmp_v03/p8_ee_Zbb_ecm91_EvtGen_Bc2TauNuTAUHADNU/events_003834121.root flat_ee_Zbb_Bc2TauNu.root

# python examples/FCCee/flavour/Bc2TauNu/analysis.py  /eos/experiment/fcc/ee/generation/DelphesEvents/fcc_tmp_v03/p8_ee_Zbb_ecm91_EvtGen_Bu2TauNuTAUHADNU/events_026079857.root flat_ee_Zbb_Bu2TauNu.root

# python examples/FCCee/flavour/Bc2TauNu/analysis.py  "/eos/experiment/fcc/ee/generation/DelphesEvents/fcc_tmp_v03/p8_ee_Zbb_ecm91_EvtGen_Bc2TauNuTAUHADNU/events_*" flat_ee_Zbb_Bc2TauNu.root

# python examples/FCCee/flavour/Bc2TauNu/analysis.py  /eos/experiment/fcc/ee/generation/DelphesEvents/fcc_tmp_v03/p8_ee_Zbb_ecm91/events_026734131.root flat_ee_Zbb_Bc2TauNu.root



if __name__ == "__main__":

    if len(sys.argv)==1:
        print ("usage:")
        print ("python ",sys.argv[0]," file.root")
        print ("python ",sys.argv[0]," dir/*.root")
        sys.exit(3)


    import glob
    filelist = glob.glob(sys.argv[1])
    
    print ("Create dataframe object from ", )
    fileListRoot = ROOT.vector('string')()
    for fileName in filelist:
        fileListRoot.push_back(fileName)
        print (fileName, " ",)
        print (" ...")
        
    outDir = sys.argv[0].replace(sys.argv[0].split('/')[0],'outputs/').replace('analysis_Bc2TauNu.py','')+'/'
    import os
    os.system("mkdir -p {}".format(outDir))
    outfile = outDir+sys.argv[1].split('/')[-1]
    ncpus = 8
    if len(sys.argv)==3:outfile=sys.argv[2]
    analysis = analysis(fileListRoot, outfile, ncpus)
    analysis.run()

    #tf = ROOT.TFile(infile)
    #entries = tf.events.GetEntries()
    #p = ROOT.TParameter(int)( "eventsProcessed", entries)
    #outf=ROOT.TFile(outfile,"UPDATE")
    #p.Write()

