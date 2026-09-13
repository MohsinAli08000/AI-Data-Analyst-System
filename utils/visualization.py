import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def auto_graphs(df):
    st.subheader("Auto Data Visualization 📊")

    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = df.select_dtypes(include=['object']).columns

    # Numeric graphs
    if len(num_cols) > 0:
        st.write("### Numeric Data")
        for col in num_cols:
            fig, ax = plt.subplots()
            sns.histplot(df[col], kde=True, ax=ax)
            ax.set_title(f"Distribution of {col}")
            st.pyplot(fig)

    # Categorical graphs
    if len(cat_cols) > 0:
        st.write("### Categorical Data")
        for col in cat_cols:
            fig, ax = plt.subplots()
            df[col].value_counts().plot(kind='bar', ax=ax)
            ax.set_title(f"Count of {col}")
            st.pyplot(fig)

    # Heatmap
    if len(num_cols) > 1:
        st.write("### Correlation Heatmap")
        fig, ax = plt.subplots()
        sns.heatmap(df[num_cols].corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)

import matplotlib.pyplot as plt
import seaborn as sns

def auto_graphs(df):
    st.subheader("Auto Data Visualization 📊")

    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = df.select_dtypes(include=['object']).columns

    # Numeric Data Graphs
    if len(num_cols) > 0:
        st.write("### Numeric Data")

        for col in num_cols:
            fig, ax = plt.subplots()
            sns.histplot(df[col], kde=True, ax=ax)
            ax.set_title(f"Distribution of {col}")
            st.pyplot(fig)

    # Categorical Data Graphs
    if len(cat_cols) > 0:
        st.write("### Categorical Data")

        for col in cat_cols:
            fig, ax = plt.subplots()
            df[col].value_counts().plot(kind='bar', ax=ax)
            ax.set_title(f"Count of {col}")
            st.pyplot(fig)

    # Correlation Heatmap (only numeric)
    if len(num_cols) > 1:
        st.write("### Correlation Heatmap")

        fig, ax = plt.subplots()
        sns.heatmap(df[num_cols].corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)