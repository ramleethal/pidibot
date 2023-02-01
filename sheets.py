import gspread
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

gc = gspread.service_account(filename = 'pidibot-sheets.json')
def GoogleSheet(key):
    doc_empl = gc.open_by_key(os.getenv(key))
    sh_empl = doc_empl.get_worksheet(0)
    df = pd.DataFrame(sh_empl.get_all_values())
    df = df.rename(columns=df.iloc[0])
    df = df.drop(df.index[0]).reset_index(drop=True)
    return df

ppl = GoogleSheet('EMPL_DOC_KEY')
scr = GoogleSheet('SCORES_DOC_KEY')

print(ppl)