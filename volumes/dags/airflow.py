from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.contrib.sensors.file_sensor import FileSensor
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import requests
import pickle
import os
from airflow.exceptions import AirflowSkipException
from sqlalchemy import create_engine

# Set the model and data paths
MOVIE_MATRIX_PATH = '/data/processed/movie_matrix.csv'
USER_MATRIX_PATH = '/data/processed/user_matrix.csv'
MODEL_PATH = '/models/model.pkl'
TEMP_MODEL_PATH = '/models/temporary_model.pkl'
DB_CONNECTION = 'postgresql://admin:admin@postgres_movie_rec:5432/MovieRecommendations'

# Define the old model score variable
old_model_score = float(Variable.get(key="model_score", default_var=100000000))

# Define the DAG
with DAG(
    dag_id='data_model_pipeline',
    tags=['datascientest', 'project'],
    schedule_interval=None,
    start_date=days_ago(0),
    catchup=False,
    render_template_as_native_obj=True
) as my_dag:
    
    def read_ratings(ratings_csv, data_dir="/data/raw") -> pd.DataFrame:
        data = pd.read_csv(os.path.join(data_dir, ratings_csv))
        temp = pd.DataFrame(LabelEncoder().fit_transform(data["movieId"]))
        data["movieId"] = temp
        return data

    def read_movies(movies_csv, data_dir="/data/raw") -> pd.DataFrame:
        df = pd.read_csv(os.path.join(data_dir, movies_csv))
        genres = df["genres"].str.get_dummies(sep="|")
        result_df = pd.concat([df[["movieId", "title"]], genres], axis=1)
        return result_df

    def create_user_matrix(ratings, movies):
        movie_ratings = ratings.merge(movies, on="movieId", how="inner")
        movie_ratings = movie_ratings.drop(["movieId"], axis=1)
        user_matrix = movie_ratings.groupby("userId").agg("mean")
        return user_matrix
    
    def load_model(model_path=MODEL_PATH):
        with open(model_path, "rb") as filehandler:
            model = pickle.load(filehandler)
        return model

    def save_model(model, model_path=MODEL_PATH):
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, "wb") as filehandler:
            pickle.dump(model, filehandler)

    def load_to_db(db_connection, data_frame, table_name):
        engine = create_engine(db_connection)
        data_frame.to_sql(table_name, engine, if_exists='append', index=False)

    def read_from_db(db_connection, table_name):
        engine = create_engine(db_connection)
        return pd.read_sql_table(table_name, engine)
    
    def trigger_api_reload_model():
        login_response = requests.post("localhost:8889/user/login",json= {"username": "admin", "password": "admin"}).json()
        access_token = login_response["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        requests.get("localhost:8889/reload_model", headers=headers)


    def preprocess_new_data():
        user_ratings = read_ratings("ratings.csv").drop(["rating", "timestamp"], axis=1)
        movies = read_movies("movies.csv").drop(["title"], axis=1)
        user_matrix = create_user_matrix(user_ratings, movies)
        os.makedirs(os.path.dirname(MOVIE_MATRIX_PATH), exist_ok=True)
        movies.to_csv(MOVIE_MATRIX_PATH, index=False)
        user_matrix.to_csv(USER_MATRIX_PATH)

    def load_processed_data_into_db():
        movie_matrix = pd.read_csv(MOVIE_MATRIX_PATH)
        user_matrix = pd.read_csv(USER_MATRIX_PATH)
        load_to_db(DB_CONNECTION, movie_matrix, "movie_matrix_table")
        load_to_db(DB_CONNECTION, user_matrix, "user_matrix_table")
        print("Processed data loaded into the database.")

    def retrain_model():
        model = load_model()
        movie_matrix = read_from_db(DB_CONNECTION, "movie_matrix_table")
        X = movie_matrix.drop("movieId", axis=1)
        model.fit(X)
        save_model(model, TEMP_MODEL_PATH)

    def evaluate_new_model():
        model = load_model(TEMP_MODEL_PATH)
        user_matrix = read_from_db(DB_CONNECTION, "user_matrix_table")
        X = user_matrix.drop('userId', axis=1).iloc[0:99]

        distances, indices = model.kneighbors(X)
        total_distance=0
        for distance in distances:
            total_distance += sum(distance)

        print(f"Total distance: {total_distance}, Old model score: {old_model_score}")

        if total_distance > old_model_score:
            raise AirflowSkipException('Model score is worse than score of old model.')
        else:
            Variable.set("model_score", total_distance)
            print(f"New model score: {total_distance}")

    def deploy_new_model():
        model = load_model(TEMP_MODEL_PATH)
        save_model(model, MODEL_PATH)
        print("New model saved")
        trigger_api_reload_model()
        print("Api triggered to reload the model")

    # Define the tasks
    task_0 = FileSensor(
        task_id='check_for_new_data',
        fs_conn_id='file_system',
        filepath='/data/raw',
        poke_interval=5,
        timeout=30,
    )

    task_1 = PythonOperator(
        task_id='preprocess_new_data',
        python_callable=preprocess_new_data,
    )

    task_2 = PythonOperator(
        task_id='load_processed_data_into_db',
        python_callable=load_processed_data_into_db,
    )

    task_3 = PythonOperator(
        task_id='retrain_model',
        python_callable=retrain_model,
    )

    task_4 = PythonOperator(
        task_id='evaluate_new_model',
        python_callable=evaluate_new_model,
    )

    task_5 = PythonOperator(
        task_id='deploy_new_model',
        python_callable=deploy_new_model,
    )

    # Define task dependencies
    task_0 >> task_1 >> task_2 >> task_3 >> task_4 >> task_5