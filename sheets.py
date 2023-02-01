import gspread
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

gc = gspread.service_account(filename = 'pidibot-sheets.json')
doc_empl = gc.open_by_key(os.getenv('EMPL_DOC_KEY'))
doc_scores = gc.open_by_key(os.getenv('SCORES_DOC_KEY'))

doc_empl = gc.open_by_key(os.getenv('EMPL_DOC_KEY'))
sh_empl = doc_empl.get_worksheet(0)
ppl = pd.DataFrame(sh_empl.get_all_values())
ppl = ppl.rename(columns=ppl.iloc[0])
ppl = ppl.drop(ppl.index[0]).reset_index(drop=True)
rows = ppl.shape[0]
print(ppl)




print(ppl)