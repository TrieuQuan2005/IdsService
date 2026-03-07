import os
from RandomJungle.Data.FeatureSets import HostMultiFeatures, FlowMultiFeatures, HostBinaryFeatures, FlowBinaryFeatures
from RandomJungle.Models.RfHostBin import RfHostBin
from RandomJungle.Models.RfFlowBin import RfFlowBin
from RandomJungle.Models.RfHostMulti import RfHostMulti
from RandomJungle.Models.RfFlowMulti import RfFlowMulti
from RandomJungle.Data.ModelOutputs import BinaryModelOutput, HostMultiModelOutput, FlowMultiModelOutput
from RandomJungle.Data.Labels import BinaryLabel, FinalPredictionLabel
from DecisionFusion.DecisionFusion import DecisionFusion

# Create zero features
host_bin = HostBinaryFeatures(0,0.0,0.0,0.0,0.0,0.0)
flow_bin = FlowBinaryFeatures(0.0,0.0,0,0.0,0.0,0.0)
host_multi = HostMultiFeatures(0,0.0,0.0,0.0,0.0,0.0)
flow_multi = FlowMultiFeatures(0.0,0.0,0,0.0,0.0,0.0)

# Arrays
h_bin_arr = host_bin.to_array().reshape(1,-1)
f_bin_arr = flow_bin.to_array().reshape(1,-1)
h_multi_arr = host_multi.to_array().reshape(1,-1)
f_multi_arr = flow_multi.to_array().reshape(1,-1)

# Load models
hostBinModel = RfHostBin(); hostBinModel.load('Train/hostBin.pkl')
flowBinModel = RfFlowBin(); flowBinModel.load('Train/flowBin.pkl')
hostMultiModel = RfHostMulti(); hostMultiModel.load('Train/hostMulti.pkl')
flowMultiModel = RfFlowMulti(); flowMultiModel.load('Train/flowMulti.pkl')

# Predict
host_bin_out = BinaryModelOutput.from_proba(hostBinModel.predict_proba(h_bin_arr)[0], hostBinModel.model.classes_)
flow_bin_out = BinaryModelOutput.from_proba(flowBinModel.predict_proba(f_bin_arr)[0], flowBinModel.model.classes_)

# Only predict multi if model has >=2 classes
host_multi_out = None
flow_multi_out = None
if len(getattr(hostMultiModel.model,'classes_',[]))>=2:
    host_multi_out = HostMultiModelOutput.from_proba(hostMultiModel.predict_proba(h_multi_arr)[0], hostMultiModel.model.classes_)
if len(getattr(flowMultiModel.model,'classes_',[]))>=2:
    flow_multi_out = FlowMultiModelOutput.from_proba(flowMultiModel.predict_proba(f_multi_arr)[0], flowMultiModel.model.classes_)

fusion = DecisionFusion()
final_label, confidence = fusion.fuse(host_bin_out, flow_bin_out, host_multi_out, flow_multi_out)

# Log to file same format used in app
log_dir = os.path.join('Logger','logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir,'predictions.txt')

host_vec_str = ",".join([str(x) for x in h_multi_arr[0].tolist()])
flow_vec_str = ",".join([str(x) for x in f_multi_arr[0].tolist()])

def fmt_output(out):
    if out is None:
        return 'None:0.0'
    return f"{out.label.name}:{out.confidence:.6f}"

host_bin_s = fmt_output(host_bin_out)
flow_bin_s = fmt_output(flow_bin_out)
host_multi_s = fmt_output(host_multi_out)
flow_multi_s = fmt_output(flow_multi_out)
final_s = f"{final_label.name}:{confidence:.6f}"

line = f"[{host_vec_str}] [{flow_vec_str}] {host_bin_s} {flow_bin_s} {host_multi_s} {flow_multi_s} {final_s}\n"
with open(log_file,'a',encoding='utf-8') as f:
    f.write(line)

print('WROTE LOG LINE:')
print(line)
print('\nModel classes:')
print('hostBin', hostBinModel.model.classes_)
print('flowBin', flowBinModel.model.classes_)
print('hostMulti', getattr(hostMultiModel.model,'classes_',None))
print('flowMulti', getattr(flowMultiModel.model,'classes_',None))

