from loaders.load import load_data
from loaders.loader_aug import Loader_aug, Loader_aug_batch
from loaders.dataset import Entity, Dataset

import glob
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


dataset_path = './dataset'


# ---------------------------------------------------------------------------
# TSB-AD "Stock" (Finance) loader
#   file: <id>_Stock_id_<k>_Finance_tr_<train_len>_1st_<first_anomaly>.csv  (columns: Data, Label)
#   train = Data[:train_len], test = Data[train_len:], labels = Label[train_len:]
#   main.py passes dataparams.data_path and dataparams.train_end for this dataset.
# ---------------------------------------------------------------------------
def _stock_path(dataparams):
    try:
        return dataparams.data_path
    except (AttributeError, KeyError):
        pass
    root = os.environ.get('STOCK_DIR', f'{dataset_path}/TSB-AD-U')
    files = glob.glob(os.path.join(root, '**', f'{dataparams.entities}.csv'), recursive=True)
    if not files:
        raise FileNotFoundError(f'Cannot find {dataparams.entities}.csv under {root}')
    return files[0]


def _stock_train_end(dataparams, path):
    try:
        return int(dataparams.train_end)
    except (AttributeError, KeyError):
        import re
        return int(re.search(r'_tr_(\d+)_', os.path.basename(path)).group(1))


def _downsample(Y, labels, downsampling):
    # same scheme as the other loaders (max-pool); skipped for downsampling in (None, 1)
    n_features, n_t = Y.shape
    right_padding = downsampling - n_t % downsampling
    Y = np.pad(Y, ((0, 0), (right_padding, 0)))
    Y = Y.reshape(n_features, Y.shape[-1] // downsampling, downsampling).max(axis=2)
    if labels is not None:
        labels = np.pad(labels, (right_padding, 0))
        labels = labels.reshape(labels.shape[0] // downsampling, downsampling).max(axis=1)
    return Y, labels


def load_stock(group, path, train_end, downsampling=None, normalize=True, verbose=True,
               validation=False, window_size=100):
    name = os.path.splitext(os.path.basename(path))[0]
    df = pd.read_csv(path)
    Y_all = df['Data'].values.astype(float).reshape(1, -1)
    label_all = df['Label'].values.astype(int)

    scaler = None
    if normalize:
        scaler = MinMaxScaler()
        scaler.fit(Y_all[:, :train_end].T)       # fit on the training part only
    do_ds = downsampling is not None and downsampling > 1

    if group == 'train':
        Y = Y_all[:, :train_end]
        if scaler is not None:
            Y = scaler.transform(Y.T).T
        if do_ds:
            Y, _ = _downsample(Y, None, downsampling)

        if validation:
            train_length = int(Y.shape[1] * 0.9)
            # Stock train parts are short (e.g. 500 points): a plain 10% tail (50 points) is shorter than
            # one window and Loader_aug would get no window at all. Give the validation tail the last
            # (window_size-1) training points as context so every held-out point ends a full window.
            val_start = max(0, train_length - (window_size - 1))
            entity = Entity(Y=Y[:, :train_length], name=f'{name}-train', verbose=verbose)
            entity_val = Entity(Y=Y[:, val_start:], name=f'{name}-val', verbose=verbose)
            data = Dataset(entities=[entity], name=f'{name}-train', verbose=verbose)
            data_val = Dataset(entities=[entity_val], name=f'{name}-val', verbose=verbose)
            return data, data_val
        entity = Entity(Y=Y, name=f'{name}-train', verbose=verbose)
        return Dataset(entities=[entity], name=f'{name}-train', verbose=verbose)

    elif group == 'test':
        Y = Y_all[:, train_end:]
        labels = label_all[train_end:]
        if scaler is not None:
            Y = scaler.transform(Y.T).T
        if do_ds:
            Y, labels = _downsample(Y, labels, downsampling)
        entity = Entity(Y=Y, name=f'{name}-test', labels=labels[None, :], verbose=verbose)
        return Dataset(entities=[entity], name=f'{name}-test', verbose=verbose)


def _load(dataparams, group, validation):
    if dataparams.dataset == 'stock':
        path = _stock_path(dataparams)
        return load_stock(group=group, path=path, train_end=_stock_train_end(dataparams, path),
                          downsampling=dataparams.downsampling, normalize=True, verbose=True,
                          validation=validation, window_size=dataparams.window_size)
    return load_data(dataset=dataparams.dataset,
                     group=group,
                     entities=dataparams.entities,
                     downsampling=dataparams.downsampling,
                     min_length=None,
                     root_dir=dataset_path,
                     verbose=True,
                     validation=validation)


def load_dataloader_aug(dataparams, anomaly_types=None, anomaly_types_for_dict=None, group='train'):
    if group=='train':
        train_dataset, val_dataset = _load(dataparams, group='train', validation=True)

        train_dataloader = Loader_aug(dataset=train_dataset,
                                    batch_size=dataparams.batch_size,
                                    window_size=dataparams.window_size,
                                    window_step=dataparams.window_step,
                                    anomaly_types=dataparams.anomaly_types,
                                    anomaly_types_for_dict=anomaly_types_for_dict,
                                    min_range=dataparams.min_range,
                                    min_features=dataparams.min_features,
                                    max_features=dataparams.max_features,
                                    fast_sampling=False,
                                    shuffle=True,
                                    verbose=True,)

        val_dataloader = Loader_aug(dataset=val_dataset,
                                    batch_size=dataparams.batch_size,
                                    window_size=dataparams.window_size,
                                    window_step=dataparams.window_step,
                                    anomaly_types=dataparams.anomaly_types,
                                    anomaly_types_for_dict=anomaly_types_for_dict,
                                    min_range=dataparams.min_range,
                                    min_features=dataparams.min_features,
                                    max_features=dataparams.max_features,
                                    fast_sampling=False,
                                    shuffle=True,
                                    verbose=True,)
        return train_dataloader, val_dataloader
    elif group=='test':
        test_dataset = _load(dataparams, group='test', validation=False)

        test_dataloader = Loader_aug(dataset=test_dataset,
                                    batch_size=dataparams.batch_size,
                                    window_size=dataparams.window_size,
                                    window_step=dataparams.window_size,
                                    anomaly_types=anomaly_types,
                                    anomaly_types_for_dict=anomaly_types_for_dict,
                                    min_range=dataparams.min_range,
                                    min_features=dataparams.min_features,
                                    max_features=dataparams.max_features,
                                    fast_sampling=False,
                                    shuffle=False,
                                    verbose=True,)
        return test_dataloader
    elif group=='test_all':
        test_dataset = _load(dataparams, group='test', validation=False)

        test_dataloader = Loader_aug(dataset=test_dataset,
                                    batch_size=dataparams.batch_size,
                                    window_size=dataparams.window_size,
                                    window_step=1,
                                    anomaly_types=anomaly_types,
                                    anomaly_types_for_dict=anomaly_types_for_dict,
                                    min_range=dataparams.min_range,
                                    min_features=dataparams.min_features,
                                    max_features=dataparams.max_features,
                                    fast_sampling=False,
                                    shuffle=False,
                                    verbose=True,)
        return test_dataloader
