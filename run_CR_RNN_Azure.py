from azureml.core import Run
import joblib
import trnscrpt_rnn

#Start Run
run = Run.get_context()

#Call Transcript 
trnscrpt_rnn.runRNNTrans()

#End Run 
run.complete()