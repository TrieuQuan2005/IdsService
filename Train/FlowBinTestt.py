from RandomJungle.Models.RfFlowBin import RfFlowBin
from RandomJungle.Data.FeatureSets import FlowBinaryFeatures

flowBinModel = RfFlowBin()
flowBinModel.load("flowBin.pkl")

testData = FlowBinaryFeatures(
    packets_per_second=282.7,
    bytes_per_second=16962.0,
    packet_count=2827,
    flow_duration=9.997170209884644,
    forward_ratio=1.0,
    syn_ratio=0.0,
)

print(flowBinModel.predict(testData.to_array().reshape(1, -1)))