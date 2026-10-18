import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('Data chest/Mosbirzhia_currency_daily2.csv')

plt.figure(figsize=(8, 12))
df.hist()
plt.tight_layout()
plt.savefig('graphics/1_Histogram', dpi=150, bbox_inches='tight')
plt.close()

plt.figure(figsize=(12, 8))
sns.lineplot(data=df, x='CLOSE', y='HIGH', legend=False, color='red')
sns.lineplot(data=df, x='CLOSE', y='LOW', legend=False, color='green')
plt.title('High prices and low closing prices')
plt.xlabel('Closure')
plt.ylabel('High')
plt.savefig('graphics/2_Closure to the high', dpi=150, bbox_inches='tight')
plt.close()

plt.figure(figsize=(12, 8))
sns.lineplot(data=df, x='OPEN', y='HIGH', legend=False, color='red')
sns.lineplot(data=df, x='OPEN', y='LOW', legend=False, color='green')
plt.xlabel('Discovery')
plt.ylabel('Closure')
plt.savefig('graphics/3_Opening with high and low prices')
plt.close()

plt.figure(figsize=(12, 8))
sns.scatterplot(data=df, x='CLOSE', y='HIGH', legend=False, color='red')
sns.scatterplot(data=df, x='CLOSE', y='LOW', legend=False, color='green')
plt.title('High prices and low closing prices')
plt.xlabel('Closure')
plt.ylabel('High')
plt.savefig('graphics/4_Closure to the high', dpi=150, bbox_inches='tight')
plt.close()
