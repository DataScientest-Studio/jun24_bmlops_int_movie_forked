🎬 Movie Recommendation System
==============================
The Movie Recommendation System develops a movie recommendation system for a streaming platform. The recommendation system leverages collaborative filtering techniques, utilizing user ratings and movie genre data to generate personalized movie recommendations.

This project is a comprehensive MLOps implementation designed to enhance user experience by suggesting movies that align with individual tastes. This project is based on [the MovieLens 20M Dataset](https://grouplens.org/datasets/movielens/20m/).

👨🏼‍💻👩‍💻👨🏻‍💻 Development Team
==============================
The Movie Recommendation System has been developed by:

    -Dennis Rothfuss
    -Eva Losada Barreiro

🏗️ Architecture
==============================


📂 Project Organization
==============================

```plaintext
.github/
├── workflows/
│   ├── build-and-push-dockerimages.yml
│   └── python-app.yml
models/
├── .gitkeep
├── model.pkl
notebooks/
├── .gitkeep
references/
├── .gitkeep
reports/
├── figures/
│   └── .gitkeep
src/
├── data/
│   ├── .gitkeep
│   ├── __init__.py
│   ├── check_structure.py
│   ├── import_raw_data.py
│   └── make_dataset.py
├── features/
│   ├── .gitkeep
│   ├── __init__.py
│   └── build_features.py
├── model_api/
│   ├── Dockerfile
│   ├── model_api.py
│   ├── requirements.txt
│   └── test_api.py
├── models/
│   ├── .gitkeep
│   ├── __init__.py
│   ├── predict_model.py
│   └── train_model.py
├── visualization/
│   ├── __init__.py
│   └── config
volumes/
├── .gitignore
├── LICENSE
├── README.md
├── docker-compose.yml
├── requirements.txt
└── setup.py

--------

## Steps to follow 

Convention : All python scripts must be run from the root specifying the relative file path.

### 1- Create a virtual environment using Virtualenv.

    `python -m venv my_env`

###   Activate it 

    `./my_env/Scripts/activate`

###   Install the packages from requirements.txt  (You can ignore the warning with "setup.py")

    `pip install -r .\requirements.txt`

### 2- Execute import_raw_data.py to import the 4 datasets (say yes when it asks you to create a new folder)

    `python .\src\data\import_raw_data.py` 

### 3- Execute make_dataset.py initializing `./data/raw` as input file path and `./data/processed` as output file path.

    `python .\src\data\make_dataset.py`

### 4- Execute build_features.py to preprocess the data (this can take a while)

    `python .\src\features\build_features.py`

### 5- Execute train_model.py to train the model

    `python .\src\models\train_model.py`

### 5- Finally, execute predict_model.py file to make the predictions (by default you will be printed predictions for the first 5 users of the dataset). 

    `python .\src\models\predict_model.py`

### Note that we have 10 recommandations per user

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
