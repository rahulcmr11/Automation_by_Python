import os
from openpyxl import load_workbook
from xlrd import open_workbook

path = input("Enter path of all the excel sheets: ")
string = input("Enter word ").lower()
print(string)
print('Searching...\n')
workbooks = os.listdir(path)
workbooks = [_ for _ in workbooks if not _.startswith('~')]


for workbook in workbooks:
    print("Searching -- ",workbook)
    wb2 = load_workbook(os.path.join(path, workbook))
    wb_name = os.path.join(path, workbook)
    ##another
    
    book = open_workbook(os.path.join(path, workbook))

    
    for sheet in book.sheets():
        for rowidx in range(sheet.nrows):
            row = sheet.row(rowidx)
 
            for colidx, cell in enumerate(row):

                if string in str(cell.value).lower():#.find(string) != -1:
                    print("wb_name_excel---> "+ workbook +" , sheetname  --> "+sheet.name+"\n")
                    print("searching for--> \n",string )
                    print("column_ids--> ",colidx)
                    print("\n row_ids--> ",rowidx)
                else :
                    #print("Not found")
                    continue


