from biosppy.signals import ecg
from script_runner import run

def proccessCalcBPM(data):
    results = []
    for payload in data:
        signal = payload["signal"]
        out = ecg.ecg(
            signal=signal,
            sampling_rate=360,
            show=False
        )

        results.append(
            out["heart_rate"].tolist()
        )
    return results

def lambda_handler(event, context):
    return run(
        process_function=proccessCalcBPM,
        payloads=event["data"],
        prepare_signals=True,
        min_derivations=1
    )