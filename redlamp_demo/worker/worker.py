#!/usr/bin/env python3
"""
RedLamp Worker: Subprocess communicating via JSON lines over stdin/stdout.
Imports directly from REDLAMP-main without rewriting scoring or normalization.
"""
import sys
import os
import json

# Ensure redlamp_demo is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from engine import RedLampEngine
from index import RedLampIndexer, get_default_result_dir

RESULT_DIR = get_default_result_dir()

def main():
    indexer = RedLampIndexer(RESULT_DIR)
    engine = RedLampEngine(RESULT_DIR)

    # Process JSON commands line by line from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            action = req.get("action")
            
            if action == "index":
                resp = {"status": "ok", "data": indexer.index_cache}
            elif action == "entity":
                dataset = req.get("dataset")
                entity = req.get("entity")
                seed = int(req.get("seed", 0))
                data = engine.load_entity_data(dataset, entity, seed)
                model, params = engine.load_model(dataset, entity, seed)
                resp = {
                    "status": "ok",
                    "data": {
                        "length": data["length"],
                        "threshold_995": data["threshold_995"],
                        "threshold_990": data["threshold_990"],
                        "threshold_950": data["threshold_950"],
                        "max_anomaly_idx": data["max_anomaly_idx"],
                        "normal_idx": data["normal_idx"],
                        "feat_min": data["feat_min"],
                        "feat_max": data["feat_max"],
                        "feat_median": data["feat_median"],
                        "n_features": params.n_features,
                        "window_size": params.n_time,
                    }
                }
            elif action == "predict_point":
                dataset = req.get("dataset")
                entity = req.get("entity")
                seed = int(req.get("seed", 0))
                point = req.get("point", [])
                context_type = req.get("context_type", "sample_last")
                custom_history = req.get("custom_history")
                th_override = req.get("threshold_override")
                res = engine.predict_point(dataset, entity, seed, point, context_type, custom_history, th_override)
                resp = {"status": "ok", "data": res}
            elif action == "explain":
                dataset = req.get("dataset")
                entity = req.get("entity")
                seed = int(req.get("seed", 0))
                t = req.get("t")
                if t is not None:
                    t = int(t)
                res = engine.explain(dataset, entity, seed, t)
                resp = {"status": "ok", "data": res}
            else:
                resp = {"status": "error", "message": f"Unknown action: {action}"}
        except Exception as e:
            resp = {"status": "error", "message": str(e)}

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()

