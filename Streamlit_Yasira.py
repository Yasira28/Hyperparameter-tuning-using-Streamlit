import streamlit as st
import pickle
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title='Insurance Charges Prediction', layout='centered', initial_sidebar_state='expanded')

st.title("💸 Insurance Charges Prediction with Decision Tree Regressor")
st.write("""
This demo showcases how hyperparameters affect the model performance using a *Decision Tree Regressor* on an insurance charges prediction dataset.
""")

st.sidebar.header('Set Parameters')
split_size = st.sidebar.slider('Data split ratio (% for Training Set)', 10, 90, 80, 5) / 100
max_depth_ = st.sidebar.slider('Set Max Depth for the model', 1, 20, 5, 1)
min_split_size_ = st.sidebar.slider('Set Min split size for the model', 2, 100, 5, 1)
min_leaf_size_ = st.sidebar.slider('Set Min leaf size for the model', 1, 100, 5, 1)

# Load dataset
df = pd.read_csv('Clean_insurance.csv')
X = df.drop('charges', axis=1)
y = df.charges

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=split_size, random_state=42)

# Scale the features
scaler = MinMaxScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)

# Load the pickled model
with open('decision_tree_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Update model with new hyperparameters
model.set_params(max_depth=max_depth_, min_samples_split=min_split_size_, min_samples_leaf=min_leaf_size_)

# Train the model
model.fit(x_train, y_train)

# Make predictions
y_pred_test = model.predict(x_test)
y_pred_train = model.predict(x_train)

# Calculate MAPE
MAPE_test = mean_absolute_percentage_error(y_test, y_pred_test)
MAPE_train = mean_absolute_percentage_error(y_train, y_pred_train)

# Display data and results
st.subheader('Dataset Preview')
st.dataframe(df.head())

st.subheader('Initial Model Performance')
col1, col2 = st.columns(2)
with col1:
    st.metric("Test MAPE", f"{MAPE_test:.2%}")
with col2:
    st.metric("Train MAPE", f"{MAPE_train:.2%}")

# Add a Random Search button
if st.button('Perform Randomized Search for Best Hyperparameters'):
    with st.spinner('Performing Randomized Search...'):
        param_dist = {
            'max_depth': range(1, 21),
            'min_samples_split': range(2, 101),
            'min_samples_leaf': range(1, 101)
        }
        random_search = RandomizedSearchCV(estimator=model, param_distributions=param_dist, n_iter=100, cv=5, scoring='neg_mean_absolute_percentage_error', n_jobs=-1, random_state=42)
        random_search.fit(x_train, y_train)

        best_params = random_search.best_params_
        st.write('Best Hyperparameters found by Randomized Search:')
        st.json(best_params)

        # Retrain the model with best hyperparameters
        model.set_params(**best_params)
        model.fit(x_train, y_train)

        # Make predictions with best model
        y_pred_test_best = model.predict(x_test)
        y_pred_train_best = model.predict(x_train)

        # Calculate MAPE for best model
        MAPE_test_best = mean_absolute_percentage_error(y_test, y_pred_test_best)
        MAPE_train_best = mean_absolute_percentage_error(y_train, y_pred_train_best)

        st.subheader("Best Model Performance")
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Best Test MAPE", f"{MAPE_test_best:.2%}")
        with col4:
            st.metric("Best Train MAPE", f"{MAPE_train_best:.2%}")

        # Visualize performance comparison
        st.subheader("Performance Comparison")

        fig, ax = plt.subplots()
        bars = ax.bar(['Initial Test', 'Best Test'], [MAPE_test, MAPE_test_best], color=['blue', 'green'])
        ax.set_ylabel('MAPE')
        ax.set_title('Test MAPE Comparison')
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2%}', va='bottom')

        st.pyplot(fig)
else:
    st.info('Click the button to perform Randomized Search for the best hyperparameters.')