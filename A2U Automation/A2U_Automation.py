import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QAction, qApp
from PyQt5.QtWidgets import QDesktopWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QInputDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
import pandas as pd

class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """get Text"""
        self.btn = QPushButton('파일명 입력', self)
        self.btn.move(30, 30)
        self.btn.clicked.connect(self.showDialog)

        self.le = QLineEdit(self)
        self.le.move(120, 30)
        self.le.resize(150,30)
        
        """The button which quit the program"""
        btn = QPushButton('나가기', self)
        btn.move(200, 150)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(QCoreApplication.instance().quit)

        """exit Action"""
        exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        """settings of menuBar"""
        self.statusBar()
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAction)
        #filemenu.addAction(Add) 이런거 넣어야함

        
        """Basic settings of the program"""
        self.setWindowTitle('A2U 업무자동화 프로그램')
        self.setWindowIcon(QIcon('A2U.png'))
        self.resize(300, 200)
        self.center()
        self.show()

    def center(self):
        """set program to be centered"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showDialog(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', '품목,재고,입출고\n띄어쓰기없이 순서대로\n파일명 예시 (재고.csv면 "재고"만 치면됨):')
        if ok:
            self.le.setText(str(" 파일 생성 완료!"))
            file1, file2, file3 = text.split(",")
            pd.set_option('display.max_rows', 500)
            pd.set_option('display.max_columns', 500)
            pd.set_option('display.width', 1000)
            def load_excel(name):
                stock_df = pd.read_csv(name, dtype=str)
                return stock_df

            def get_size(df):
                pum = []
                size = []
                for name in df["품목명"]:
                    ind = name.rfind(" ")
                    pum.append(name[:ind])
                    size.append(name[ind:])
                df["품목명"] = pum
                df["사이즈"] = size
                return df

            def categorise(stock_df, name):
                leng = len(name)
                bools = []
                for unq in stock_df["품목코드"]:
                    if unq[:leng] == name:
                        bools.append(True)
                    else:
                        bools.append(False)
                return bools


            def make_sheet1(stock_df, cat_col):
                sheet = pd.DataFrame(columns=["품목명","사이즈", "전재고", "매입량", "매출량","현재고", "단가"])
                j = pd.DataFrame(("합계"," ",0,0,0,0," "))
                cat_col = cat_col.dropna()
                jjg = 0
                mir = 0
                mcr = 0
                hjg = 0
                for name in cat_col:
                    if len(name) == 2:
                        name = "0" + f"{name}"
                    name_df = stock_df[categorise(stock_df,name)]
                    sheet = sheet.append(name_df[["품목명","사이즈", "전재고", "매입량", "매출량","현재고", "단가"]],ignore_index=True)
                    sheet.loc[len(sheet)] = ["합계"," ",sum(pd.to_numeric(name_df["전재고"].str.replace(",",""))),sum(pd.to_numeric(name_df["매입량"].str.replace(",",""))),sum(pd.to_numeric(name_df["매출량"].str.replace(",",""))),sum(pd.to_numeric(name_df["현재고"].str.replace(",","")))," "]
                    try:
                        sheet.loc[len(sheet)] = ["합계액", " ", sheet.iloc[len(sheet)-1,2] * int(sheet.iloc[len(sheet)-2,6].replace(",","")),sheet.iloc[len(sheet)-1,3] * int(sheet.iloc[len(sheet)-2,6].replace(",","")),sheet.iloc[len(sheet)-1,4] * int(sheet.iloc[len(sheet)-2,6].replace(",","")),sheet.iloc[len(sheet)-1,5] * int(sheet.iloc[len(sheet)-2,6].replace(",","")), " "]
                    except:
                        pass
                    jjg += int(sheet.iloc[len(sheet)-1,2])
                    mir += int(sheet.iloc[len(sheet)-1,3])
                    mcr += int(sheet.iloc[len(sheet)-1,4])
                    hjg += int(sheet.iloc[len(sheet)-1,5])

                for i in range(len(sheet)):
                    try:
                        sheet.iloc[i,5] = str(int(sheet.iloc[i,2].replace(",","")) + int(sheet.iloc[i,3].replace(",","")) - int(sheet.iloc[i,4].replace(",","")))
                    except:
                        pass
                    try:
                        sheet.iloc[i,5] = sheet.iloc[i,2] + sheet.iloc[i,3] - sheet.iloc[i,4]
                    except:
                        pass
                sheet.loc[len(sheet)] = ["총합계액", " ", jjg, mir, mcr, hjg, f"재고증감액: {hjg - jjg}"]
                return sheet

            df1 = pd.read_csv(f"{file2}.csv", dtype=str)
            df2 = pd.read_csv(f"{file3}.csv", dtype=str)
            df3 = df1.merge(df2, how='left', on=["품목코드","품목명"]).fillna("0")
            df3 = get_size(df3)

            writer = pd.ExcelWriter('최종.xlsx', engine='xlsxwriter')
            for i in range(load_excel(f"{file1}.csv").shape[1]):
                af_trans = make_sheet1(df3,load_excel(f"{file1}.csv").iloc[:,i])
                af_trans = af_trans.fillna(0)
                af_trans.to_excel(writer, sheet_name = f"{load_excel(f'{file1}.csv').columns[i]}", index=False)
                workbook = writer.book
                worksheet = writer.sheets[f"{load_excel(f'{file1}.csv').columns[i]}"]
                merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 2})
                startCells = [1]
                for row in range(2,len(af_trans)+1):
                    if (af_trans.iloc[row-1,0] != af_trans.iloc[row-2,0]):
                        startCells.append(row)
                lastRow = len(af_trans)
                for row in startCells:
                    try:
                        endRow = startCells[startCells.index(row)+1]-1
                        if row == endRow:
                            worksheet.write(row, 0, af_trans.iloc[row-1,0], merge_format)
                        else:
                            worksheet.merge_range(row, 0, endRow, 0, str(af_trans.iloc[row-1,0]), merge_format)
                    except IndexError:
                        if row == lastRow:
                            worksheet.write(row, 0, af_trans.iloc[row-1,0], merge_format)
                        else:
                            worksheet.merge_range(row, 0, lastRow, 0, str(af_trans.iloc[row-1,0]), merge_format)

            writer.save()


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())