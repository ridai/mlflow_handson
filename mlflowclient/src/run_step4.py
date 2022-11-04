import os
from mlflow import (
    set_tracking_uri,
    set_experiment,
    start_run,
    set_tag,
    log_metric,
    log_metrics,
    log_param,
    log_params,
)
import datetime

if __name__ == "__main__":
    # MLflow Trackingサーバへの接続
    set_tracking_uri("http://mlflowserver:5000")

    # experiment idを自前で指定(=とりあえず時刻文字列)
    experiment_name = str(datetime.datetime.now())
    set_experiment(experiment_name)

    with start_run(run_name="SampleA"):
        # tagの保存
        set_tag("parentTagA", "hoge")
        with start_run(run_name="ChildrenSampleB", nested=True):
            # tagの保存
            set_tag("childrenTagA", "fuga")
            # parameterの保存
            log_param("Dence", 128)
            data = {"Dropout": 0.1, "Activation": "relu"}
            log_params(data)

            # metricsのstepごとのデータの保存
            log_metric("mse", 100.0, step=0)
            log_metric("rmse", 50.0, step=0)
            data = {"mse": 80.0, "rmse": 30.0}
            log_metrics(data, step=1)

        with start_run(run_name="ChildrenSampleC", nested=True):
            # tagの保存
            set_tag("childrenTagA", "hogehoge")
            # parameterの保存
            log_param("Dence", 256)
            data = {"Dropout": 0.3, "Activation": "relu"}
            log_params(data)

            # metricsのstepごとのデータの保存
            log_metric("mse", 120.0, step=0)
            log_metric("rmse", 70.0, step=0)
            data = {"mse": 60.0, "rmse": 10.0}
            log_metrics(data, step=1)
