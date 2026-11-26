from hashlib import sha256
import json
from math import ceil, floor

import numpy as np
from sklearn.linear_model import QuantileRegressor
from sklearn.metrics import mean_pinball_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from domain.shop_history import work_orders

QUANTILES = (0.2, 0.8)

def calculate(data):
    records = list(work_orders())
    x = np.array([row[:4] for row in records], dtype=float)
    y = np.array([row[4] for row in records], dtype=float)
    split = 110
    future = np.array([[data['minutes'],data['mass'],data['stones'],data['backlog']]],dtype=float)
    models = [make_pipeline(StandardScaler(), QuantileRegressor(quantile=q,alpha=0.02,solver='highs')).fit(x[:split],y[:split])
              for q in QUANTILES]
    held = np.vstack([model.predict(x[split:]) for model in models])
    lower,upper = np.min(held,axis=0),np.max(held,axis=0)
    point = sorted(float(model.predict(future)[0]) for model in models)
    return {'algorithm':'QuantileRegressor','quantiles':list(QUANTILES),'seed':1088,
            'train_rows':split,'held_rows':len(y)-split,'lower_days':max(1,floor(point[0])),
            'upper_days':max(1,ceil(point[1])),
            'coverage':round(float(np.mean((lower<=y[split:]) & (y[split:]<=upper))),4),
            'p20_pinball':round(mean_pinball_loss(y[split:],held[0],alpha=.2),4),
            'p80_pinball':round(mean_pinball_loss(y[split:],held[1],alpha=.8),4),
            'crossing_rows':int(np.sum(held[0]>held[1])),
            'input_sha256':sha256(json.dumps([records,data],sort_keys=True).encode()).hexdigest()}
