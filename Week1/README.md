# Abalone Age Prediction

## Project Overview
This project focuses on predicting the age of abalone using physical measurements and machine learning. By leveraging features like size, weight, and sex of abalones, we build a regression model—specifically using CatBoost—that accurately estimates the number of growth rings, which corresponds to the abalone's age. This non-invasive predictive approach aims to support sustainable fisheries management by providing an efficient alternative to traditional, time-consuming age determination methods.

The project includes:
- Exploratory data analysis and preprocessing
- Encoding categorical features and feature engineering
- Training and tuning regression models (Random Forest, XGBoost, CatBoost)
- Model evaluation using R² and MAE

## Project Structure
```
week1/
├── venv/                   # Python virtual environment folder
├── requirements.txt        # Project dependencies
├── catboost_abalone_model.pkl             # Saved trained CatBoost+OPTUS model (pickle)
├── abalone.ipynb           # Jupyter notebook with full analysis and modeling
├── Abalone_dataset(Data)/  # Folder containing raw dataset files (e.g., CSV)

```

## Installation and Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd WEEK1
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Jupyter Notebook
The notebook (`abalone.ipynb`) contains the complete analysis including:
- Data loading and exploration
- Data preprocessing and feature engineering
- Implementation of various models
- Model evaluation and comparison
  
## Data Description

The dataset contains 4,177 samples of abalones with 9 features, including one categorical and eight continuous variables. The target variable is Rings, representing the abalone’s age.

Features include:

- Sex (categorical): Male (M), Female (F), Infant (I)
- Length (continuous): Longest shell measurement (mm)
- Diameter (continuous): Perpendicular to length (mm)
- Height (continuous): Meat thickness (mm)
- Whole weight (continuous): Whole abalone weight (grams)
- Shucked weight (continuous): Weight of meat (grams)
- Viscera weight (continuous): Gut weight (grams)
- Shell weight (continuous): Weight of shell (grams)
- Rings (integer): Number of growth rings (target variable)

The dataset contains no missing values but shows class imbalance in the target variable, with some ring counts being rare.

## Models Used

- **Random Forest Regressor**  
  A baseline ensemble model using multiple decision trees to capture non-linear relationships in the data.

- **XGBoost Regressor**  
  An optimized gradient boosting algorithm known for speed and performance, used for improving prediction accuracy.

- **CatBoost Regressor**  
  A gradient boosting model that natively handles categorical features like 'Sex' and reduces overfitting with ordered boosting.

- **CatBoost + Optuna**  
  The CatBoost model further optimized using Optuna, a Bayesian hyperparameter tuning framework, to achieve the best predictive performance.


See `requirements.txt` for the complete list of dependencies with versions.
