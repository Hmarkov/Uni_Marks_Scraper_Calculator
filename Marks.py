from selenium import webdriver
from selenium.webdriver.common.by import By
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller

#Chrome initialization 
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.
options.add_argument('--log-level=3')
chromedriver_autoinstaller.install()
driver = webdriver.Chrome(service=Service(), options=options)

#Lists to avoid
abrv=["AM","AO","AS","E1","EC","N","F","IN","M","NS","P","PM/PO","R","View Statistics"]
markres=["Not marked yet",""]


class Manual_Marks:
     def __init__(self,mark,weight):
         self.mark=mark
         self.weight=weight

class Modules_Marks:
    def __init__(self,year, code, period,m_name,a_name,weight,mark):
        self.year = year
        self.code = code
        self.period = period
        self.m_name = m_name
        self.a_name = a_name
        self.weight = weight
        self.mark = mark

    def __repr__(self):
        return repr('|Year:' + self.year+
        '|Code:' +self.code+
        '|Period:'+self.period+
        '|ModuleName:'+self.m_name+
        '|AssessmentName:'+self.a_name+
        '|Weight:'+self.weight+
        '|Mark:'+self.mark+"|")
    
    def __eq__(self, other):
        return self.m_name==other.m_name
    def __hash__(self):
        return hash('ModuleName', self.m_name)

#region
# Login and Scrape
def login(user,pwd):
    driver.get('https://evision.uea.ac.uk/urd/sits.urd/run/siw_lgn')
    username = driver.find_element(By.ID,"MUA_CODE.DUMMY.MENSYS")
    password = driver.find_element(By.ID,"PASSWORD.DUMMY.MENSYS")
    username.send_keys(user)
    password.send_keys(pwd)
    driver.find_element(By.NAME,"BP101.DUMMY_B.MENSYS").click()
    driver.find_element(By.LINK_TEXT,"Provisional Marks This Year").click()
    tbody = driver.find_element(By.XPATH,'//*[@id="sitspagecontent"]/table[1]/tbody')
    scrape(tbody)

def scrape(body):
    listy=[]
    objs=[]
    for row in body.find_elements(By.XPATH,'tr'):
        for td in row.find_elements(By.XPATH,'td'):
            if td.text not in abrv:
                listy.append(td)
    listt = np.array_split(listy,((len(listy)/8)+2))
    for el in listt:
        objs.append(Modules_Marks(el[0].text,el[1].text,el[2].text,el[3].text,el[4].text,el[5].text,el[6].text))
    group(objs)
#endregion

###Sort and regroup 
def group(lst):
    final_list=[]
    sorted_list=[]
    seen =set()
    tmp=[]
    for obj in lst:
        if obj.m_name not in seen:
            seen.add(obj.m_name)
    for obj in lst:
        if obj.m_name in seen:
            sorted_list.append(obj)
    for i in range(len(list(seen))):
        for el in sorted_list:
            if el.m_name == list(seen)[i]:
                if float(eval(el.weight))!=0.0:
                    tmp.append(el)
            else:
                final_list.append(tmp)
                tmp=[]
    final_list = [element for element in final_list if element]
    show(final_list)

### Marks calculator on collected data 
def calc_marks(l):
    marks=[]
    weights=[]
    for el in l:
        if el.mark not in markres :
            marks.append(float(el.mark))
            weights.append(float(eval(el.weight)))
        else:
            marks.append(float(0))
            weights.append(float(eval(el.weight)))
    mark=0
    weight=0
    res=0
    for i in range(len(marks)):
        mark+=marks[i]*weights[i]
        weight+=weights[i]
        if weight!=0:
            res=mark/weight
    return str(res)

###Print Table
def show(listy):
    print("\n -------------------------Weighted Average Automatic Calculator-------------------------\n")
    for el in listy:
        if len(el)>1:
            for i in el:
                print(i)
            print("Modules Weighted grade: "+calc_marks(el))
            print("\n")
        else:
            print(el)
            print("Modules Weighted grade: "+calc_marks(el))
            print("\n")

#Manual calculator
def calculator(list):
    mark=0
    weight=0
    for i in range(len(list)):
        mark+=list[i].mark*(list[i].weight/100)
        weight+=(list[i].mark/100)    
    return mark
        
def manual_calc():
    print("\n -------------------------Manual Calculator-------------------------\n")
    list=[]
    print("Number of items to calcluate")
    num = int(input("Number of items to calcluate: "))
    for i in range(num):
        grade = float(input("Grade: "))
        weight = float(input("Weight: "))
        list.append(Manual_Marks(grade,weight))
    print(calculator(list))



__name__ = "__main__" 
login("username","password")
manual_calc()


