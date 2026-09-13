import streamlit as st

# ✅ Clean columns
def clean_columns(df):
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
    return df

def clean_columns(df):
    # Remove unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

    # Clean column names
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()

    return df
# ✅ Show missing values
def show_missing_values(df):
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        st.success("No missing values found ✅")
    else:
        st.warning("Missing Values Found ⚠️")
        st.dataframe(missing.reset_index().rename(columns={'index': 'Column', 0: 'Missing Count'}))

    return missing

def show_missing_values(df):
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        st.success("No missing values found ✅")
    else:
        st.warning("Missing Values Found ⚠️")
        st.dataframe(missing.reset_index().rename(columns={'index': 'Column', 0: 'Missing Count'}))

    return missing
# ✅ Handle missing values
def handle_missing_values(df, missing):
    if not missing.empty:
        st.subheader("Handle Missing Values")

        option = st.selectbox(
            "How do you want to fill missing values?",
            ["None", "Mean", "Median", "Mode"]
        )

        if option != "None":
            for col in missing.index:
                if df[col].dtype in ['int64', 'float64']:
                    if option == "Mean":
                        df[col].fillna(df[col].mean(), inplace=True)
                    elif option == "Median":
                        df[col].fillna(df[col].median(), inplace=True)
                else:
                    if option == "Mode":
                        df[col].fillna(df[col].mode()[0], inplace=True)

            st.success(f"Missing values filled using {option} ✅")

    return df
def handle_missing_values(df, missing):
    if not missing.empty:
        st.subheader("Handle Missing Values")

        option = st.selectbox(
            "How do you want to fill missing values?",
            ["None", "Mean", "Median", "Mode"]
        )

        if option != "None":
            for col in missing.index:
                if df[col].dtype in ['int64', 'float64']:
                    if option == "Mean":
                        df[col].fillna(df[col].mean(), inplace=True)
                    elif option == "Median":
                        df[col].fillna(df[col].median(), inplace=True)
                else:
                    if option == "Mode":
                        df[col].fillna(df[col].mode()[0], inplace=True)

            st.success(f"Missing values filled using {option} ✅")

    return df