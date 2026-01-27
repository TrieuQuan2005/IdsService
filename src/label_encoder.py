# src/label_encoder.py
class AttackLabelEncoder:
    LABEL_MAPPING = {
        "BENIGN": "Normal",

        "DDoS": "DDoS",

        "DoS Hulk": "DoS",
        "DoS GoldenEye": "DoS",
        "DoS slowloris": "DoS",
        "DoS Slowhttptest": "DoS",

        "Web Attack � Brute Force": "WebAttack",
        "Web Attack � XSS": "WebAttack",
        "Web Attack � Sql Injection": "WebAttack",

        "Infiltration": "Infiltration",
        "PortScan": "PortScan",

        "Bot": "Botnet",
        "Botnet": "Botnet",

        "FTP-Patator": "BruteForce",
        "SSH-Patator": "BruteForce",

        "Heartbleed": "Heartbleed"
    }

    DEFAULT_LABEL = "Other"

    def encode(self, labels):
        return labels.astype(str).map(
            lambda x: self.LABEL_MAPPING.get(x.strip(), self.DEFAULT_LABEL)
        )

    def decode(self, label):
        return label

