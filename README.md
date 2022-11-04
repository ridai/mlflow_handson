# celery-handson
## 目次
1. [概要](#anchor1)
1. [Step1](#anchor2)
1. [Step2](#anchor3)
1. [Step3](#anchor4)
1. [Step4](#anchor5)
1. [動作確認課題](#anchor6)

<a id="anchor1"></a>
## 概要
 [MLFlow](https://github.com/mlflow/mlflow/)をPythonアプリから利用するためのハンズオン資料です。<br>
 あくまで、一部機能の紹介に過ぎないので、あまり高度な使い方は想定してません。<br>

#### MLFlowとは？
機械学習の実行時に、各種データ（使った特徴、モデル、CVスコア、画像、lossなど）を所定のデータ構造で紐づけて管理してくれる。また、データにアクセスするためのエンドポイントを提供してくれる。<br>
他にも、データを簡単に視認できるように、専用のUI画面も用意されている。<br>

ただし、自前で学習の試行結果をDB等で管理できるのであれば、必ずしも必須ではない。

#### 前提
- mlflow version: ver.1.24.X

<a id="anchor2"></a>
## Step.1
### 概要
MLflowを立ち上げ、実際のUI画面を確認し、「実験」と呼ばれる概念を理解する。


### 手順
1. 環境を立ち上げる
```
$docker-compose build
$docker-compose up
```

コンテナの構成は以下の図の通り。

<img width="500" alt="mlflow_handson_arch" src="https://user-images.githubusercontent.com/2268153/199867105-b551b2b6-b689-43d3-bdf0-55c4c3429e26.png">


2. ブラウザで`localhost:5000`にアクセスすると、以下のMLflowのUI画面が見えるはず。

<img width="500" alt="mlflow_00" src="https://user-images.githubusercontent.com/2268153/199773431-ab773f81-d596-4745-a048-f2f5e3e54305.png">

3. mlflowmyql コンテナに入り、table情報を見ると以下のようなtableが作成されていることが確認できる。

```
bash-4.2# mysql -u mlflow -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 11
Server version: 5.7.40 MySQL Community Server (GPL)

Copyright (c) 2000, 2022, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> use mlflow
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> show tables;
+-----------------------+
| Tables_in_mlflow      |
+-----------------------+
| alembic_version       |
| experiment_tags       |
| experiments           |
| latest_metrics        |
| metrics               |
| model_version_tags    |
| model_versions        |
| params                |
| registered_model_tags |
| registered_models     |
| runs                  |
| tags                  |
+-----------------------+
12 rows in set (0.00 sec)
```

### 解説
#### 環境構築
MLflowサーバ(MLflow Trackinサーバと呼ばれる)を立ち上げる際は、schemableなデータを格納する先としてRDBMSの指定と、objectデータの格納先としてObjectStorageを指定する。<br><br>
RDBMSを利用するためには、mlflowの立ち上げコマンドにて `mlflow server --backend-store-uri 'mysql://[mysql username]:[mysql password]@[mysql hostname]:[mysql port]/mlflow`と宣言する必要がある。<br>
※ RDBMSを指定しないと、mlflowサーバのlocalファイルに `./mlruns`というディレクトリが作成され、そこにデータが格納されていく。<br><br>
ObjectStorageを利用するためには、環境変数として`MLFLOW_S3_ENDPOINT_URL=http://[ObjectStorage hostname]:[ObjectStorage port]`、`AWS_ACCESS_KEY_ID=[ObjectStorage Access Key]`、`AWS_SECRET_ACCESS_KEY=[ObjectStorage Secret Key]`の指定が必要。また、mlflowの立ち上げコマンドにて `mlflow server --default-artifact-root 's3://mlflow/`と宣言する必要がある。<br>


#### 実験(=experiment)とは
画面左のメニューは、「実験(=experiment)」と呼ばれるデータを選択できる。<br>
実験には、「実験名(=experiment name)」と「ID」が割り振られ、それぞれ重複は許されない。<br>
また、同実験名(ID)のデータ内には、複数の学習の試行データを行データとして追加していくことができる。<br>
実際に追加される行データの中身(=run)については、後述。<br>
つまり、「実験」は、複数の学習の試行データを、名前(ID)をつけて集約・管理できるもの。<br>

<a id="anchor3"></a>
## Step.2
### 概要
clientから、実験IDを新規に作成し、学習の試行データを投入してみる

### 手順

1. clientコンテナに入り、簡単な学習スクリプトを回す
```
$docker exec -it mlflowclient /bin/bash
$python /data/run_step2.py
```

2. MLflowのUI画面を確認し、新しい「実験名」がメニューに増えていること・クリックすると学習のデータが入っていることを確認する。

### 解説
#### MLFlowサーバへの接続

``` python
    set_tracking_uri("http://mlflowserver:5000")
```

#### 実験IDの払い出し

``` python
    experiment_name = str(datetime.datetime.now())
    # mlflow.set_experiment(experiment_name: Optional[str] = None, experiment_id: Optional[str] = None) → Experiment
    set_experiment(experiment_name)
```

実験名として、現在時刻の文字列を指定。実験名を明に指定しない場合、ランダムな値が自動で割り振られる。<br>

<img width="500" alt="exp" src="https://user-images.githubusercontent.com/2268153/199887447-154bd773-22f7-4d73-9baf-185e03046437.png">

#### 学習試行データの投入準備
実験に紐づいて保存される、一つ一つの学習試行データは、`run`という単位のデータ構造にまとめられる。
`run`のデータ構造には、学習のloss情報や、metrics情報、学習結果モデルなどのデータを格納・管理できる。<br>
`run`を作成するためには、以下のmethodを呼び出す。

``` python
    # mlflow.start_run(run_id: Optional[str] = None, experiment_id: Optional[str] = None, run_name: Optional[str] = None, nested: bool = False, tags: Optional[Dict[str, Any]] = None, description: Optional[str] = None) → ActiveRun
    with start_run(run_name="SampleA"):
        ...
```

このwith句で囲った中で、各種学習試行データの格納処理(後述)をすると、指定した`run_name`に紐づくデータとしてmlflowサーバにデータが格納されていく。<br>
実際に、`run_step2.py`を実行すると、`SampleA`という`run`が生まれることがUI上で確認できる。

<img width="500" alt="run" src="https://user-images.githubusercontent.com/2268153/199887547-63d170cf-08c9-4173-9ca4-c9507d0b3e6b.png">


#### 学習データ(tag)の投入
`run`の中に`tag`と呼ばれる、ユーザが好きに指定できる `{key(str): value(str)}`データを保存できる。実態は、MySQLにtag tableが存在し、そこにkeyとvalueのrecordが挿入される仕組み。<br>
※ valueに与えられる文字列の長さは、`5000` までらしい。(https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.set_tag)<br>
この`tag`は、後から学習データの***検索に使うこと***ができる。<br>
`tag`を利用するには、以下のようにmethodを呼ぶ。

```python
        # mlflow.set_tag(key: str, value: Any) → None
        set_tag("tagA", "hoge")
```

実際に投入した結果、UI上では以下のように格納されていることが確認できる。

<img width="500" alt="tag" src="https://user-images.githubusercontent.com/2268153/199887794-61465168-0645-4a34-88ec-cf8772a859b3.png">

<img width="500" alt="detail" src="https://user-images.githubusercontent.com/2268153/199888406-26233d9f-9ddf-4e78-a5a7-d93348814fa4.png">

#### 学習データ(param)の投入
ハイパーパラメータ情報などの保存向けに、`param`と呼ばれるデータを保存できる。<br>
単純な`{key(str): value(str|number)}`の保存であれば、以下のmethodを呼ぶ。

```python
        # mlflow.log_params(params: Dict[str, Any]) → None
        log_param("Dence": 128)
```

また、複数の`param`をdictとして一括でデータ保存することもできる。<br>
その場合は、以下のmethodを呼ぶ。

``` python
        # mlflow.log_params(params: Dict[str, Any]) → None
        data = {"Dropout": 0.1, "Activation": "relu"}
        log_params(data)
```

#### 学習データ(metric)の投入
評価結果情報などの保存向けに、`metric`と呼ばれるデータを保存できる。<br>

単純な`{key(str): value(number)}`の保存であれば、以下のmethodを呼ぶ。

```python
        # mlflow.log_metric(key: str, value: float, step: Optional[int] = None) → None
        log_metric("mse": 100.0, step=0)
        log_metric("rmse": 50.0, step=0)
```

また、複数の`metric`をdictとして一括でデータ保存することもできる。<br>
その場合は、以下のmethodを呼ぶ。

``` python
        # mlflow.log_metrics(metrics: Dict[str, float], step: Optional[int] = None) → None
        data = {"mse": 150.0, "rmse": 120.0}
        log_metrics(data, step=1)
```

ここで、`step`を指定しているが、これは同metricsの遷移を保存するための情報であり、UI上では、以下のように確認できる。

<img width="500" alt="metrics_step" src="https://user-images.githubusercontent.com/2268153/199888621-e0d8fe45-e022-4d88-a02a-2b9ba4e95071.png">


<a id="anchor4"></a>
## Step.3
### 概要
textやbinaryデータを格納してみる。<br>
Step.2までは、MySQLに格納されるデータ(tag/metrics/params)の確認だったが、ここではjsonやpickleファイルの保存を行い、ObjectStorageに格納されることを確認する。

### 手順

1. clientコンテナに入り、簡単な学習スクリプトを回す
```
$docker exec -it mlflowclient /bin/bash
$python /data/run_step3.py
```

2. MLflowのUI画面を確認し、新しい「実験名」がメニューに増えていること・クリックすると学習のデータが入っていることを確認する。

3. runの中身を確認すると、`Artifact`という領域に、jsonデータが保存されていることが確認できる。

### 解説
#### テキストの投入
テキストをファイルとして保存してほしい場合に利用。<br>

``` python
        # mlflow.log_text(text: str, artifact_file: str) → None
        log_text("Hello world", "file1.txt")
```

結果、artifactの領域にtextファイルが存在していることがわかる

<img width="500" alt="text" src="https://user-images.githubusercontent.com/2268153/199899904-b5feb1e8-de03-49e1-8858-ccb873620a2c.png">

#### dictの投入
jsonファイルとして保存したい場合に利用。<br>

``` python
        # mlflow.log_dict(dictionary: Any, artifact_file: str) → None
        data = {"var1": 1.0, "var2": "fugafuga"}
        log_dict(data, "file2.json")
```

結果、artifactの領域にtextファイルが存在していることがわかる

<img width="500" alt="json" src="https://user-images.githubusercontent.com/2268153/199900200-a8a665ce-2d69-4a64-8a51-b17b07e37d2c.png">

#### 保存済みのbinaryデータを投入

図やテキスト、バイナリデータなど、保存済みのファイルをアップロードする場合に利用。<br>

``` python
        # mlflow.log_artifact(local_path: str, artifact_path: Optional[str] = None) → None
        log_artifact("/data/sample.png")
```

結果、artifactの領域にtextファイルが存在していることがわかる

<img width="500" alt="figure" src="https://user-images.githubusercontent.com/2268153/199901006-02871e00-5c26-4790-bb2e-b7c368f5a683.png">


<a id="anchor5"></a>
## Step.4
### 概要
`run`のデータ構造nest化して管理してみる。

### 手順
1. clientコンテナに入り、簡単な学習スクリプトを回す
```
$docker exec -it mlflowclient /bin/bash
$python /data/run_step4.py
```

2. MLflowのUI画面を確認し、新しい「実験名」がメニューに増えていること・クリックすると学習のデータが入っていることを確認する。

3. runの中身を確認すると、さらに`run`をnestで持っていることが確認できる

### 解説
#### runのnest化
runのwith句の中で、さらに、runのwith句を差し込み、以下のように、`nested=True`を指定するとrunがnest構造になる。`nested`を指定しないとnest構造にならない点に注意。

<img width="500" alt="nest" src="https://user-images.githubusercontent.com/2268153/199903008-02c6c305-3b08-458f-8eb9-331d81af7865.png">


---

## 総括
上記、pythonからのclientmethodを活用することで、ある程度機械学習に必要なデータ構造に従ってデータの格納が簡単に行えるのが、MLflowのメリットである。<br>
