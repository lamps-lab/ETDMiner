import glob
import pandas as pd 
import math 

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def createDf_from_txt(rootpath,folder):
    df_6 = pd.DataFrame(columns=['Path','Label_page_6'])
    df_26 = pd.DataFrame(columns=['Path','Label_page_26'])
    df_46 = pd.DataFrame(columns=['Path','Label_page_46'])
    file6=[]
    file26=[]
    file46=[]

    #For page no 6
    with open(rootpath+"00"+str(folder)+"_ocr_page6.txt") as f:
        contents = f.readlines()
        for i in range(0,len(contents)):
            filename=(contents[i].strip()) 
            file6.append(filename)

    for path_label in file6:
        path=path_label.split(',')[0]
        label=path_label.split(',')[1]
        df_6=df_6.append({'Path':path,'Label_page_6':label}, ignore_index=True)

    # For page number 26

    with open(rootpath+"00"+str(folder)+"_ocr_page26.txt") as f:
        contents = f.readlines()
        for i in range(0,len(contents)):
            filename=(contents[i].strip()) 
            file26.append(filename)

    for path_label in file26:
        path=path_label.split(',')[0]
        label=path_label.split(',')[1]
        df_26=df_26.append({'Path':path,'Label_page_26':label}, ignore_index=True)

    # For page number 46
    with open(rootpath+"00"+str(folder)+"_ocr_page50.txt") as f:
        contents = f.readlines()
        for i in range(0,len(contents)):
            filename=(contents[i].strip()) 
            file46.append(filename)

    for path_label in file46:
        path=path_label.split(',')[0]
        label=path_label.split(',')[1]
        df_46=df_46.append({'Path':path,'Label_page_46':label}, ignore_index=True)

    merged_df = df_26.merge(df_46, how = 'outer', on = ['Path'])
    final_merged = merged_df.merge(df_6, how='outer', on=['Path'])
    return final_merged

def calculate_agreement(final_merged, folder):
    final_merged['Final_label'] = ""
    for ind in final_merged.index:
        i=0
        label6 = final_merged['Label_page_6'][ind]
        label26=final_merged['Label_page_26'][ind]
        label46= (final_merged['Label_page_46'][ind])
        if type(label26) is str and type(label46) is str:
            if label6==label26==label46:
                final_merged['Final_label'][ind]=label6
            elif label6==label26:
                final_merged['Final_label'][ind]=label6
            elif label6==label46:
                final_merged['Final_label'][ind]=label6
            elif label26==label46:
                final_merged['Final_label'][ind]=label26
            else:
                final_merged['Final_label'][ind]="Complete Disagreement"
    #         print("yes")
        else: 
            final_merged['Final_label'][ind]=label6
        final_merged.to_csv("Folder"+str(folder)+'.csv')
       
def main():
    path = "results/"
    Folder_num = 0
    df = createDf_from_txt(path, Folder_num)
    calculate_agreement(df,Folder_num)
    print("done")

if __name__ == "__main__":
    main()
