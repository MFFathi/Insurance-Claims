import nbformat as nbf
import numpy as np

nb = nbf.v4.new_notebook()

# Create cells
cells = []

# Title and imports
cells.append(nbf.v4.new_markdown_cell("""# Enhanced Insurance Claims Data Analysis

This notebook provides detailed analysis of insurance claims data with:
- Comprehensive data visualization
- Statistical analysis
- Pattern discovery
- Feature relationships"""))

cells.append(nbf.v4.new_code_cell("""# Import required libraries
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set basic plot styles
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['axes.grid'] = True
sns.set_theme(style="whitegrid")"""))

# Data Loading
cells.append(nbf.v4.new_markdown_cell("## 1. Data Loading and Initial Examination"))
cells.append(nbf.v4.new_code_cell("""# Load data
df = pd.read_csv("Cleaned_Patient_Records.csv")
print("Dataset Shape:", df.shape)
print("Columns:", df.columns.tolist())
df.head()"""))

# Basic Analysis
cells.append(nbf.v4.new_markdown_cell("## 2. Statistical Analysis"))
cells.append(nbf.v4.new_code_cell("""# Basic statistics and distributions
print("Basic Statistics:")
print(df.describe())

# Distribution of Settlement Values
plt.figure(figsize=(12, 6))
sns.histplot(data=df, x='SettlementValue', bins=50, kde=True)
plt.title('Distribution of Settlement Values')
plt.xlabel('Settlement Amount')
plt.ylabel('Frequency')
plt.show()

# Box plot of settlements by accident type
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x='AccidentType', y='SettlementValue')
plt.title('Settlement Distribution by Accident Type')
plt.xticks(rotation=45)
plt.show()"""))

# Enhanced Feature Analysis
cells.append(nbf.v4.new_markdown_cell("## 3. Enhanced Feature Analysis"))
cells.append(nbf.v4.new_code_cell("""# Create composite features
# First create total damages
df['total_damages'] = df[[col for col in df.columns if col.startswith('Special') or col.startswith('General')]].sum(axis=1)

# Then create special and general damages separately
df['total_special_damages'] = df[[col for col in df.columns if 'Special' in col]].sum(axis=1)
df['total_general_damages'] = df[[col for col in df.columns if 'General' in col]].sum(axis=1)

# Create damage severity ratio with protection against division by zero
df['damage_severity_ratio'] = df['total_damages'] / df['Injury_Prognosis'].replace(0, 1)

# Handle infinite values and very large numbers
df = df.replace([np.inf, -np.inf], np.nan)

# Fill NaN values for numeric columns only
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

# Scatter plot matrix of key features
key_features = ['SettlementValue', 'Injury_Prognosis', 'total_special_damages', 'total_general_damages']
sns.pairplot(df[key_features], diag_kind='kde')
plt.suptitle('Relationships Between Key Features', y=1.02)
plt.show()

# Correlation analysis with heatmap
plt.figure(figsize=(12, 8))
correlation_matrix = df[key_features].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix of Key Features')
plt.show()"""))

# Temporal Analysis
cells.append(nbf.v4.new_markdown_cell("## 4. Advanced Temporal Analysis"))
cells.append(nbf.v4.new_code_cell("""# Convert to datetime
df['Accident Date'] = pd.to_datetime(df['Accident Date'])

# Extract temporal features
df['hour'] = df['Accident Date'].dt.hour
df['day_of_week'] = df['Accident Date'].dt.day_name()
df['month'] = df['Accident Date'].dt.month
df['season'] = pd.cut(df['Accident Date'].dt.month, bins=[0,3,6,9,12], labels=['Winter', 'Spring', 'Summer', 'Fall'])

# Create subplots for temporal patterns
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Average settlement by hour
sns.lineplot(data=df, x='hour', y='SettlementValue', ax=axes[0,0])
axes[0,0].set_title('Average Settlement by Hour')

# Average settlement by day of week
sns.boxplot(data=df, x='day_of_week', y='SettlementValue', ax=axes[0,1])
axes[0,1].set_title('Settlement Distribution by Day of Week')
axes[0,1].tick_params(axis='x', rotation=45)

# Average settlement by month
monthly_avg = df.groupby('month')['SettlementValue'].mean()
sns.barplot(x=monthly_avg.index, y=monthly_avg.values, ax=axes[1,0])
axes[1,0].set_title('Average Settlement by Month')

# Settlement distribution by season
sns.violinplot(data=df, x='season', y='SettlementValue', ax=axes[1,1])
axes[1,1].set_title('Settlement Distribution by Season')

plt.tight_layout()
plt.show()"""))

# Injury Analysis
cells.append(nbf.v4.new_markdown_cell("## 5. Injury and Damage Analysis"))
cells.append(nbf.v4.new_code_cell("""# Create injury severity categories
df['severity_category'] = pd.qcut(df['Injury_Prognosis'], q=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])

# Plot injury patterns
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Settlement by injury severity
sns.boxplot(data=df, x='severity_category', y='SettlementValue', ax=axes[0,0])
axes[0,0].set_title('Settlement by Injury Severity')
axes[0,0].tick_params(axis='x', rotation=45)

# Psychological injury impact
sns.boxplot(data=df, x='Minor_Psychological_Injury', y='SettlementValue', ax=axes[0,1])
axes[0,1].set_title('Settlement Distribution by Psychological Injury')

# Special vs General damages
sns.scatterplot(data=df, x='total_special_damages', y='total_general_damages', 
                hue='severity_category', size='SettlementValue', sizes=(20, 200), ax=axes[1,0])
axes[1,0].set_title('Special vs General Damages')

# Damage ratio distribution
sns.histplot(data=df[df['damage_severity_ratio'] < df['damage_severity_ratio'].quantile(0.95)], 
            x='damage_severity_ratio', bins=50, kde=True, ax=axes[1,1])
axes[1,1].set_title('Distribution of Damage-Severity Ratio')

plt.tight_layout()
plt.show()"""))

# Vehicle and Driver Analysis
cells.append(nbf.v4.new_markdown_cell("## 6. Vehicle and Driver Analysis"))
cells.append(nbf.v4.new_code_cell("""# Create age groups
df['driver_age_group'] = pd.qcut(df['Driver Age'], q=5, labels=['Very Young', 'Young', 'Middle', 'Senior', 'Elderly'])
df['vehicle_age_group'] = pd.qcut(df['Vehicle Age'], q=4, labels=['New', 'Moderate', 'Old', 'Very Old'])

# Plot vehicle and driver patterns
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Settlement by driver age group
sns.boxplot(data=df, x='driver_age_group', y='SettlementValue', ax=axes[0,0])
axes[0,0].set_title('Settlement by Driver Age Group')
axes[0,0].tick_params(axis='x', rotation=45)

# Settlement by vehicle age group
sns.boxplot(data=df, x='vehicle_age_group', y='SettlementValue', ax=axes[0,1])
axes[0,1].set_title('Settlement by Vehicle Age')
axes[0,1].tick_params(axis='x', rotation=45)

# Driver age vs Vehicle age
sns.scatterplot(data=df, x='Driver Age', y='Vehicle Age', 
                hue='SettlementValue', size='Injury_Prognosis', sizes=(20, 200), ax=axes[1,0])
axes[1,0].set_title('Driver Age vs Vehicle Age')

# Average settlement by weather and vehicle type
sns.barplot(data=df, x='Weather Conditions', y='SettlementValue', hue='Vehicle Type', ax=axes[1,1])
axes[1,1].set_title('Settlement by Weather and Vehicle Type')
axes[1,1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()"""))

# Final Processing
cells.append(nbf.v4.new_markdown_cell("## 7. Final Processing and Conclusions"))
cells.append(nbf.v4.new_code_cell("""# Handle infinite values and very large numbers
df = df.replace([np.inf, -np.inf], np.nan)

# Fill NaN values for numeric columns only
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

# Scale numerical features
scaler = RobustScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

# Encode categorical variables (excluding datetime column)
categorical_columns = df.select_dtypes(include=['object']).columns
categorical_columns = [col for col in categorical_columns if col != 'Accident Date']
for col in categorical_columns:
    df[col] = df[col].astype('category').cat.codes

# Save preprocessed data
output_path = "Cleaned_Patient_Records_preprocessed.csv"
df.to_csv(output_path, index=False)
print(f"✅ Preprocessed data saved to {output_path}")

# Final summary statistics
print("\nFinal Dataset Summary:")
print(f"Total features: {df.shape[1]}")
print(f"Total samples: {df.shape[0]}")

# Final correlation heatmap
key_features = ['SettlementValue', 'total_special_damages', 'total_general_damages', 
                'Injury_Prognosis', 'Driver Age', 'Vehicle Age']
plt.figure(figsize=(10, 8))
sns.heatmap(df[key_features].corr(), annot=True, cmap='coolwarm', center=0)
plt.title('Final Correlation Heatmap of Key Features')
plt.tight_layout()
plt.show()"""))

# Add cells to notebook
nb['cells'] = cells

# Write the notebook
with open('MLModel/improved_preprocessing.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Enhanced notebook created successfully!") 