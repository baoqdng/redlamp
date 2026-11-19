use std::collections::{BTreeMap, HashMap};
use std::fs::File;
use std::path::{Path, PathBuf};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricValue {
    pub vus_roc: f64,
    pub vus_pr: f64,
    pub rf: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricStats {
    pub vus_roc_mean: f64,
    pub vus_roc_std: f64,
    pub vus_pr_mean: f64,
    pub vus_pr_std: f64,
    pub rf_mean: f64,
    pub rf_std: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EntityMeta {
    pub dataset: String,
    pub entity: String,
    pub seeds: Vec<i32>,
    pub default_seed: i32,
    pub n_features: usize,
    pub window_size: usize,
    pub window_step: usize,
    pub embedding_dim: usize,
    pub has_model: bool,
    pub model_path: Option<String>,
    pub is_multi_seed: bool,
    pub per_seed_metrics: HashMap<i32, MetricValue>,
    pub aggregate_metrics: Option<MetricStats>,
    pub single_metrics: Option<MetricValue>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatasetIndex {
    pub datasets: BTreeMap<String, Vec<EntityMeta>>,
}

fn calc_mean_std(vals: &[f64]) -> (f64, f64) {
    if vals.is_empty() {
        return (0.0, 0.0);
    }
    let n = vals.len() as f64;
    let mean = vals.iter().sum::<f64>() / n;
    if vals.len() == 1 {
        return (mean, 0.0);
    }
    let var = vals.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / n;
    (mean, var.sqrt())
}

pub fn scan_index(result_dir: &Path) -> DatasetIndex {
    let mut datasets: BTreeMap<String, Vec<EntityMeta>> = BTreeMap::new();

    // 1. Parse CSV metrics
    let iops_metrics = parse_seeds_csv(&result_dir.join("metrics_iops.csv"));
    let smd_metrics = parse_seeds_csv(&result_dir.join("metrics_smd.csv"));
    let msl_metrics = parse_seeds_csv(&result_dir.join("metrics_msl.csv"));
    let smap_metrics = parse_seeds_csv(&result_dir.join("metrics_smap.csv"));
    let aa_metrics = parse_anomaly_archive_csv(&result_dir.join("anomaly_archive_per_entity.csv"));

    // 2. Scan iops / aiops
    let aiops_dir = result_dir.join("aiops");
    let mut aiops_entities = Vec::new();
    if aiops_dir.exists() {
        for entry in std::fs::read_dir(&aiops_dir).into_iter().flatten().flatten() {
            let ent_name = entry.file_name().to_string_lossy().to_string();
            if ent_name.to_lowercase().contains("stock") {
                continue;
            }
            if entry.path().is_dir() {
                let (seeds, model_path) = find_seeds_and_model(&entry.path());
                let ent_metrics = iops_metrics.get(&ent_name).cloned().unwrap_or_default();
                let stats = compute_stats(&ent_metrics);
                aiops_entities.push(EntityMeta {
                    dataset: "iops".to_string(),
                    entity: ent_name,
                    seeds: if seeds.is_empty() { vec![0, 1, 2, 3, 4] } else { seeds },
                    default_seed: 0,
                    n_features: 1,
                    window_size: 100,
                    window_step: 10,
                    embedding_dim: 128,
                    has_model: model_path.is_some(),
                    model_path,
                    is_multi_seed: true,
                    per_seed_metrics: ent_metrics,
                    aggregate_metrics: Some(stats),
                    single_metrics: None,
                });
            }
        }
    }
    aiops_entities.sort_by(|a, b| a.entity.cmp(&b.entity));
    datasets.insert("iops".to_string(), aiops_entities);

    // 3. Scan smd
    let smd_dir = result_dir.join("smd");
    let mut smd_entities = Vec::new();
    if smd_dir.exists() {
        for entry in std::fs::read_dir(&smd_dir).into_iter().flatten().flatten() {
            let ent_name = entry.file_name().to_string_lossy().to_string();
            if ent_name.to_lowercase().contains("stock") {
                continue;
            }
            if entry.path().is_dir() {
                let (seeds, model_path) = find_seeds_and_model(&entry.path());
                let ent_metrics = smd_metrics.get(&ent_name).cloned().unwrap_or_default();
                let stats = compute_stats(&ent_metrics);
                smd_entities.push(EntityMeta {
                    dataset: "smd".to_string(),
                    entity: ent_name,
                    seeds: if seeds.is_empty() { vec![0, 1, 2, 3, 4] } else { seeds },
                    default_seed: 0,
                    n_features: 38,
                    window_size: 100,
                    window_step: 10,
                    embedding_dim: 128,
                    has_model: model_path.is_some(),
                    model_path,
                    is_multi_seed: true,
                    per_seed_metrics: ent_metrics,
                    aggregate_metrics: Some(stats),
                    single_metrics: None,
                });
            }
        }
    }
    smd_entities.sort_by(|a, b| a.entity.cmp(&b.entity));
    datasets.insert("smd".to_string(), smd_entities);

    // 4. Scan msl
    let msl_dir = result_dir.join("msl");
    let mut msl_entities = Vec::new();
    if msl_dir.exists() {
        let (global_seeds, global_model_path) = find_seeds_and_model(&msl_dir);
        let test_each_dir = msl_dir.join("d1_b128_w100_s10").join("0").join("test_each");
        let mut channels = Vec::new();
        if test_each_dir.exists() {
            for entry in std::fs::read_dir(&test_each_dir).into_iter().flatten().flatten() {
                let chan = entry.file_name().to_string_lossy().to_string();
                if !chan.to_lowercase().contains("stock") && entry.path().is_dir() {
                    channels.push(chan);
                }
            }
        }
        if channels.is_empty() {
            channels = msl_metrics.keys().filter(|k| *k != "msl" && !k.to_lowercase().contains("stock")).cloned().collect();
        }
        channels.sort();
        for chan in channels {
            let ent_metrics = msl_metrics.get(&chan).cloned().unwrap_or_default();
            let stats = compute_stats(&ent_metrics);
            msl_entities.push(EntityMeta {
                dataset: "msl".to_string(),
                entity: chan,
                seeds: if global_seeds.is_empty() { vec![0, 1, 2, 3, 4] } else { global_seeds.clone() },
                default_seed: 0,
                n_features: 55,
                window_size: 100,
                window_step: 10,
                embedding_dim: 128,
                has_model: global_model_path.is_some(),
                model_path: global_model_path.clone(),
                is_multi_seed: true,
                per_seed_metrics: ent_metrics,
                aggregate_metrics: Some(stats),
                single_metrics: None,
            });
        }
    }
    datasets.insert("msl".to_string(), msl_entities);

    // 5. Scan smap
    let smap_dir = result_dir.join("smap");
    let mut smap_entities = Vec::new();
    if smap_dir.exists() {
        let (global_seeds, global_model_path) = find_seeds_and_model(&smap_dir);
        let test_each_dir = smap_dir.join("d1_b128_w100_s10").join("0").join("test_each");
        let mut channels = Vec::new();
        if test_each_dir.exists() {
            for entry in std::fs::read_dir(&test_each_dir).into_iter().flatten().flatten() {
                let chan = entry.file_name().to_string_lossy().to_string();
                if !chan.to_lowercase().contains("stock") && entry.path().is_dir() {
                    channels.push(chan);
                }
            }
        }
        if channels.is_empty() {
            channels = smap_metrics.keys().filter(|k| *k != "smap" && !k.to_lowercase().contains("stock")).cloned().collect();
        }
        channels.sort();
        for chan in channels {
            let ent_metrics = smap_metrics.get(&chan).cloned().unwrap_or_default();
            let stats = compute_stats(&ent_metrics);
            smap_entities.push(EntityMeta {
                dataset: "smap".to_string(),
                entity: chan,
                seeds: if global_seeds.is_empty() { vec![0, 1, 2, 3, 4] } else { global_seeds.clone() },
                default_seed: 0,
                n_features: 25,
                window_size: 100,
                window_step: 10,
                embedding_dim: 128,
                has_model: global_model_path.is_some(),
                model_path: global_model_path.clone(),
                is_multi_seed: true,
                per_seed_metrics: ent_metrics,
                aggregate_metrics: Some(stats),
                single_metrics: None,
            });
        }
    }
    datasets.insert("smap".to_string(), smap_entities);

    // 6. Scan anomaly_archive (250 entities)
    let aa_dir = result_dir.join("anomaly_archive");
    let mut aa_entities = Vec::new();
    // Build list of 1..=250 formatted as %03d
    for id in 1..=250 {
        let ent_id_str = format!("{:03}", id);
        let id_num_str = format!("{}", id);
        // check on-disk model
        let disk_ent_dir = aa_dir.join(&ent_id_str);
        let (has_model, model_path, step) = if disk_ent_dir.exists() {
            let mut found_path = None;
            let mut detected_step = 1;
            for sub in walkdir::WalkDir::new(&disk_ent_dir) {
                if let Ok(entry) = sub {
                    let p = entry.path();
                    if p.is_file() && p.file_name().map(|n| n == "bestmodel.pkl").unwrap_or(false) {
                        found_path = Some(p.to_string_lossy().to_string());
                        if let Some(parent) = p.parent().and_then(|p| p.parent()) {
                            let name = parent.file_name().unwrap_or_default().to_string_lossy();
                            if name.contains("_s10") {
                                detected_step = 10;
                            }
                        }
                        break;
                    }
                }
            }
            (found_path.is_some(), found_path, detected_step)
        } else {
            (false, None, 1)
        };

        let metric = aa_metrics.get(&ent_id_str).or_else(|| aa_metrics.get(&id_num_str)).cloned();

        aa_entities.push(EntityMeta {
            dataset: "anomaly_archive".to_string(),
            entity: ent_id_str,
            seeds: vec![0],
            default_seed: 0,
            n_features: 1,
            window_size: 100,
            window_step: step,
            embedding_dim: 128,
            has_model,
            model_path,
            is_multi_seed: false,
            per_seed_metrics: HashMap::new(),
            aggregate_metrics: None,
            single_metrics: metric,
        });
    }
    datasets.insert("anomaly_archive".to_string(), aa_entities);

    DatasetIndex { datasets }
}

fn compute_stats(seed_map: &HashMap<i32, MetricValue>) -> MetricStats {
    let mut roc = Vec::new();
    let mut pr = Vec::new();
    let mut rf = Vec::new();
    for v in seed_map.values() {
        roc.push(v.vus_roc);
        pr.push(v.vus_pr);
        rf.push(v.rf);
    }
    let (vus_roc_mean, vus_roc_std) = calc_mean_std(&roc);
    let (vus_pr_mean, vus_pr_std) = calc_mean_std(&pr);
    let (rf_mean, rf_std) = calc_mean_std(&rf);
    MetricStats {
        vus_roc_mean,
        vus_roc_std,
        vus_pr_mean,
        vus_pr_std,
        rf_mean,
        rf_std,
    }
}

fn parse_seeds_csv(path: &Path) -> HashMap<String, HashMap<i32, MetricValue>> {
    let mut map: HashMap<String, HashMap<i32, MetricValue>> = HashMap::new();
    if !path.exists() {
        return map;
    }
    let Ok(file) = File::open(path) else { return map };
    let mut rdr = csv::Reader::from_reader(file);
    for result in rdr.records() {
        let Ok(rec) = result else { continue };
        // Headers typically: dataset, setting, entity, seed, VUS-ROC, VUS-PR, RF, ...
        let entity = rec.get(2).unwrap_or("").trim().to_string();
        if entity.to_lowercase().contains("stock") {
            continue;
        }
        let seed_str = rec.get(3).unwrap_or("0").trim();
        let Ok(seed) = seed_str.parse::<i32>() else { continue };
        let vus_roc = rec.get(4).and_then(|v| v.trim().parse::<f64>().ok()).unwrap_or(0.0);
        let vus_pr = rec.get(5).and_then(|v| v.trim().parse::<f64>().ok()).unwrap_or(0.0);
        let rf = rec.get(6).and_then(|v| v.trim().parse::<f64>().ok()).unwrap_or(0.0);

        map.entry(entity).or_default().insert(seed, MetricValue { vus_roc, vus_pr, rf });
    }
    map
}

fn parse_anomaly_archive_csv(path: &Path) -> HashMap<String, MetricValue> {
    let mut map = HashMap::new();
    if !path.exists() {
        return map;
    }
    let Ok(file) = File::open(path) else { return map };
    let mut rdr = csv::Reader::from_reader(file);
    for result in rdr.records() {
        let Ok(rec) = result else { continue };
        // Columns: entity, VUS_ROC, VUS_PR, RF
        let entity = rec.get(0).unwrap_or("").trim().to_string();
        let vus_roc = rec.get(1).and_then(|v| v.trim().parse::<f64>().ok()).unwrap_or(0.0);
        let vus_pr = rec.get(2).and_then(|v| v.trim().parse::<f64>().ok()).unwrap_or(0.0);
        let rf = rec.get(3).and_then(|v| v.trim().parse::<f64>().ok()).unwrap_or(0.0);
        map.insert(entity.clone(), MetricValue { vus_roc, vus_pr, rf });
        if let Ok(id_num) = entity.parse::<i32>() {
            map.insert(format!("{:03}", id_num), MetricValue { vus_roc, vus_pr, rf });
        }
    }
    map
}

fn find_seeds_and_model(dir: &Path) -> (Vec<i32>, Option<String>) {
    let mut seeds = Vec::new();
    let mut sample_model = None;
    for entry in walkdir::WalkDir::new(dir) {
        if let Ok(e) = entry {
            let p = e.path();
            if p.is_file() && p.file_name().map(|n| n == "bestmodel.pkl").unwrap_or(false) {
                if sample_model.is_none() {
                    sample_model = Some(p.to_string_lossy().to_string());
                }
                if let Some(parent) = p.parent() {
                    if let Ok(s) = parent.file_name().unwrap_or_default().to_string_lossy().parse::<i32>() {
                        if !seeds.contains(&s) {
                            seeds.push(s);
                        }
                    }
                }
            }
        }
    }
    seeds.sort();
    (seeds, sample_model)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_index_scanning_and_stock_exclusion() {
        let result_dir = Path::new("../result");
        let idx = scan_index(result_dir);
        
        // Must contain all 5 datasets
        assert!(idx.datasets.contains_key("anomaly_archive"), "Missing anomaly_archive");
        assert!(idx.datasets.contains_key("iops"), "Missing iops");
        assert!(idx.datasets.contains_key("smd"), "Missing smd");
        assert!(idx.datasets.contains_key("smap"), "Missing smap");
        assert!(idx.datasets.contains_key("msl"), "Missing msl");

        // Stock dataset must be completely absent
        assert!(!idx.datasets.contains_key("stock"), "Found stock dataset");
        for (ds, entities) in &idx.datasets {
            assert!(!ds.to_lowercase().contains("stock"), "Dataset name contains stock");
            for e in entities {
                assert!(!e.entity.to_lowercase().contains("stock"), "Entity name contains stock: {}", e.entity);
            }
        }

        // Multi-seed datasets must have 5 seeds [0, 1, 2, 3, 4]
        let smd = idx.datasets.get("smd").unwrap();
        assert_eq!(smd.len(), 28, "SMD should have 28 entities");
        assert_eq!(smd[0].seeds, vec![0, 1, 2, 3, 4], "SMD entity seeds");

        let iops = idx.datasets.get("iops").unwrap();
        assert_eq!(iops.len(), 29, "AIOps should have 29 entities");
        assert_eq!(iops[0].seeds, vec![0, 1, 2, 3, 4], "AIOps entity seeds");

        let msl = idx.datasets.get("msl").unwrap();
        assert_eq!(msl.len(), 23, "MSL should have 23 channels");
        assert_eq!(msl[0].seeds, vec![0, 1, 2, 3, 4], "MSL seeds");

        let smap = idx.datasets.get("smap").unwrap();
        assert_eq!(smap.len(), 54, "SMAP should have 54 channels");
        assert_eq!(smap[0].seeds, vec![0, 1, 2, 3, 4], "SMAP seeds");

        // Anomaly archive should have 250 entities
        let aa = idx.datasets.get("anomaly_archive").unwrap();
        assert_eq!(aa.len(), 250, "Anomaly Archive should have 250 entities");
        let e001 = aa.iter().find(|e| e.entity == "001").unwrap();
        assert!(e001.has_model, "001 should have model downloaded");
        assert!(e001.single_metrics.is_some(), "001 should have metrics");
    }
}

